# GTA V / FiveM: mapas, interiores (MLO) e roupas

Fontes: tutoriais "Creating Interiors" e "Basic Clothes Editing" do Sollumz 2.9 + código da extensão (✔ = conferido).

## Peças de um mapa

| Arquivo | Papel |
|---|---|
| `.ydr` | modelos (casca do prédio, móveis) |
| `.ybn` | colisão (casca/rooms) |
| `.ytyp` | archetypes: um por modelo + o archetype MLO (rooms, portals, entities) |
| `.ymap` | instâncias no mundo: onde cada archetype/MLO fica |
| `.ytd` | texturas |

FiveM: tudo em `stream/`; no manifest `this_is_a_map 'yes'` ✔ e `data_file 'DLC_ITYP_REQUEST' 'stream/x.ytyp'` ✔ para cada ytyp.

## Archetype (ytyp) — campos ✔ (doc)

`Type` (Base | Time | MLO) · `Name` · `Special Attribute` (portas, luzes, arbustos...) · `Texture Dictionary` · `Clip Dictionary` ·
`Drawable Dictionary` (vazio se o modelo não está num ydd) · `Physics Dictionary` (vazio ou = nome se física embutida) ·
`HD Texture Distance` (distância do +hi.ytd) · `LOD Distance` (onde o objeto some) · `Asset Type` (Drawable/Fragment/Drawable Dictionary/Assetless) ·
`Asset Name` (= nome do archetype).
Time archetype: objeto que só aparece em certas horas (janelas acesas à noite).

## Interior MLO passo a passo (Sollumz)

1. **Escolher prédio** no CodeWalker e importar a casca (doc "Picking a building" / "Importing from CodeWalker").
2. **Modelar** o interior com espessura de parede real; cada sala fechada; aberturas (portas) com batente para o portal.
3. **Texturizar** com shaders GTA (gta-assets.md).
4. **Colisão**:
   - corte o buraco da porta nas `.ybn` vanilla que tapam a entrada e confira de dentro;
   - duplique a casca (Shift+D), tire do drawable (Alt+P), `Convert to Composite`, **Apply Flag Preset** ✔;
   - material de colisão por superfície; **o piso de cada sala precisa de material diferente** para o Room ID funcionar.
5. **ytyp**: Sollumz Tools > Archetype Definition > YTYPS `+` → drawables como **Base** → `Auto-Create From Selected`;
   colisão como **MLO** → `Auto-Create From Selected`.
6. **Rooms**: `Create Limbo Room` primeiro (limbo = "fora"); `+` para cada sala; em Edit Mode selecione os 4 vértices da sala → `Set Bounds From Selection`.
7. **Portals**: selecione os 4 cantos da passagem → crie de **dentro para fora** (Room → Limbo); seta errada → `Flip Direction`.
   Portal entre duas salas internas: direção indiferente.
8. **Entities**: selecione o drawable → `Add Object(s) as Entity` → atribua a room (a casca vai no limbo).
9. **Export**: objetos selecionados e **visíveis** (oculto não exporta) → Export.
10. **ymap** no CodeWalker: novo ymap → nova entity com o nome do archetype MLO → cole a posição (copiada do Blender com
    General > Object Location & Rotation Tools) → **calcular flags e extents** → salvar → Tools > Generate manifest.
11. Teste: entrar e sair, luz/timecycle por sala, colisão de dentro, portas.

Erros clássicos: portal na direção errada (interior some ao entrar), room bounds menores que a sala (objetos piscam),
esquecer o flag preset (atravessa o chão), mesmo material de piso em salas diferentes (room ID não pega).

## Colisão: presets e materiais ✔ (código Sollumz)

