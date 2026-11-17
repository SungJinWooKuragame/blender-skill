# GTA V / FiveM: assets

Ferramentas: Blender + **Sollumz 2.9** (import/export dos formatos), **CodeWalker** (ver mapa, posicionar,
converter, RPF), OpenIV (opcional, extrair RPF). Doc do Sollumz: docs.sollumz.org (índice completo em /llms.txt).
Antes de qualquer procedimento, confira a versão do Sollumz instalada (`blender_manifest.toml` da extensão).

## Formatos

| Ext | O que é | Sollumz |
|---|---|---|
| `.ydr` | Drawable: modelo estático (prop, peça) | DRAWABLE |
| `.ydd` | Drawable Dictionary: vários drawables (roupas de ped, componentes) | DRAWABLE_DICTIONARY |
| `.yft` | Fragment: modelo com física/quebra/ossos (veículos, props destrutíveis) | FRAGMENT |
| `.ytd` | Texture Dictionary | export_ytd / txd_* |
| `.ybn` | Bounds: colisão estática | BOUND_COMPOSITE |
| `.ytyp` | Archetypes: define o modelo (lodDist, flags, txd, física) | createytyp/createarchetype |
| `.ymap` | Placement: onde as entidades ficam no mundo | createymap |
| `.ycd` | Clip Dictionary: animações (ver gta-animation.md) | CLIP_DICTIONARY |
| `.ynv` | Navmesh | NAVMESH |

Prefixos de `.ybn`: normal (jogadores/veículos), `hi@` (balas), `ma@` (spawn procedural de lixo/grama).

## Export (Sollumz 2.9 ✔)

- `Target Formats`: **Native** (binário pronto para o jogo; requer pymateria) e/ou **CW XML** (precisa passar pelo CodeWalker). Padrão: ambos.
- `Target Game Versions`: **Gen8 = GTAV Legacy**, **Gen9 = GTAV Enhanced**; com os dois, saem em `gen8/` e `gen9/`.
  FiveM roda sobre o Legacy: use os arquivos **gen8** no `stream/` (confirme na doc do FiveM se isso mudar).
- `Limit to Selected` ligado por padrão: selecione o objeto raiz antes de exportar.
- `Exclude Skeleton`: para componentes de ped mp (roupas) que usam o esqueleto do ped.
- `Apply Parent Transforms` desligado por padrão: escale/rote o objeto filho, não o raiz.
- Operadores ✔: `sollumz.export_assets`, `sollumz.import_assets`, `sollumz.converttodrawable`, `sollumz.createshadermaterial`,
  `sollumz.autoconvertmaterials`, `sollumz.createbound`, `sollumz.converttocomposite`, `sollumz.createytyp`,
  `sollumz.createarchetypefromselected`, `sollumz.auto_lod`, `sollumz.extract_lods`, `sollumz.generate_wheel_instances`,
  `sollumz.calculate_mass`, `sollumz.export_ytd`, `sollumz.find_missing_textures`, `sollumz.material_merge_bake`.

## Shaders

Principled BSDF não vira shader GTA sozinho. Cada material precisa de um shader `.sps` (296 disponíveis ✔).
Escolha pelas três perguntas: tem normal map? tem specular? tem alpha?

| Caso | Shader |
|---|---|
| Só cor | `default` |
| Cor + normal | `normal` |
| Cor + normal + specular (mais comum em props) | `normal_spec` |
| Recorte binário (grade, folha) | `cutout`, `normal_spec_cutout`, `cutout_fence` |
| Transparência real | `alpha`, `normal_spec_alpha`, `glass`, `glass_pv` |
| Decal | `decal`, `normal_spec_decal`, `decal_dirt` |
| Luz/emissivo | `emissive`, `emissivenight` (só à noite), `emissivestrong` |
| Tint de paleta | variantes `_tnt` |

Samplers do `normal_spec`: DiffuseSampler (cor), BumpSampler (normal, **Non-Color**), SpecSampler.
Normal map no BumpSampler em Color = aparência errada no Blender (export não muda, mas você avalia errado).

## Prop (ydr) passo a passo

Testado headless (Sollumz 2.9, Native + Gen8): cubo → `normal_spec` → `converttodrawable` → colisão `converttocomposite` →
`export_assets` gerou `nome.ydr` (693 B) e `nome_col.ybn` (153 B). Lições do teste:
- **Drawable sem material de shader Sollumz não exporta o `.ydr` e o operador ainda retorna FINISHED.** Confira os arquivos gerados, nunca o retorno.
- Colisão sem material de colisão exporta só com WARNING: adicione material antes (`createcollisionmaterial`).
- Com uma só versão marcada (só Gen8) os arquivos saem na raiz da pasta, sem subpasta `gen8/`.
- Por script: `bpy.ops.sollumz.createshadermaterial(shader_index=i)`, com `i` = índice em
  `importlib.import_module("<pacote_sollumz>.ydr.shader_materials").shadermats` cujo `.value == "normal_spec.sps"`;
  `bpy.ops.sollumz.export_assets(directory=...)` respeita `Limit to Selected` das preferências do add-on.

