# Engines: Unreal, Unity, Godot, Minecraft

Regra geral: metros no Blender (unit scale 1.0), transformações aplicadas, origem no pivô desejado, triângulos ou
quads (engine triangula; triangule você se o bake dependeu disso), um material por "tipo de superfície".
Depois de exportar: **reimporte** no Blender ou abra no engine e confira escala, rotação, normais, materiais.
Teste ✔ (Blender 5.3): caixa 1,8×0,6×0,4 m exportada em GLB (`export_format="GLB"`, `export_apply=True`) e FBX
(`apply_scale_options="FBX_SCALE_ALL"`, `axis_forward="-Z"`, `axis_up="Y"`, `use_triangles=True`) e reimportada: mesmas dimensões,
escala 1, rotação 0, 12 tris. Isso prova o round-trip no Blender, não o import no engine: confira lá também.

## Unreal Engine

- FBX para skeletal/static; glTF/USD também importam. Blender metros → Unreal centímetros: FBX com
  `apply_unit_scale` ✔ resolve; objeto de 1,8 m deve medir 180 uu.
- Skeletal: o Unreal transforma o objeto armature num osso raiz extra, exceto quando o objeto se chama `Armature`;
  deixe o objeto como `Armature` e o primeiro osso como `root`. `add_leaf_bones` ✔ desligado; `primary_bone_axis`/`secondary_bone_axis` ✔ ajustados se os ossos vierem tortos.
- Colisão estática por prefixo (doc Epic ✔): `UBX_<Mesh>_##` caixa, `USP_` esfera, `UCP_` cápsula, `UCX_` convexo
  (fechado e convexo). Esfera/caixa falham em static mesh com escala não uniforme.
- LODs: alinhados, mesmo pivô; import com "Import LODs".
- Lightmap: UV channel 1 sem overlap (ou deixe o Unreal gerar). Normal map **DirectX**: inverta o verde.
- Nanite: pensado para malha estática densa; suporte a skeletal/translúcido/masked mudou entre versões do UE 5 — confira a doc da versão do projeto.
- Root motion: animação com deslocamento no osso raiz; habilite no asset de animação.

## Unity

- FBX: `apply_scale_options='FBX_SCALE_ALL'` ✔ (evita escala 100 e rotação −90 em X) ou "Apply Transform"; teste.
- Humanoid rig exige hierarquia humanoide mínima (hips, spine, head, membros); Generic para o resto.
- Blend shapes = shape keys. Normal map OpenGL (nativo do Blender).
- LOD Group é montado no Unity (ou pelo importador com sufixos `_LOD0`, `_LOD1`... — confirme na doc da versão).
- URP/HDRP têm canais de máscara diferentes; empacote conforme o pipeline usado.

## Godot 4

- Prefira **glTF/GLB** (`export_scene.gltf` ✔, `export_format='GLB'`). Godot também importa `.blend` direto se o caminho do Blender estiver configurado.
- Sufixos no nome do objeto (doc Godot ✔; separadores `-`, `$`, `_`; maiúsculas indiferentes):
  `-col` (colisão trimesh), `-convcol` (convexa), `-colonly`, `-convcolonly`, `-occ`/`-occonly` (occluder), `-navmesh`,
  `-rigid`, `-vehicle`, `-wheel`, `-noimp` (ignorar), `-loop`/`-cycle` (animação em loop), `-alpha`, `-vcol`.
- AnimationPlayer recebe as Actions; nomeie as Actions como os estados.

## Minecraft

- **Java**: modelos de bloco/item são JSON de cubos (elementos) com rotação por elemento limitada (um eixo, ângulos em passos fixos —
  confira o formato atual na wiki de modelos da versão alvo) e texturas 16×16 no estilo vanilla.
  Entidades customizadas dependem de mod/loader (ex.: GeckoLib). Blockbench é a ferramenta padrão; Blender serve para referência/render.
- **Bedrock**: `.geo.json` + animações JSON; Blockbench exporta direto. Formatos Java e Bedrock **não são intercambiáveis**.
- Do Blender para Minecraft: modele em cubos alinhados à grade de 1/16 de bloco, UV por face em pixels inteiros; importe no Blockbench (OBJ) e ajuste.
- Render estilo Minecraft no Blender: texturas com interpolação **Closest**.

## Outros destinos

| Destino | Formato | Atenção |
|---|---|---|
| Web/three.js/AR | GLB + Draco/meshopt ✔ | Khronos PBR Neutral para prever a cor; texturas ≤ 2048 |
| Roblox | FBX/OBJ | limites de tris por mesh e esqueleto R15; conferir doc atual |
| Impressão 3D | STL (`wm.stl_export` ✔) / 3MF | malha manifold, espessura mínima da impressora, escala em mm |
| VFX/cinema | USD (`wm.usd_export` ✔) / Alembic ✔ | caches de animação; Collada não existe mais no 5.x ✔ |

Engine nova: pesquise a doc oficial de import (unidades, eixo, formatos, limites de ossos/influências) antes do primeiro export.