Flag presets ✔: `General (Default)`, `General 2`, `Water surface`, `Leaves - Bush`, `Stair plane`, `Stair mesh`, `Deep surface`.
(Só os nomes vêm do código. Prática comum, não verificada aqui: escada com uma rampa simples de colisão no lugar dos degraus
para o personagem subir suave; confira o efeito de `Stair plane` vs `Stair mesh` em jogo.)
Materiais (182 no total), exemplos: `CONCRETE`, `CONCRETE_DUSTY`, `BRICK`, `MARBLE`, `ROCK`, `WOOD_SOLID_SMALL/MEDIUM/LARGE`,
`WOOD_SOLID_POLISHED`, `CARPET_SOLID`, `CARPET_FLOORBOARD`, `METAL_SOLID_SMALL/MEDIUM/LARGE`, `PLASTIC`, `PLASTIC_HOLLOW`,
`GLASS_SHOOT_THROUGH`, `GLASS_BULLETPROOF`, `GLASS_OPAQUE`, `GRASS`, `GRASS_SHORT`, `SAND_COMPACT`, `DIRT_TRACK`, `ROOF_TILE`, `RUBBER`.
Escolha o mais próximo do material visual: define som de passo, marca de bala e partícula. Lista completa no dropdown do Sollumz.
Primitivas (`Bound Poly Box/Capsule/Sphere`) sempre que possível; malha só quando a forma não sai de primitivas.
Composite e GeometryBVH na origem (0,0,0); renomeie o Bound Composite com o nome exato do `.ybn`.

## LOD de mapa

- Níveis no Sollumz ✔ (`LODLevel`): Very High, High, Medium, Low, Very Low.
- Hierarquia de LOD entre entidades (HD → LOD → SLOD) é gerida no grupo do mapa; use a ferramenta **Map LOD Hierarchy** do Sollumz
  (arrastar para ligar pai/filho). Contêineres com pai/filho faltando ficam travados para evitar perda no export.
- Interior MLO: o exterior do prédio continua com seus LODs; o interior só carrega perto.

## Roupas (componente de ped mp) — procedimento ✔ (doc)

1. CodeWalker RPF Explorer: exporte XML do esqueleto `x64v.rpf\models\cdimages\streamedpeds_mp.rpf\mp_m_freemode_01.yft`,
   do componente base (ex.: `jbib_007_u.ydd`, da pasta DLC base, não de hotfix) e do diffuse (`jbib_diff_007_a_uni.ytd`). Mesma pasta.
2. Blender: Import CodeWalker XML do `.ydd.xml` com **Import External Skeleton** ligado. Vertex groups devem ter nomes de osso
   (`SKEL_L_Hand`); `UNK.001` = esqueleto errado.
3. Find Missing Files para ligar o `.dds` do diffuse.
4. Por LOD (High/Medium/Low): Merge by Distance com **Sharp Edges**; troque LOD com Shift+V.
5. Edite (fechar buracos, Normals > Reset Vectors, Mark Sharp). Buracos de manga em Medium/Low podem ficar.
6. Export: selecione a hierarquia → Export CodeWalker XML para pasta nova → importe no CodeWalker para virar `.ydd`.
- Texturas embutidas: `jbib_normal_000`, `jbib_spec_000`; diffuse `jbib_diff_007_a_uni`.
- Vertex colors: Color 1 `#FF8000`; Color 2 `#000` alpha 0 (sem vento/suor); Face Corner + Byte Color. Emissivo: Color 1 `#FFBAFF`.
- Vertex group vazio/sem nome = roupa invisível no jogo. Normal/spec ausente = textura xadrez.
- FiveM: roupas addon seguem a nomenclatura de stream de roupas do FiveM (pasta `stream/` com nome do pacote + `.ymt`/meta);
  confira o guia atual de clothing do FiveM antes de publicar (não coberto pela doc do Sollumz).

## Não suportado pelo Sollumz ✔ (doc)

Ped `.yft` com esqueleto articulado + física extra: animais `a_c_*` e alguns personagens de história (`z_z_*`). Esqueletos simples
como `mp_m_freemode_01.yft` funcionam.
