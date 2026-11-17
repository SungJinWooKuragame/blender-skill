---
name: blender-3d-production
description: Use when doing any Blender or 3D production task — modeling (hard surface, organic, sculpt, retopology), UVs, baking, PBR materials, shaders, lighting, rendering, logos/product shots, rigging, weight painting, animation, Geometry Nodes, simulation/VFX, bpy scripting, optimization/LODs, or exporting to GTA V/FiveM (Sollumz, CodeWalker, ydr, yft, ytd, ybn, ytyp, ycd), Unreal, Unity, Godot or Minecraft. Also when a 3D result "looks AI-made", "cheap", "fake" or "flat", or an AI-generated mesh must be made production-ready.
license: MIT
compatibility: "Blender 5.2+ (verified on 5.3). GTA V needs Sollumz 2.9 and CodeWalker."
metadata:
  version: "1.0.0"
---

# Blender 3D Production

Um asset só está pronto quando funciona no destino: geometria limpa, escala
real, materiais que exportam e números medidos. Bonito no viewport não basta.

## 1. Antes de tocar na cena

1. **Destino** define tudo: render/produto, GTA/FiveM, Unreal, Unity, Godot,
   Minecraft, impressão 3D. Sem destino definido, pergunte; é a única pergunta
   obrigatória. O resto escolha e justifique em uma linha.
2. **Cena existente é trabalho do usuário**: liste objetos, collections,
   modificadores e materiais antes de mudar; não renomeie nem apague o que não
   foi pedido; salve cópia (`save_as_mainfile(copy=True)`) antes de edição destrutiva em lote.
3. Versão: `bpy.app.version_string`. API mudou no 5.x; confira em
   [references/bpy-api-5x.md](references/bpy-api-5x.md) antes de escrever código.

## 2. Carregue só a especialidade da tarefa

| Tarefa | Arquivo |
|---|---|
| Script bpy, automação, erros de API, MCP vs headless | [bpy-api-5x.md](references/bpy-api-5x.md) |
| Hard surface, orgânico, sculpt, retopo, topologia, modificadores | [modeling-topology.md](references/modeling-topology.md) |
| UV, texel density, baking, PBR, color space, texturas | [uv-baking-texturing.md](references/uv-baking-texturing.md) |
| Visual premium: logo 3D, produto, materiais, luz, câmera, render | [lookdev-render.md](references/lookdev-render.md) |
| Rig, weight paint, animação, NLA, mocap, export de clips | [rigging-animation.md](references/rigging-animation.md) |
| GTA V/FiveM: formatos, shaders, props, veículos, colisão, LOD | [gta-assets.md](references/gta-assets.md) |
| GTA V/FiveM: mapas, interiores MLO, ymap/ytyp, roupas de ped | [gta-maps-mlo.md](references/gta-maps-mlo.md) |
| GTA V/FiveM: animação de ped/objeto, YCD, clip dictionary | [gta-animation.md](references/gta-animation.md) |
| Unreal, Unity, Godot, Minecraft, glTF/FBX/USD | [game-engines.md](references/game-engines.md) |
| Geometry Nodes, procedural, física, VFX | [procedural-sim-vfx.md](references/procedural-sim-vfx.md) |
| Orçamento de polígonos, LOD, textura, draw calls | [optimization.md](references/optimization.md) |
| Mesh/textura/mocap gerado por IA | [ai-3d-tools.md](references/ai-3d-tools.md) |
| Onde confirmar algo que não está aqui | [sources.md](references/sources.md) |

Tarefa simples = zero ou um arquivo. Tarefa de pipeline (ex.: carro para FiveM) = os 2 ou 3 da rota.
Nas references, ✔ = conferido por introspecção no Blender 5.3 / código do Sollumz 2.9 / doc oficial; sem ✔ = prática consolidada, confira se crítico.
Se `blender-core` estiver instalada, use-a para execução (MCP/headless) e esta skill para critério, pipeline e destino.

**Achar o Blender** (headless): processo aberto (`Get-Process blender | Select Path`), Steam (`<Steam>/steamapps/common/Blender/blender.exe`),
`C:\Program Files\Blender Foundation\Blender <ver>\blender.exe`, ou variável `BLENDER_PATH`. Não varra o disco inteiro.

## 3. Regras que valem sempre

- **Dados, não operadores**: `bpy.data`, `bmesh`, `foreach_get/set`. Operador só com `temp_override` e checando `{'FINISHED'}`.
- **Escala real**: 1 unidade = 1 m. Aplique rotação/escala antes de bevel, modificadores com distância, rig, física, bake e export.
- **Não invente** operador, propriedade, nome de osso, flag ou shader. Confirme por introspecção (`T.bl_rna.properties`, `dir(bpy.ops.x)`) ou doc. Não confirmou: diga.
- **Scripts idempotentes**: rodar duas vezes não duplica objeto, material nem modificador (busque por nome antes de criar).
- **Mapas de dados** (roughness, metallic, normal, AO, máscaras) = `Non-Color`. Cor = `sRGB`.
- **Shader procedural do Blender não exporta** para engine nenhuma: bake para imagem.
- **Export que "deu certo" não prova nada**: reimporte ou abra no destino.

## 4. Ciclo de qualidade (obrigatório antes de "pronto")

```bash
blender -b cena.blend --python scripts/qa_report.py -- --objects Nome      # números + problemas
blender -b cena.blend --python scripts/review_render.py -- --objects Nome --out C:/tmp/rev.png --shading clay
```
Via MCP: `import sys; sys.path.insert(0, r"<skill>/scripts"); import qa_report; qa_report.run(["Nome"])`.
Logo/produto premium: `scripts/logo_studio.py` (cena separada com cópia do objeto; detalhes em lookdev-render.md).
GTA: `scripts/gta_ycd_export.py` + `scripts/ycdconv.ps1` (animação, ver gta-animation.md).
`review_render` restaura engine, resolução, color management, câmera, World e materiais (testado headless com duas execuções na mesma sessão).

1. Rode `qa_report` → zere os problemas ou justifique cada um.
2. Rode `review_render` (clay para forma, material para acabamento) → **olhe as imagens** e critique
   silhueta, proporção, sombreamento (gradiente estranho = normais), reflexo nas bordas.
3. Corrija e repita. Mínimo duas voltas em trabalho visual.
4. Reporte números: tris, dimensões (m), materiais, texturas (resolução), arquivos gerados com tamanho.

## 5. Ao terminar

Feche com até três linhas: o que foi verificado e como (script, render, reimport,
teste no jogo/engine), o que não foi testado no destino e qualquer coisa marcada
como não verificada.
