"""Monta um Clip Dictionary do Sollumz a partir de Actions e exporta .ycd.xml (GTA V / FiveM).

Pré-requisitos: Sollumz 2.9 habilitado; armature do ped (ex.: mp_m_freemode_01) na cena; Actions já bakeadas a 30 fps.
Uso headless (NÃO use --factory-startup: o Sollumz precisa carregar):
    blender -b cena.blend --python gta_ycd_export.py -- --armature mp_m_freemode_01 --dict meu_dict \
        --clip meu_clip=MinhaAction [--clip outro=OutraAction] --out C:/tmp/anim
Via MCP: import gta_ycd_export; gta_ycd_export.run("mp_m_freemode_01", "meu_dict", [("meu_clip", "MinhaAction")], r"C:/tmp/anim")
Depois converta para binário: powershell.exe -File ycdconv.ps1 xml2ycd <xml> <ycd>
Imprime "@@YCD@@{json}". Não salva o .blend.
"""
import importlib
import json
import os
import sys

import addon_utils
import bpy

FPS = 30


def _sollumz_pkg():
    mods = [m.__name__ for m in addon_utils.modules() if m.__name__.lower().endswith("sollumz") or "sollumz_dev" in m.__name__
            or m.__name__.lower().endswith(".sollumz")]
    if not mods:
        raise RuntimeError("Sollumz não encontrado nas extensões")
    pkg = mods[0]
    addon_utils.enable(pkg, default_set=False)
    return pkg


def action_fcurves(act):
    """F-curves de uma Action em camadas (5.x) ou legada."""
    if bpy.app.version >= (5, 0, 0):
        return [fc for layer in act.layers for strip in layer.strips for cb in strip.channelbags for fc in cb.fcurves]
    return list(act.fcurves)


def check_action(act, armature):
    """Problemas que quebram ou degradam o clip no jogo."""
    issues = []
    fcs = action_fcurves(act)
    if not fcs:
        issues.append(f"{act.name}: sem F-curves")
    euler = [fc.data_path for fc in fcs if fc.data_path.endswith("rotation_euler")]
    if euler:
        issues.append(f"{act.name}: {len(euler)} canais rotation_euler (GTA usa quaternion)")
    bones = set(armature.data.bones.keys())
    missing = {fc.data_path.split('"')[1] for fc in fcs if fc.data_path.startswith("pose.bones[")} - bones
    if missing:
        issues.append(f"{act.name}: ossos inexistentes no armature: {sorted(missing)[:5]}")
    if bpy.context.scene.render.fps != FPS:
        issues.append(f"cena a {bpy.context.scene.render.fps} fps (GTA = {FPS})")
    return issues


def run(armature_name, dict_name, clips, out_dir):
    pkg = _sollumz_pkg()
    yi = importlib.import_module(pkg + ".ycd.ycdimport")
    ye = importlib.import_module(pkg + ".ycd.ycdexport")
    SollumType = importlib.import_module(pkg + ".sollumz_properties").SollumType
    arm = bpy.data.objects[armature_name]

    issues = []
    resolved = []
    for clip_name, action_name in clips:
        act = bpy.data.actions[action_name]
        issues += check_action(act, arm)
        resolved.append((clip_name, act))

    old = bpy.data.objects.get(dict_name)  # idempotente: recria o dicionário
    if old:
        for c in list(old.children_recursive) + [old]:
            bpy.data.objects.remove(c, do_unlink=True)
    cd, clips_obj, anims_obj = yi.create_clip_dictionary_template(dict_name)
    report = []
    for clip_name, act in resolved:
        an = yi.create_anim_obj(SollumType.ANIMATION)
        an.name, an.parent = clip_name + "_anim", anims_obj
        ap = an.animation_properties
        ap.hash = clip_name + "_anim"
        ap.target_id_type, ap.target_id = "ARMATURE", arm.data  # alvo antes da action: evita erro de bone-map no update
        ap.action = act
        cl = yi.create_anim_obj(SollumType.CLIP)
        cl.name, cl.parent = clip_name, clips_obj
        cp = cl.clip_properties
        cp.hash, cp.name = clip_name, clip_name + ".clip"
        f0, f1 = act.frame_range
        cp.duration = (f1 - f0) / FPS
        ca = cp.animations.add()
        ca.animation, ca.start_frame, ca.end_frame = an, f0, f1
        report.append({"clip": clip_name, "action": act.name, "frames": [f0, f1], "duration_s": round(cp.duration, 3)})

    os.makedirs(out_dir, exist_ok=True)
    xml = os.path.join(out_dir, dict_name + ".ycd.xml")
    if not ye.export_ycd(cd, xml):
        raise RuntimeError("export_ycd falhou (veja o Info Log do Sollumz)")
    return {"xml": xml, "bytes": os.path.getsize(xml), "clips": report, "issues": issues}


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    get = lambda n: a[a.index(n) + 1]
    clips = [tuple(a[i + 1].split("=", 1)) for i, v in enumerate(a) if v == "--clip"]
    print("@@YCD@@" + json.dumps(run(get("--armature"), get("--dict"), clips, get("--out")), ensure_ascii=False))
