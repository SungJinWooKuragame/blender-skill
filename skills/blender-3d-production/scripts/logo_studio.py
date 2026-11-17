"""Estúdio de logo/produto premium (ponto de partida testado no Blender 5.3; itere a partir dele).

Uso:
    blender -b --factory-startup --python logo_studio.py -- --text S --out C:/tmp/logo.png
    blender -b cena.blend --python logo_studio.py -- --object MeuLogo --out C:/tmp/logo.png --color 0.8 0.1 0.1
Opções: --text T | --object NOME (mesh/curve já na cena) · --color R G B (linear) · --metal 0|1 · --rough 0.22
        --res 1280 720 · --samples 128 · --save C:/tmp/logo.blend
Monta: bevel 5 seg + weighted normal, material herói, cyclorama fosco (spec 0), softbox frontal + 2 strips laterais + rim,
câmera 100 mm com DOF, Cycles + AgX Medium High Contrast. Imprime "@@LOGO@@{json}".
"""
import json
import math
import sys

import bpy
from mathutils import Matrix, Vector


def _look_at(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()


def _area(scene, name, loc, size, size_y, energy, target=(0, 0, 0)):
    light = bpy.data.lights.get(name) or bpy.data.lights.new(name, "AREA")
    light.shape, light.size, light.size_y, light.energy = "RECTANGLE", size, size_y, energy
    light.spread = math.radians(35)  # controla vazamento no fundo
    ob = bpy.data.objects.new(name, light)  # sempre novo e só na cena do estúdio
    scene.collection.objects.link(ob)
    ob.location = loc
    _look_at(ob, target)
    return ob


def _mat(name, color, metal, rough, spec=0.5, aniso=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["Anisotropic"].default_value = aniso
    return m


def run(text="S", object_name=None, color=(0.08, 0.12, 0.35), metal=1.0, rough=0.22,
        res=(1280, 720), samples=128, out="//logo.png", save=None):
    # Tudo acontece numa cena separada "LogoStudio" com uma CÓPIA do objeto: a cena do usuário não é tocada.
    sc = bpy.data.scenes.get("LogoStudio") or bpy.data.scenes.new("LogoStudio")
    for o in list(sc.collection.objects):  # limpa execução anterior (idempotente)
        bpy.data.objects.remove(o)
    vl = sc.view_layers[0]
    if object_name:
        src = bpy.data.objects[object_name]
        user_dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(src.evaluated_get(user_dg))  # mesh/curva/texto com modificadores
        logo = bpy.data.objects.new(src.name + "_studio", me)
        sc.collection.objects.link(logo)
        logo.matrix_world = src.matrix_world.copy()
    else:
        cu = bpy.data.curves.new("LogoText", "FONT")
        cu.body, cu.size, cu.extrude = text, 0.2, 0.02
        cu.align_x = cu.align_y = "CENTER"
        tmp = bpy.data.objects.new("LogoText", cu)
        sc.collection.objects.link(tmp)
        tmp.rotation_euler = (math.radians(90), 0, 0)
        vl.update()
        me = bpy.data.meshes.new_from_object(tmp.evaluated_get(vl.depsgraph))
        logo = bpy.data.objects.new("SM_Logo", me)
        sc.collection.objects.link(logo)
        logo.matrix_world = tmp.matrix_world.copy()
        bpy.data.objects.remove(tmp)
        bpy.data.curves.remove(cu)

    # aplicar rotação/escala só na cópia, via dados (sem operador, sem depender da cena ativa)
    loc = logo.matrix_world.to_translation()
    logo.data.transform(logo.matrix_world.to_3x3().to_4x4())
    logo.matrix_world = Matrix.Translation(loc)
    logo.data.shade_smooth()
    logo.data.set_sharp_from_angle(angle=math.radians(30))
    vl.update()
    size = max(logo.dimensions)
    bev = logo.modifiers.get("Bevel") or logo.modifiers.new("Bevel", "BEVEL")
    bev.width, bev.segments, bev.limit_method = size * 0.03, 5, "ANGLE"
    bev.use_clamp_overlap, bev.harden_normals = True, True
    wn = logo.modifiers.get("WeightedNormal") or logo.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
    wn.keep_sharp = True
    logo.data.materials.clear()
    logo.data.materials.append(_mat("M_Hero", color, metal, rough, aniso=0.6 if metal > 0.5 else 0.0))

    vl.update()
    pts = [logo.matrix_world @ Vector(c) for c in logo.bound_box]
    floor_z = min(p.z for p in pts)
    cx = sum(p.x for p in pts) / 8
    cy = sum(p.y for p in pts) / 8
    cz = sum(p.z for p in pts) / 8
    s = size / 0.2  # escala do estúdio relativa ao logo de 0.2 m usado no teste

    back = _mat("M_Cyclo", (0.02, 0.02, 0.025), 0.0, 1.0, spec=0.0)  # fosco e spec 0: sem Fresnel branco no rasante
    for name, loc, rot in (("Cyclo_Floor", (cx, cy + 0.4 * s, floor_z), (0, 0, 0)),
                           ("Cyclo_Wall", (cx, cy + 1.0 * s, floor_z + 1.6 * s), (math.radians(90), 0, 0))):
        me = bpy.data.meshes.get(name)
        if not me:
            me = bpy.data.meshes.new(name)
            me.from_pydata([(-2, -2, 0), (2, -2, 0), (2, 2, 0), (-2, 2, 0)], [], [(0, 1, 2, 3)])
            me.materials.append(back)
        ob = bpy.data.objects.new(name, me)
        sc.collection.objects.link(ob)
        ob.location, ob.rotation_euler, ob.scale = loc, rot, (s, s, s)

    tgt = (cx, cy, cz)
    _area(sc, "L_Front", (cx + 0.25 * s, cy - 1.4 * s, cz + 0.9 * s), 0.6 * s, 0.15 * s, 15 * s * s, tgt)
    _area(sc, "L_StripL", (cx - 0.45 * s, cy - 0.2 * s, cz + 0.1 * s), 0.9 * s, 0.08 * s, 12 * s * s, tgt)
    _area(sc, "L_StripR", (cx + 0.45 * s, cy - 0.2 * s, cz + 0.1 * s), 0.9 * s, 0.08 * s, 12 * s * s, tgt)
    _area(sc, "L_Rim", (cx, cy + 0.45 * s, cz + 0.35 * s), 0.6 * s, 0.15 * s, 20 * s * s, tgt)
    world = bpy.data.worlds.get("LogoStudio_World") or bpy.data.worlds.new("LogoStudio_World")  # World próprio, sem nós
    world.color = (0.005, 0.005, 0.006)
    sc.world = world

    cd = bpy.data.cameras.get("CAM_Hero") or bpy.data.cameras.new("CAM_Hero")
    cd.lens, cd.dof.use_dof, cd.dof.aperture_fstop = 100, True, 4.0
    cam = bpy.data.objects.new("CAM_Hero", cd)
    sc.collection.objects.link(cam)
    cam.location = (cx + 0.35 * s, cy - 1.25 * s, cz + 0.05 * s)
    _look_at(cam, tgt)
    cd.dof.focus_distance = (cam.location - Vector(tgt)).length
    sc.camera = cam

    sc.render.engine = "CYCLES"
    sc.cycles.samples, sc.cycles.use_denoising = samples, True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True, scene=sc.name)
    if save:
        bpy.ops.wm.save_as_mainfile(filepath=save, copy=True)
    return {"out": bpy.path.abspath(out), "scene": sc.name, "logo": logo.name, "size_m": round(size, 4)}


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    def opt(n, k=1, d=None, cast=str):
        if n not in a:
            return d
        i = a.index(n)
        vals = [cast(v) for v in a[i + 1:i + 1 + k]]
        return vals[0] if k == 1 else tuple(vals)

    print("@@LOGO@@" + json.dumps(run(
        text=opt("--text", d="S"), object_name=opt("--object"),
        color=opt("--color", 3, (0.08, 0.12, 0.35), float), metal=opt("--metal", d=1.0, cast=float),
        rough=opt("--rough", d=0.22, cast=float), res=opt("--res", 2, (1280, 720), int),
        samples=opt("--samples", d=128, cast=int), out=opt("--out", d="//logo.png"), save=opt("--save"))))
