# Geometry Nodes, procedural, simulação e VFX

## Geometry Nodes

- Node group = ferramenta: entradas nomeadas com unidade e faixa (`Altura (m)` 0.1–10), padrões sensatos, agrupadas por painel.
- Instâncias até o fim (`Realize Instances` só quando precisa editar a malha ou exportar); instância é barata, malha realizada não.
- Atributos nomeados (`wear`, `id`) para alimentar material: `Store Named Attribute` → Attribute node no shader.
- Distribuição: `Distribute Points on Faces` (Poisson Disk para espaçamento mínimo) → `Instance on Points` com rotação/escala aleatória por seed exposta.
- Padrões úteis: escada (Mesh Line + Instance + offset), cerca/cabo ao longo de curva (Curve to Points/Resample + Instance),
  prédio (Grid → extrude por andar → instância de janelas por face), espalhar pedras/plantas com máscara de vertex group/ângulo.
- Export para engine: aplique o modificador ou exporte com modificadores avaliados; instâncias viram malha (glTF tem `export_gpu_instances` ✔).
- GTA: o Sollumz tem GN próprio para grama (`map_grass_create_geonodes` ✔).

## Simulação (offline)

| Efeito | Sistema | Nota |
|---|---|---|
| Queda/colisão de objetos | Rigid Body | escala aplicada; massa real; shape Convex Hull > Mesh |
| Destruição | Cell Fracture (add-on) + Rigid Body / constraints | pré-fratura; bake antes de render |
| Tecido | Cloth | colisão com espessura; mais qualidade = mais steps, não mais polígonos |
| Fumaça/fogo/líquido | Mantaflow (Fluid) | resolução baixa para timing, alta só no bake final; cache em disco |
| Corpo mole | Soft Body ou Cloth com pressão | |
| Simulação procedural | Simulation Zone (GN) | controle total, bake de cache |
Sempre: **bake** da simulação (cache), frame range definido, cache fora de pasta temporária.

## VFX para jogo (tempo real)

Simulação do Blender não roda em engine. Para jogo, entregue:
- Flipbook: renderize a sim em spritesheet (ex.: 8×8 quadros) com alpha, normal opcional.
- Mesh + shader animado (UV scroll, vertex color/máscara) para fogo/água estilizados.
- Vertex Animation Texture (VAT) para destruição/tecido pré-calculados (precisa shader do engine).
- GTA: partículas são `.ypt`, que o Sollumz não importa/exporta (não está entre os formatos do menu de import ✔); use os ptfx existentes do jogo.

## Cabelo e pelos

Curves (hair) com GN de grooming para render; para jogo: hair cards (planos com textura alpha) gerados dos curves e bakeados.
