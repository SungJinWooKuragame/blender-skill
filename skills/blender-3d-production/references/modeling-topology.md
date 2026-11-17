# Modelagem e topologia

## Escolha do método (decida antes de começar)

| Objeto | Método | Topologia final |
|---|---|---|
| Produto, máquina, arma, veículo (render) | Poly + Bevel + Weighted Normal, ou SubD com loops de suporte | quads onde há SubD; n-gon plano tolerado sem SubD |
| Mesmo objeto para jogo | Low poly com bevel de 1–2 segmentos + Weighted Normal, ou bake de high | triângulos controlados, silhueta primeiro |
| Personagem, criatura, orgânico | Blockout → sculpt (voxel remesh → multires) → retopo → bake | quads com loops de deformação |
| Pedra, terreno, detalhe natural | Sculpt/displace + decimate ou GN | triângulos ok, sem deformação |
| Repetição/arquitetura/cabos | Geometry Nodes ou Array/Curve | instâncias |
| Logo 3D | Curva/SVG → mesh → bevel (ver lookdev-render.md) | n-gons planos ok, bevel com 3+ segmentos |

## Sequência profissional

1. **Referência e medidas**: tamanho real em metros antes do primeiro vértice. Imagem de referência como Empty/Reference alinhada.
2. **Blockout** só com formas primárias; valide silhueta e proporção pelo `review_render --shading clay` antes de detalhar.
3. **Formas secundárias** (painéis, recortes), depois **terciárias** (parafusos, textos). Detalhe pequeno que não muda a silhueta em jogo vira textura/normal map.
4. Nomeie e organize ao criar: `SM_Cadeira`, `SM_Cadeira_Perna_L`; collections por função (`GEO`, `COL`, `LOD`, `RIG`, `REF`).

## Hard surface: sombreamento limpo

O problema "parece IA/barato" quase sempre é **sombreamento**: bordas perfeitamente vivas e gradientes escuros em faces planas.

- Borda viva não existe no mundo real. Bevel em toda aresta que pega luz:
  modificador Bevel, `limit_method` Angle (~30°), `segments` 2–3 (jogo) ou 3–5 (render), `use_clamp_overlap` ligado.
- Gradiente em face plana depois de bevel/n-gon = normais interpoladas. Corrija com **Weighted Normal**
  (modificador `WEIGHTED_NORMAL`, "Keep Sharp") depois do Bevel, ou `harden_normals` no próprio Bevel ✔.
  Smooth shading necessário (`shade_smooth_by_angle`).
- Ordem típica da pilha: Mirror → Boolean(s) → Bevel → Weighted Normal → (Triangulate só no export).
- Boolean: cortadores em collection oculta `CUTTERS`, display Wire/Bounds; aplique só no fim. Solvers 5.3 ✔:
  `MANIFOLD` (rápido e robusto, exige malhas manifold), `EXACT` (aceita malha imperfeita, lento), `FLOAT` (legado).
  Faces coplanares geram lixo em qualquer solver: deixe 0.001 m de sobreposição.
- SubD: loops de suporte a ~10–20% da largura da face controlam a quina; crease para testes, não para export de jogo (engine não lê crease).
- Escala aplicada antes do Bevel (escala 2x deixa bevel desigual).

## Orgânico

- Sculpt: Voxel Remesh (resolução crescente) para formas grandes; Dyntopo para adicionar detalhe local;
  Multires para detalhe final que será bakeado. Face Sets e máscaras para isolar regiões.
- Ordem de pincel: Grab/Snake Hook (massa) → Clay Strips/Draw (volume) → Crease/Pinch (dobras) → Smooth com moderação.
- Anatomia: confira proporções com referência (cabeças de altura: ~7,5 realista, menos para estilizado); silhueta lida a 3 m de distância.

## Retopologia

- Ferramentas: Snap a Face (Project Individual Elements), Shrinkwrap no retopo, Poly Build, Remesh Quad (QuadriFlow) como ponto de partida.
- Loops concêntricos em olhos, boca, ombros; 3 loops em cotovelo/joelho; polos (3 ou 5 arestas) fora de zonas que dobram.
- Densidade segue a curvatura e a deformação, não a área.

## Limpeza obrigatória antes de UV/export

- Merge by Distance (`mesh.remove_doubles`, threshold 0.0001) ✔, Recalculate Outside (`mesh.normals_make_consistent`) ✔,
  remover vértices soltos e faces de área zero (o `qa_report.py` conta tudo isso).
- Face Orientation overlay: vermelho visível = normal invertida.
- Origem no lugar lógico (base do objeto para props, eixo de rotação para portas/rodas).
- Interseções escondidas em objeto de jogo: tudo bem se não aparece e não quebra bake; interseção que aparece = refaça.

## Erros comuns

| Sintoma | Causa | Correção |
|---|---|---|
| Faixa escura em face plana | normais suavizadas por n-gon/bevel | Weighted Normal / harden normals |
| Bevel com largura diferente por eixo | escala não aplicada | Ctrl+A Scale, refazer bevel |
| Boolean deixa buracos | malha não-manifold, faces coplanares | limpar, sobrepor 1 mm, solver Exact (ou Manifold se a malha for fechada) |
| Brilho "de plástico" em tudo | sem variação de roughness | ver lookdev-render.md |
| Objeto pesado e igual ao low | detalhe em geometria que deveria ser normal map | bake (uv-baking-texturing.md) |