1. Modelo com escala real, origem na base, transformações aplicadas, UV pronto, texturas em potência de 2 (DDS no final; BC1/DXT1 sem alpha, BC3/DXT5 com alpha).
2. Shader Tools → escolha o shader → `Create Shader Material` → ligue as texturas nos samplers.
3. Selecione → `Convert to Drawable` ✔ (vira a hierarquia drawable → model; o mesh ativo vai para LOD High).
4. Colisão (abaixo), LODs (abaixo).
5. Texturas: embutidas no ydr (simples) ou num `.ytd` com o mesmo nome do modelo (reaproveitável).
6. `.ytyp` com o archetype: nome do modelo, `lodDist`, texture dictionary, flags. Gere com `createarchetypefromselected`.
7. FiveM: `stream/` com `.ydr`, `.ytd`, `.ybn`, `.ytyp` e no `fxmanifest.lua`: `data_file 'DLC_ITYP_REQUEST' 'stream/nome.ytyp'` ✔.
   Mapa (ymap): `this_is_a_map 'yes'` ✔.
8. Teste: `CreateObject(joaat('nome'), ...)` em jogo e ver colisão, LOD em distância e sombra.

## Colisão (ybn ou embutida)

Hierarquia ✔: `BoundComposite` → `BoundGeometryBVH` (malha) ou primitivas (`BoundBox`, `BoundSphere`, `BoundCapsule`, `BoundCylinder`) / `BoundPolyBox`…
- **Aplique um Flag Preset no BoundGeometryBVH.** Esquecer isso é o erro mais comum: colisão não funciona no jogo.
- Malha de colisão simples (dezenas a centenas de tris), fechada, sem detalhe; primitivas sempre que der.
- Material de colisão (concreto, metal, madeira...) define som, partícula e física; escolha pelo material real.
- Room ID para MLO (interiores); Procedural ID em `ma@`.

## LOD

Níveis no Sollumz ✔ (código `LODLevel`): Very High, High, Medium, Low, Very Low (Data > Sollumz LOD). Prop simples: só High.
`sollumz.auto_lod` ✔ gera níveis reduzidos; confira cada um visualmente.
Asset de mapa: LOD reduzido de verdade em Medium/Low (50% / 25% / 10% dos tris como ponto de partida) + `lodDist` coerente
no ytyp (props pequenos 50–150 m; prédios 300+). Mesmo mesh em todos os níveis = nenhum ganho.

## Veículo (yft)

Caminho mais seguro: **importar um veículo vanilla parecido** e substituir as peças (hierarquia, ossos e metas já corretos).
Do zero só se necessário.
- Ossos ✔ (BoneProperties do Sollumz): `chassis`, `bodyshell`, `wheel_lf/rf/lr/rr` (+ `wheel_lm1..3`/`rm1..3`),
  `hub_lf`, `suspension_lf`, `door_dside_f/r`, `door_pside_f/r`, `bonnet`, `boot`, `bumper_f/r`, `windscreen`,
  `window_lf…`, `wing_lf`, `headlight_l/r`, `taillight_l/r`, `indicator_lf…`, `brakelight_l`, `reversinglight_l`,
  `platelight`, `interiorlight`, `siren1…`, `steeringwheel`, `seat_dside_f`, `exhaust`, `engine`, `petroltank`, `extra_1…`, `misc_a…`.
- Peça nova: vertex group com o nome do osso, Drawable Model dentro de `<carro>.mesh`, modificador Armature apontando para o armature do carro (doc Sollumz).
- Rodas: uma roda (`wheel_lf`) é reaproveitada pelo jogo; mesh sem vertex group, presa por Child Of; marque `Is Wheel Mesh`; `Generate Wheel Instances` para pré-visualizar.
- Luzes: shader `vehicle_lightsemissive` + **Light ID** por face (Sollumz Tools > Fragment > Vehicle Light IDs); sem ID a luz fica sempre acesa.
- Shaders de veículo ✔: `vehicle_paint1..9` (cor de pintura; 3 = livery; variantes `_enveff` = neve), `vehicle_mesh` (metal/chassi),
  `vehicle_vehglass` / `_inner`, `vehicle_interior` / `2`, `vehicle_tire`, `vehicle_shuts` (batentes/cofre), `vehicle_badges`,
  `vehicle_decal`/`2`, `vehicle_dash_emissive`, `vehicle_licenseplate`, `vehicle_detail2`.
- Vertex color do veículo: R = AO, G = deformação (dano), B = queimado.
- Export: escolha hi, não-hi ou ambos (`_hi.yft` é o de perto). Metas no resource FiveM ✔: `VEHICLE_METADATA_FILE` (vehicles.meta),
  `HANDLING_FILE`, `CARCOLS_FILE`, `VEHICLE_VARIATION_FILE` (carvariations), `VEHICLE_LAYOUTS_FILE`.
- Enhanced (Gen9): limite de 128 materiais/geometrias por arquivo; texturas `script_rt_` em A8R8G8B8.

## Mapas, interiores (MLO) e roupas

Ver [gta-maps-mlo.md](gta-maps-mlo.md).

## Limites e performance FiveM

- Arquivo de stream grande trava o carregamento: ydr/yft até alguns MB; texturas 2048 só no que aparece de perto (veículo, arma); prop pequeno 512–1024.
- Menos materiais = menos draw calls; agrupe texturas num atlas quando possível.
- Teste com `resmon` e com a visão de streaming do CodeWalker; prop sem LOD em ymap grande derruba FPS.
