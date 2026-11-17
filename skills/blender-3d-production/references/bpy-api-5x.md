# bpy no Blender 5.x

Fatos marcados ✔ foram conferidos por introspecção no Blender 5.3.0.

## Executar

- **MCP ao vivo** (blender-mcp `execute_blender_code`): passos pequenos, imprima só o necessário. Cada chamada
  tem namespace novo: re-importe módulos (ficam em cache no `sys.modules`; `importlib.reload` só após editar).
- **Headless**: `blender -b in.blend --python script.py -- --arg x`. Argumentos depois de `--` em `sys.argv`.
  `--factory-startup` ignora add-ons do usuário (Sollumz não carrega); tire-o quando precisar deles.
- Imprima resultado com marcador (`print("@@JSON@@" + json.dumps(r))`) e filtre com grep: economiza tokens.
- Windows + Git Bash: `//arquivo` vira `/arquivo`. Use caminhos absolutos ou `MSYS_NO_PATHCONV=1`.

## Mudanças que quebram tutorial antigo e memória de LLM

| Antigo | 5.x |
|---|---|
| `mesh.use_auto_smooth` | removido ✔. Use `bpy.ops.object.shade_smooth_by_angle(angle=, keep_sharp_edges=)` ✔, `object.shade_auto_smooth` (adiciona modificador) ✔ ou `mesh.set_sharp_from_angle(angle=)` ✔ |
| `ShaderNodeTexMusgrave` | removido ✔. Noise Texture com `noise_type` ✔ (fBM, multifractal, ridged...) |
| `wm.collada_export` (.dae) | removido ✔. Use glTF/FBX/USD |
| `scene.node_tree` (compositor) | `scene.compositing_node_group` ✔ |
| `BLENDER_EEVEE_NEXT` | `BLENDER_EEVEE` ✔ |
| bone layers | `armature.collections` / `collections_all` ✔ |
| `action.fcurves` direto | Actions em camadas/slots ✔ (`action.slots`, `action.layers`, `is_action_layered`) |
| Principled antigo (`Specular`, `Emission`, `Subsurface`, `Clearcoat`) | `Specular IOR Level`, `Emission Color` + `Emission Strength`, `Subsurface Weight`, `Coat Weight`, `Sheen Weight`, `Transmission Weight` ✔ |
| `bgl` | removido; use `gpu` (em background: `gpu.init()` antes) |

Principled BSDF 5.3 ✔: Base Color, Metallic, Roughness, IOR, Alpha, Normal, Diffuse Roughness, Subsurface Weight/Radius/Scale,
Specular IOR Level, Specular Tint, Anisotropic, Transmission Weight, Coat Weight/Roughness/IOR/Tint/Normal,
Sheen Weight/Roughness/Tint, Emission Color/Strength, Thin Film Thickness/IOR, Thin Wall.

View transforms 5.3 ✔: Standard, AgX (padrão), Filmic, Khronos PBR Neutral, ACES 1.3, ACES 2.0, Filmic Log, False Color, Raw.

## Padrões

```python
# operador com contexto explícito (background não tem 3D View)
with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob],
                               selected_editable_objects=[ob]):
    assert bpy.ops.object.transform_apply(location=False, rotation=True, scale=True) == {'FINISHED'}

# idempotente: reaproveita em vez de duplicar
mat = bpy.data.materials.get("M_Metal") or bpy.data.materials.new("M_Metal")
mod = ob.modifiers.get("Bevel") or ob.modifiers.new("Bevel", "BEVEL")

# leitura em massa (100x mais rápido que loop em vértices)
import numpy as np
co = np.empty(len(me.vertices) * 3, dtype=np.float32)
me.vertices.foreach_get("co", co)

# malha avaliada (com modificadores); sempre libere
ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
m = ev.to_mesh(); ...; ev.to_mesh_clear()
```

- Nó por `type` (`n.type == "BSDF_PRINCIPLED"`), nunca por `name` (nome é traduzido na UI em PT).
- Enum válido: `[i.identifier for i in T.bl_rna.properties["prop"].enum_items]`. Enums dinâmicos
  (`render.engine`, `view_transform`) listam menos em background: atribua dentro de `try/except TypeError`
  e leia os valores válidos na mensagem.
- Edit Mode: `ob.data` não atualiza; use `bmesh.from_edit_mesh` + `bmesh.update_edit_mesh` ou volte ao Object Mode.
- Remover/aplicar modificador ou objeto invalida a referência Python: guarde nomes, não objetos.
- Não confie em nome padrão (`Cube.001`); renomeie explicitamente e busque por `bpy.data.objects[nome]`.
- `view_layer.update()` antes de ler `matrix_world` depois de mudar transformações.
- Caminhos: `bpy.path.abspath("//tex/a.png")` relativo ao .blend.

## Exportadores (props confirmadas no 5.3 ✔)

- FBX `export_scene.fbx`: `apply_scale_options`, `apply_unit_scale`, `axis_forward`, `axis_up`, `use_triangles`,
  `add_leaf_bones`, `primary_bone_axis`, `secondary_bone_axis`, `use_armature_deform_only`, `bake_anim`,
  `bake_anim_use_all_actions`, `bake_anim_use_nla_strips`, `bake_anim_simplify_factor`, `mesh_smooth_type`,
  `use_tspace`, `object_types`, `use_selection`, `path_mode`, `embed_textures`.
- glTF `export_scene.gltf`: `export_format` (GLB/GLTF_SEPARATE), `export_yup`, `export_apply`, `export_animations`,
  `export_animation_mode`, `export_nla_strips`, `export_draco_mesh_compression_enable`, `export_tangents`,
  `export_def_bones`, `export_morph`, `export_image_format`, `export_meshopt_compression_enable`.
- OBJ `wm.obj_export`, STL `wm.stl_export`, PLY `wm.ply_export`, USD `wm.usd_export` (`meters_per_unit`,
  `convert_orientation`, `export_textures_mode`, `generate_materialx_network`), Alembic `wm.alembic_export`.
- Antes de usar uma prop não listada aqui:
  `[p.identifier for p in bpy.ops.export_scene.fbx.get_rna_type().properties]`.

## Ferramentas deste skill

`scripts/qa_report.py` (auditoria só-leitura), `scripts/review_render.py` (4 ângulos EEVEE, restaura a cena),
`scripts/logo_studio.py` (estúdio em cena separada), `scripts/gta_ycd_export.py` (Clip Dictionary → .ycd.xml).
Todos expõem `run(...)` para MCP e CLI após `--`. `scripts/ycdconv.ps1` converte XML ⇄ YCD (PowerShell 5.1).
