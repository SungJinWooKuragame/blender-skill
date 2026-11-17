"""Auditoria técnica de cena/asset no Blender (5.x). Só lê, nunca altera a cena.

Uso headless:
    blender -b arquivo.blend --python qa_report.py -- --objects Cadeira Mesa
    blender -b arquivo.blend --python qa_report.py            (todos os meshes)
Uso via MCP/console:
    import sys; sys.path.insert(0, r"<skill>/scripts"); import qa_report; print(qa_report.run(["Cadeira"]))

Saída: uma linha "@@QA@@{json}" com números por objeto + lista de problemas.
"""
import json
import sys

import bmesh
import bpy

DATA_SOCKETS = {"Roughness", "Metallic", "Normal", "Alpha", "Specular IOR Level",
                "Coat Weight", "Transmission Weight", "Height", "Displacement"}


def _image_nodes_feeding(node_tree):
    """(image_node, nome_do_socket_destino) para texturas ligadas direto ou via Normal Map/Separate."""
    out = []
    for link in node_tree.links:
        src, dst = link.from_node, link.to_node
        if src.type != "TEX_IMAGE" or not src.image:
            continue
        target = link.to_socket.name
        if dst.type in {"NORMAL_MAP", "BUMP", "DISPLACEMENT"}:
            target = "Normal"
        elif dst.type in {"SEPRGB", "SEPARATE_COLOR"}:
            target = "Roughness"  # canal empacotado (ORM etc.) = dado
        out.append((src, target))
    return out


def mesh_report(ob, depsgraph):
    issues = []
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        bm = bmesh.new()
        bm.from_mesh(me)
        tris = sum(len(f.verts) - 2 for f in bm.faces)
        ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
        non_manifold = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
        boundary = sum(1 for e in bm.edges if e.is_boundary)
        loose_verts = sum(1 for v in bm.verts if not v.link_edges)
        zero_faces = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
        bm.free()
        uv_count = len(me.uv_layers)
        dims = [round(d, 4) for d in ob.dimensions]
        rep = {
            "tris": tris, "verts": len(me.vertices), "ngons": ngons,
            "non_manifold_edges": non_manifold, "boundary_edges": boundary,
            "loose_verts": loose_verts, "zero_area_faces": zero_faces,
            "uv_maps": uv_count, "materials": [m.name if m else None for m in ob.data.materials],
            "dimensions_m": dims, "scale": [round(s, 4) for s in ob.scale],
            "rotation_euler_deg": [round(r * 57.2958, 2) for r in ob.rotation_euler],
            "modifiers": [f"{m.type}:{m.name}" for m in ob.modifiers],
        }
    finally:
        ev.to_mesh_clear()

    if any(abs(s - 1.0) > 1e-4 for s in ob.scale):
        issues.append("escala não aplicada (Ctrl+A > Scale antes de bevel/export)")
    if (ob.scale.x * ob.scale.y * ob.scale.z) < 0:
        issues.append("escala negativa: normais invertidas no export")
    if rep["uv_maps"] == 0:
        issues.append("sem UV map")
    if rep["loose_verts"]:
        issues.append(f"{rep['loose_verts']} vértices soltos")
    if rep["zero_area_faces"]:
        issues.append(f"{rep['zero_area_faces']} faces de área zero")
    if rep["non_manifold_edges"]:
        issues.append(f"{rep['non_manifold_edges']} arestas non-manifold (3+ faces numa aresta)")
    if None in rep["materials"] or not rep["materials"]:
        issues.append("slot de material vazio ou sem material")
    if max(dims) > 500 or (max(dims) < 0.001 and max(dims) > 0):
        issues.append(f"dimensão suspeita {dims} m: conferir unidade/escala")
    return rep, issues


def material_report(mat):
    issues = []
    if not mat or not mat.node_tree:
        return issues
    for img_node, target in _image_nodes_feeding(mat.node_tree):
        img = img_node.image
        cs = img.colorspace_settings.name
        if target in DATA_SOCKETS and cs not in {"Non-Color", "Linear Rec.709", "Raw"}:
            issues.append(f"{mat.name}: '{img.name}' alimenta {target} mas está em {cs} (use Non-Color)")
        if target in {"Base Color", "Emission Color"} and cs == "Non-Color":
            issues.append(f"{mat.name}: '{img.name}' é cor mas está Non-Color")
        if img.source == "FILE" and not img.packed_file:
            try:
                path = bpy.path.abspath(img.filepath)
                import os
                if not os.path.exists(path):
                    issues.append(f"{mat.name}: textura ausente no disco: {img.filepath}")
            except Exception:
                pass
        w, h = img.size
        if w and h and (w & (w - 1) or h & (h - 1)):
            issues.append(f"{mat.name}: '{img.name}' {w}x{h} não é potência de 2 (game engines)")
    return issues


def run(objects=None):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    if objects:
        obs = [bpy.data.objects[n] for n in objects if n in bpy.data.objects]
    else:
        obs = [o for o in bpy.data.objects if o.type == "MESH"]
    result = {"blender": bpy.app.version_string,
              "unit_system": bpy.context.scene.unit_settings.system,
              "unit_scale": bpy.context.scene.unit_settings.scale_length,
              "fps": bpy.context.scene.render.fps,
              "objects": {}, "issues": [], "total_tris": 0}
    seen_mats = set()
    for ob in obs:
        if ob.type != "MESH":
            continue
        rep, iss = mesh_report(ob, depsgraph)
        result["objects"][ob.name] = rep
        result["total_tris"] += rep["tris"]
        result["issues"] += [f"{ob.name}: {i}" for i in iss]
        for slot in ob.material_slots:
            if slot.material and slot.material.name not in seen_mats:
                seen_mats.add(slot.material.name)
                result["issues"] += material_report(slot.material)
    if abs(result["unit_scale"] - 1.0) > 1e-6:
        result["issues"].append(f"unit scale = {result['unit_scale']} (engines esperam 1.0 com metros)")
    return result


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    names = argv[argv.index("--objects") + 1:] if "--objects" in argv else None
    print("@@QA@@" + json.dumps(run(names), ensure_ascii=False))
