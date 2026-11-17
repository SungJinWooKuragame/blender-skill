# Otimização

Otimize contra um orçamento do destino, nunca "o máximo possível". Meça antes e depois (`qa_report.py`: tris por objeto, materiais).

## Orçamentos de partida (ajuste ao projeto)

| Asset | Tris (LOD0) | Texturas |
|---|---|---|
| Prop pequeno de jogo | 100–2.000 | 512–1024 |
| Prop médio / móvel | 2.000–10.000 | 1024–2048 |
| Arma 1ª pessoa | 10.000–40.000 | 2048–4096 |
| Personagem jogável | 20.000–80.000 | 2048–4096 (corpo + cabeça) |
| Veículo GTA/jogo | 50.000–150.000 (hi) | 1024–2048 por conjunto |
| Mobile/VR | divida por 3–5 | ≤ 1024 |

## LOD

- Cadeia típica: LOD1 50%, LOD2 25%, LOD3 10% dos tris; silhueta preservada, detalhe interno removido primeiro.
- Decimate (Collapse) para orgânico; para hard surface, remova loops/bevels manualmente (decimate destrói arestas).
- Normais e UV do LOD compatíveis com as texturas do LOD0 (mesmo UV) para não trocar textura.
- Distância de troca coerente: troca visível ("pop") = distância curta demais ou LOD pobre demais.

## Texturas e materiais

- Cada material = ao menos um draw call; junte peças que compartilham material, use atlas/trim sheet.
- Channel packing (ORM), compressão do destino (BC1/BC3/BC5/BC7; DXT no GTA), mipmaps.
- Resolução pelo tamanho na tela, não pelo gosto. Texel density consistente (uv-baking-texturing.md).

## Cena (render)

- Instâncias (Alt+D, GN) em vez de cópias. Simplify para viewport. Subdivisão adaptativa só em close.
- Ruído: denoise + adaptive sampling antes de aumentar amostras.
- VRAM: texturas 8K desnecessárias e displacement real em tudo são os vilões.

## Erros comuns

- Otimizar a malha e esquecer as 12 texturas 4K.
- Triangular com "Beauty" depois do bake de normal (sombreamento muda). Triangule antes do bake e exporte igual.
- Remover polígonos da silhueta em vez dos internos.
