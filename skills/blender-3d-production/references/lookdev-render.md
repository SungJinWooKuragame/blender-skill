# Visual premium: materiais, luz, câmera e render

Objetivo: o observador diz "que lindo", não "mais um 3D de IA". O que denuncia trabalho amador
(em ordem de frequência) e a correção:

| Denúncia | Correção |
|---|---|
| Bordas vivas, sem reflexo nas quinas | Bevel (3–6 segmentos em render) + Weighted Normal |
| Material liso e uniforme | variação de roughness (noise grande + fino), micro-normal, coat onde cabe |
| Luz chapada (HDRI padrão ou 1 sol) | luz desenhada: key + rim + fill, refletores grandes para reflexo |
| Cores saturadas, preto/branco puros | paleta restrita (2–3 cores + neutro), valores entre 5% e 95% |
| Fundo vazio ou gradiente genérico | fundo intencional: infinito (cyclorama), cor da marca escurecida, sombra de contato |
| Câmera 50 mm de frente, centralizada | tele (85–135 mm) para produto/logo, ângulo 3/4, regra dos terços |
| Tudo no mesmo nível de detalhe | hierarquia: um herói nítido, o resto suporta |
| Sem profundidade | DOF sutil (f/2.8–5.6 em escala real), névoa leve, sombra de contato |

## Logo 3D premium (estilo Apple / PlayStation)

Ponto de partida testado: `scripts/logo_studio.py -- --text S --out x.png` (ou `--object MeuLogo`). Monta tudo abaixo;
itere a partir dele com o ciclo de revisão. Lições do teste (3 iterações até ficar bom):
- **Fundo escuro precisa de Roughness 1 e Specular IOR Level 0.** Com roughness 0.6 o chão escuro reflete as luzes no ângulo
  rasante (Fresnel) e fica branco — o render parecia "fundo cinza genérico".
- **Apoie o objeto no chão** (base = menor Z do bound box) para ter sombra de contato; objeto flutuando com sombra longe = cara de IA.
- **Spread das Area lights ~35°** evita lavar o fundo; luz grande e forte na frente lava a cor do metal — softbox frontal menor e alto
  dá gradiente na face, strips laterais finas (0.9 × 0.08 m) desenham as bordas.
- Bevel ≈ 3% do tamanho do logo com 5 segmentos; menor que isso não pega brilho.
- Valores do teste (logo de 0.2 m, Cycles, AgX Medium High Contrast): frontal 0.6 m / 15 W a ~1.6 m; strips 12 W a 0.45 m de cada lado;
  rim 0.6 m / 20 W atrás; câmera 100 mm f/4 a ~1.3 m. Escale energia com o quadrado do tamanho da cena.

Passos (o script faz 2–7):

1. **Fonte vetorial**: importe SVG (File > Import > SVG) ou desenhe curvas; escala real (ex.: 0.2 m de largura).
2. Curva → `Extrude` 0.01–0.03 m, `Bevel Depth` pequeno, ou converta para mesh e use modificador Bevel (3–6 segmentos, perfil 0.5–0.7).
   Conferir: n-gons das faces frontais planos e sem triângulos finos (Triangulate com "Beauty" ou remesh nas faces planas se sombrear errado).
3. Material herói, escolha um:
   - Metal anodizado/escovado: Metallic 1, Roughness 0.25–0.4, Anisotropic 0.5–0.8 com rotação radial ou linear.
   - Vidro/acrílico: Transmission 1, Roughness 0–0.05, IOR 1.49, leve Thin Film para iridescência sutil.
   - Cerâmica/plástico premium: Metallic 0, Roughness 0.3–0.5, Coat Weight 0.3–0.6.
   - Emissivo (neon): Emission Strength 5–30 em AgX com Bloom/Glare no compositor; o objeto ainda precisa de forma (bevel + material escuro em volta).
4. Luz de estúdio: 2–3 Area lights **grandes** (retangulares, alongadas) criando faixas de reflexo nas bordas;
   uma rim por trás para separar do fundo; HDRI de estúdio só como preenchimento (strength 0.1–0.3).
   Em metal, o que se vê é o reflexo das luzes: posicione as luzes olhando o reflexo, não a iluminação.
5. Fundo: plano curvo (cyclorama) ou cor sólida escura; sombra de contato suave (luz grande e próxima).
6. Câmera 85–135 mm, leve inclinação, DOF sutil focado na borda frontal.
7. Render: Cycles para vidro/metal/cáusticas; AgX com look `AgX - Medium High Contrast` ou `AgX - Punchy` ✔; denoise ligado.
8. Variações para "chamativo": animação curta de rotação de 15–30° com a luz varrendo a borda (faixa de reflexo passando) é mais elegante que giro completo.

## Iluminação por tipo

| Cena | Setup |
|---|---|
| Produto/logo | 2 softboxes grandes laterais + rim + fill fraco; fundo escuro ou cyclorama |
| Personagem | key 45° lateral-alta, fill 1/4 da key do outro lado, rim forte atrás; HDRI ambiente |
| Exterior dia | Sun (força 3–5 em AgX, ângulo 0.5–2° para sombra suave) + Sky/HDRI |
| Interior | luz pela janela (Area/Sun) + portais de luz; bounces Cycles ≥ 6 |
| Cinematográfico | contraste alto, temperatura key quente vs fill frio (3200 K / 6500 K), volumétrico leve |

Temperatura: use Blackbody (nó) ou cor da luz; não misture 5 temperaturas sem motivo.

## Render

- Cycles: amostras com Adaptive Sampling (noise threshold 0.01–0.02), Denoise (OpenImageDenoise), Light Paths:
  aumente transmission/glossy para vidro; Clamp indirect 5–10 contra fireflies.
- EEVEE (`BLENDER_EEVEE`): rápido para look dev e revisão; raytracing ligado para reflexos; confira sombras e light threshold.
- Color management: AgX padrão; Standard só para texturas/UI; Khronos PBR Neutral para comparar com viewer de glTF/e-commerce.
- Compositor (`scene.compositing_node_group` no 5.x): Glare (bloom), Lens Distortion leve, vinheta sutil. Grading leve: não salve render ruim no compositor.

## Ciclo de revisão (o que separa bonito de genérico)

1. Render pequeno (512) de 2–4 ângulos (`scripts/review_render.py`) ou do ângulo final.
2. Leia a imagem e responda por escrito: silhueta lê? há reflexo nas bordas? os valores vão do quase preto ao quase branco?
   o olho vai para o herói? algo parece plástico/CG?
3. Mude uma coisa por vez (luz, roughness, câmera) e re-renderize. Pare quando duas revisões seguidas não acharem defeito.
4. Render final só depois disso, em resolução cheia.
