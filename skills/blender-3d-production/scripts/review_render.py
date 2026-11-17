"""Renderiza uma folha de revisão (4 ângulos) de objetos, sem alterar o .blend salvo.

Uso:
    blender -b arquivo.blend --python review_render.py -- --objects Logo --out C:/tmp/review.png
    blender -b arquivo.blend --python review_render.py -- --out C:/tmp/review.png --shading clay
Opções: --objects N1 N2 (padrão: todos os meshes visíveis) · --res 512 · --shading material|clay
Imprime "@@REVIEW@@{json}" com o caminho de cada imagem. Leia as imagens depois (Read) e critique.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector


def _bounds(obs):
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2, (hi - lo).length


def run(objects=None, out="//review.png", res=512, shading="material"):
    scene = bpy.context.scene
    obs = [bpy.data.objects[n] for n in objects] if objects else \
        [o for o in scene.objects if o.type == "MESH" and o.visible_get()]
    if not obs:
        return {"error": "nenhum mesh"}
    center, size = _bounds(obs)

    # guarda tudo que vamos mexer para restaurar no finally (cena ao vivo do usuário via MCP)
    r, vs = scene.render, scene.view_settings
    saved = {"engine": r.engine, "rx": r.resolution_x, "ry": r.resolution_y, "pct": r.resolution_percentage,
             "transp": r.film_transparent, "path": r.filepath, "vt": vs.view_transform, "look": vs.look}
    r.resolution_percentage = 100
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = res
    scene.render.film_transparent = False
    try:
        scene.view_settings.view_transform = "AgX"
    except TypeError:
        pass

    tmp = []
    cam_data = bpy.data.cameras.new("_review_cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("_review_cam", cam_data)
    scene.collection.objects.link(cam)
    tmp.append(cam)
    key = bpy.data.objects.new("_review_key", bpy.data.lights.new("_review_key", "AREA"))
    key.data.energy = 300 * max(size, 0.1) ** 2
    key.data.size = size
    scene.collection.objects.link(key)
    tmp.append(key)
    clay = None
    old_mats = {}
    if shading == "clay":
        clay = bpy.data.materials.new("_review_clay")
        bsdf = next(n for n in clay.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1)
        bsdf.inputs["Roughness"].default_value = 0.5
        for o in obs:
            old_mats[o.name] = [s.material for s in o.material_slots]
            if not o.material_slots:
                o.data.materials.append(clay)  # slot temporário, removido no finally
            for s in o.material_slots:
                s.material = clay

    old_world = scene.world
    tmp_world = None
    if old_world is None:  # sem world = fundo preto e sem luz ambiente, esconde a forma
        tmp_world = bpy.data.worlds.new("_review_world")
        tmp_world.color = (0.18, 0.18, 0.18)
        scene.world = tmp_world

    old_cam = scene.camera
    scene.camera = cam
    dist = size * 1.4 + 0.01
    base, ext = os.path.splitext(bpy.path.abspath(out))
    files = []
    try:
        for i, (az, el) in enumerate([(35, 20), (125, 20), (215, 20), (35, 65)]):
            a, e = math.radians(az), math.radians(el)
            cam.location = center + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * dist
            cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
            key.location = center + Vector((math.cos(a + 0.8), math.sin(a + 0.8), 1.2)) * dist
            key.rotation_euler = (center - key.location).to_track_quat("-Z", "Y").to_euler()
            path = f"{base}_{i}{ext or '.png'}"
            scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            files.append(path)
    finally:
        scene.camera = old_cam
        r.engine = saved["engine"]
        r.resolution_x, r.resolution_y, r.resolution_percentage = saved["rx"], saved["ry"], saved["pct"]
        r.film_transparent, r.filepath = saved["transp"], saved["path"]
        try:
            vs.view_transform, vs.look = saved["vt"], saved["look"]
        except TypeError:
            pass
        if tmp_world:
            scene.world = old_world
            bpy.data.worlds.remove(tmp_world)
        for o in obs:
            if o.name in old_mats:
                if not old_mats[o.name]:
                    o.data.materials.clear()  # remove o slot temporário
                else:
                    for s, m in zip(o.material_slots, old_mats[o.name]):
                        s.material = m
        for o in tmp:
            data = o.data
            bpy.data.objects.remove(o)
            if isinstance(data, bpy.types.Camera):
                bpy.data.cameras.remove(data)
            else:
                bpy.data.lights.remove(data)
        if clay:
            bpy.data.materials.remove(clay)
    return {"files": files, "center": list(center), "size_m": round(size, 4)}


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    def opt(name, default=None, many=False):
        if name not in argv:
            return default
        i = argv.index(name) + 1
        if many:
            vals = []
            while i < len(argv) and not argv[i].startswith("--"):
                vals.append(argv[i])
                i += 1
            return vals
        return argv[i]

    print("@@REVIEW@@" + json.dumps(run(opt("--objects", many=True), opt("--out", "//review.png"),
                                        int(opt("--res", 512)), opt("--shading", "material"))))
