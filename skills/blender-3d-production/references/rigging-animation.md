# Rigging, weight paint e animação

Se a skill `blender-animation` estiver instalada (descreve keyframing, actions em camadas, NLA, retarget), use-a para a mecânica
e este arquivo para os critérios de qualidade. Sem ela, os padrões abaixo e os de gta-animation.md bastam.

## Rig

- Modele em pose neutra do destino: T-pose (Unreal Mannequin antigo, Mixamo) ou A-pose (Unreal 5 Manny/Quinn, MetaHuman).
  Rig de jogo com destino conhecido: **use o esqueleto do destino**, não crie um novo.
- Separe ossos de deformação (`DEF-`/nome do jogo) de controles (`CTRL-`, `MCH-`). Exporte só deform
  (`use_armature_deform_only` no FBX ✔, `export_def_bones` no glTF ✔).
- Rigify para personagem de render/animação; para jogo, gere o rig e exporte só a camada DEF, ou use rig simples (FK + IK de pernas).
- Bone roll consistente (Recalculate Roll > Global +Z para coluna; eixo de dobra alinhado em braços/pernas) — roll errado = IK torcendo.
- IK: pole target para joelho/cotovelo; corrente com 2 ossos; leve pré-dobra no rest pose para o IK saber o lado.
- Organização: bone collections (`armature.collections` ✔) por função: Body, Face, IK, FK, MCH.

## Weight paint

1. Automatic Weights como base (malha manifold, sem vértices duplicados, escala aplicada; senão o heat falha com "Bone Heat Weighting failed").
2. Limite de influências: 4 por vértice para a maioria dos engines (`object.vertex_group_limit_total` ✔ limit=4), depois
   `object.vertex_group_normalize_all` ✔.
3. Teste em poses extremas (agachar, braço acima da cabeça, torção 90°) gravadas numa action de teste de 10 frames.
4. Ombro, quadril, joelho e cotovelo: suavize por loops, não por pincel aleatório; joelho/cotovelo dobrado não pode perder volume (use ossos de twist/corretivos ou shape keys corretivas).
5. Malha que não deforma (botões, fivelas) = peso 1 num osso só ou objeto parentado com Child Of.

## Animação: qualidade mensurável

Os 12 princípios viram checagens:
- **Timing/spacing**: Graph Editor; picos ou degraus indesejados em F-curves = pop. Meça a maior variação de rotação por frame dos ossos principais; picos isolados indicam erro.
- **Arcos**: Motion Paths em mãos/cabeça; trajetória em zigue-zague = corrigir.
- **Antecipação e follow-through**: ossos de cadeia (coluna → pescoço → cabeça, ombro → mão) chegam em frames diferentes (offset 1–3 frames), não juntos.
- **Peso**: pelve desce no contato e sobe na passagem; pés travados no chão durante apoio.
- **Foot sliding**: no apoio, posição mundial do pé varia < 1 cm entre frames. Meça com `matrix_world @ pose_bone.head` por frame.
- **Contato com chão**: Z mínimo dos pés constante no apoio; clip que afunda ou flutua > 1 cm deve ser corrigido.
- **Loop**: primeiro e último frame idênticos (pose e velocidade); exporte sem duplicar o frame final quando o destino faz o loop sozinho.
- **Silhueta**: pose lida em contraluz.

## Sistema de Actions (5.x)

- Actions em camadas com slots ✔ (`action.slots`, `action.layers`, `action.is_action_layered`). Código antigo com
  `action.fcurves` falha; leia as curvas com
  `[fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]` ✔ (testado no 5.3).
- Um clip por Action; nomeie como o destino espera (`Idle`, `Walk_F`, `anim@x@clip`).
- NLA para combinar/emendar; bake final (`nla.bake` com visual keying) antes de exportar para engine.
- FPS do projeto = FPS do destino antes de animar (Blender padrão 24 ✔; GTA e maioria dos jogos 30; Unreal aceita qualquer, 30 comum).

## Mocap e retarget

- Fontes: Mixamo (FBX), BVH, mocap por vídeo (ver ai-3d-tools.md). Skill `blender-motion-capture` (se instalada) cobre import e limpeza.
- Retarget: mapear ossos por nome, alinhar rest pose (T vs A) antes, copiar rotações em espaço local e posição só da raiz/pelve escalada pela altura.
- Limpeza obrigatória: filtro de jitter (Graph Editor > Smooth/Butterworth), travar pés, corrigir penetração no chão, remover rotação de raiz indesejada.

## Shape keys / facial

- Shape keys com nomes do padrão do destino (ARKit 52 para Apple/MetaHuman/VRM; visemes para lip sync).
- Corretivas acionadas por driver na rotação do osso.
- Export: FBX/glTF exportam shape keys como morph targets; modificadores antes do Armature impedem shape key no export — aplique-os ou mantenha só Armature.
