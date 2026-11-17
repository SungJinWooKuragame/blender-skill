# UV, baking e texturas PBR

## UV

- Seams onde a vista não chega e onde a superfície já quebra (quinas duras, divisões de material). Toda quina
  "hard" (sharp) precisa de seam junto, senão o normal map bakeado mostra costura.
- Texel density consistente no asset (e entre assets que aparecem juntos). Referência comum para jogo em 1ª/3ª pessoa:
  ~512–1024 px/m para props, mais para armas/rosto. Use `uv.average_islands_scale` ✔ antes de empacotar.
- Empacote com `uv.pack_islands` ✔ e margem: textura 2048 → ~8 px (0.004); 1024 → 4 px. Margem pequena + mipmaps = sangramento.
- Overlap só intencional (peças espelhadas/repetidas) e desloque a cópia 1 UDIM (+1 em U) durante o bake.
- Stretch: overlay de UV Stretch no editor; azul é bom, vermelho é refazer.
- Smart UV (`uv.smart_project` ✔) é aceitável para hard surface de bake rápido; nunca para personagem.
- Lightmap de engine (Unreal/Unity estático): segundo UV map sem overlap.

## Baking high → low (Cycles)

Configuração (`scene.render.bake` ✔: `use_selected_to_active`, `use_cage`, `cage_extrusion`, `max_ray_distance`, `margin`, `normal_space`):
1. Low poly com UV final, sem overlap (exceto deslocado), triangulado igual ao export (triangule antes de bakear normal
   ou o engine re-triangula diferente e aparecem sombras).
2. High selecionado, low ativo; `cage_extrusion` mínimo que cubra o high (comece 0.01–0.05 m), ou objeto cage dedicado.
3. Imagem alvo em Image Texture **selecionado** no material do low (Non-Color para normal/dados).
4. Margem (`margin`) 8–16 px. Resolução final só depois que o teste em 512 sair limpo.
5. Bakes: Normal (Tangent), AO, Curvature (via GN/atributos ou pointiness), ID de material, Height.
Problemas: ondas no normal = cage curto; "costura" = UV seam sem sharp ou vice-versa; manchas = high atravessando o low.

## Convenção de normal map (verde)

| Destino | Formato | No Blender |
|---|---|---|
| Blender, Unity, Godot, glTF | OpenGL (Y+) | nativo |
| Unreal | DirectX (Y−) | inverta o canal G no export ou marque "Flip Green" no import do Unreal |
Normal com relevo invertido no destino = canal verde errado.

## PBR

- Metalness: metal = 1, não-metal = 0; valores intermediários só em transição (sujeira sobre metal).
- Base color de não-metal entre ~30 e 240 sRGB (carvão ~50, neve ~240). Preto puro e branco puro parecem falsos.
- Roughness é o mapa que mais vende realismo: variação sutil (manchas, digitais, desgaste nas bordas) > textura de cor.
- Color space: Base Color/Emission = sRGB; Roughness/Metallic/Normal/AO/Height/máscaras = Non-Color.
  O `qa_report.py` acusa mapa de dados em sRGB.
- Channel packing (economiza memória): **ORM** = R AO, G Roughness, B Metallic (padrão glTF/Unreal). Unity HDRP usa
  "mask map" com ordem própria; confira o destino.
- Resoluções em potência de 2 (512, 1024, 2048, 4096). Não potência de 2 quebra mipmap/compressão em engine.

## Texturização procedural → imagem

Procedural do Blender (Noise, Voronoi, Bevel node, AO node, Pointiness) **não existe fora do Blender**.
Para jogo: bake de Diffuse (só Color), Roughness, Normal para imagens. Para desgaste de borda,
use curvature/AO bakeado como máscara.

## Materiais de referência rápida

| Material | Base color (sRGB aprox.) | Metallic | Roughness |
|---|---|---|---|
| Alumínio escovado | 220,220,225 | 1 | 0.3–0.45 + anisotropia |
| Aço/cromo | 200,200,205 / 250 | 1 | 0.05–0.25 |
| Ouro | 255,195,85 | 1 | 0.15–0.3 |
| Plástico brilhante | qualquer | 0 | 0.1–0.3 |
| Borracha | 30–50 | 0 | 0.7–0.9 |
| Concreto | 130–170 | 0 | 0.8–0.95 |
| Madeira envernizada | marrom | 0 | 0.2–0.4 (com coat) |
| Vidro | — | 0 | 0–0.05, Transmission 1, IOR 1.45–1.52 |
