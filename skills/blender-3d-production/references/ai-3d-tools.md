# IA aplicada ao 3D

IA acelera rascunho, nunca entrega asset pronto. Ferramentas mudam rápido: confirme nome, preço e licença
na página oficial antes de recomendar.

## Categorias

| Uso | Exemplos (verifique disponibilidade) | Saída típica |
|---|---|---|
| Imagem/texto → 3D | Meshy, Tripo, Rodin (Hyper3D), Hunyuan3D, TRELLIS | malha triangulada densa + textura projetada |
| Textura/material | geradores de PBR por texto/imagem, upscalers | mapas que precisam conferência |
| Mocap por vídeo | Move AI, Rokoko Vision, DeepMotion | FBX/BVH com jitter e pé deslizando |
| Retopo automática | QuadriFlow/Remesh do Blender, Instant Meshes | quads uniformes sem fluxo de deformação |
| Concept/referência | geradores de imagem | só referência; proporção e construção não são confiáveis |

Skills relacionadas que podem estar instaladas: `move-ai-motion-capture`, `blender-motion-capture`.

## Malha gerada por IA → produção

1. `qa_report.py`: espere non-manifold, buracos, vértices soltos, escala arbitrária, milhões de tris.
2. Escala real e orientação; origem no lugar certo.
3. Limpeza: merge by distance, remover componentes soltos pequenos, fechar buracos, recalcular normais.
4. Decidir: retopo (personagem/deforma) ou decimate + limpeza (prop estático).
5. UV novo (o UV gerado costuma ser picado) e **bake** da textura original para o UV novo (selected to active).
6. Refaça materiais: textura de IA traz luz e sombra "assadas" na cor (delighting necessário) e roughness inexistente.
7. Detalhe hard surface gerado por IA é mole: arestas que deveriam ser retas saem onduladas. Refaça peças-chave na mão.
8. `review_render.py` lado a lado com a referência; só então siga o pipeline do destino.

## Mocap de IA → limpeza

Filtrar jitter, travar pés no apoio, corrigir chão, remover rotação de raiz espúria, retarget para o esqueleto do destino
(rigging-animation.md; para GTA, gta-animation.md).

## Direitos

Verifique a licença comercial do serviço e da referência usada. Não reproduza marca/personagem protegido como asset próprio.
