# GTA V / FiveM: animação (YCD)

Pipeline testado em produção (Blender 5.3 + Sollumz 2.9 + CodeWalker 30 dev48):

```
esqueleto do ped (mp_m_freemode_01) → Action no Blender → Clip Dictionary do Sollumz → .ycd.xml (CW XML)
→ CodeWalker.Core converte → .ycd → stream/ do resource → RequestAnimDict + TaskPlayAnim
```

## Esqueleto

- Importe um ped vanilla (`mp_m_freemode_01` / `mp_f_freemode_01`) com Sollumz; não crie esqueleto próprio.
  Sollumz tem atalho de preferências para o esqueleto externo do freemode (`prefs_external_skeleton_path_add_mp_freemode` ✔).
- Freemode: ~128 ossos (SKEL_*, IK_*, RB_* roll, MH_*, FB_* faciais). Não renomeie nem reestruture.
- Tags (usadas em `GetPedBoneIndex`) ✔: SKEL_ROOT 0 · SKEL_Pelvis 11816 · SKEL_Spine3 24818 · SKEL_Neck_1 39317 ·
  SKEL_Head 31086 · SKEL_L_Hand 18905 · SKEL_R_Hand 57005 · PH_L_Hand 60309 · PH_R_Hand 28422 ·
  SKEL_L_Foot 14201 · SKEL_R_Foot 52301 · IK_Head 12844. Lista completa: `tools/BoneProperties.xml` do Sollumz.
- Convenção no espaço do armature: frente do ped = −Y, esquerda = +X, cima = +Z, chão ≈ z −1.0.

## Preparar a Action

- Rotation mode **QUATERNION** em todos os ossos animados (Sollumz faz isso no setup de animação).
- Copy Rotation de `RB_L_ThighRoll`/`RB_R_ThighRoll` para as coxas: o jogo calcula esses ossos por expressão (.yed) que o
  Sollumz não suporta; sem isso a perna deforma.
- **30 fps**. Duração = frames/30.
- Trilha de raiz: posição (track type 0) e rotações dos ossos (type 1). Clip estacionário: mantenha a raiz parada; deslocamento real usa o mover/root motion — teste no jogo.
- Bake final (visual keying) com interpolação suavizada; picos de aceleração angular viram "tremida" no jogo.

## Autorar por script (padrão testado)

- Pose = rotações por osso em eixos de mundo da pose de descanso, convertidas para local:
  `q_local = R.inverted() @ q_mundo @ R`, com `R = bone.matrix_local.to_quaternion()`.
- Entre poses-chave: `slerp` com **continuidade de sinal** (se `q_anterior.dot(q) < 0`, use `-q`), senão o osso gira 360° no meio.
- Easing por segmento (smoothstep/in/out) e **keyframe em todos os frames** (`keyframe_insert("rotation_quaternion", frame=f, group=osso)`):
  o jogo amostra o clip, não interpola como o Blender.
- Raiz (`SKEL_ROOT`) só `location`; converta de mundo para o espaço do osso com `R.to_matrix().inverted() @ v`.
- Correção de chão: por frame, menor Z dos vértices avaliados do corpo; suba a raiz só o necessário (tolerância ~1,5 cm) e
  suavize a correção numa janela de 2 frames (dilatar + média) para não tremer.
- F-curves no 5.x: `[fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]` ✔ (`action.fcurves` não existe mais).

## Exportar (testado: Blender 5.3 + Sollumz 2.9 + CodeWalker 30 dev48)

```bash
blender -b cena.blend --python scripts/gta_ycd_export.py -- --armature mp_m_freemode_01 --dict meu_dict --clip meu_clip=MinhaAction --out C:/tmp/anim
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/ycdconv.ps1 xml2ycd C:/tmp/anim/meu_dict.ycd.xml C:/tmp/anim/meu_dict.ycd -CodeWalker D:/CodeWalker
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/ycdconv.ps1 ycd2xml C:/tmp/anim/meu_dict.ycd C:/tmp/anim/rt.ycd.xml -CodeWalker D:/CodeWalker
```
Teste real: Action de 61 frames → XML 36,9 KB → `.ycd` 1,8 KB → ida e volta com `FrameCount 61`, `Duration 2`, `pack:/meu_clip.clip`.

- O script faz o que o painel do Sollumz faz, via API ✔: `ycdimport.create_clip_dictionary_template(nome)` → objetos Animation/Clip
  (`create_anim_obj(SollumType.ANIMATION/CLIP)`), `animation_properties` (`hash`, `target_id_type="ARMATURE"`, `target_id`, `action`),
  `clip_properties` (`hash`, `name="x.clip"`, `duration = frames/30`, `animations.add()` com `start_frame`/`end_frame`),
  `ycdexport.export_ycd(cd, caminho)` → bool. **Defina o alvo antes da action**, senão o update do Sollumz dispara "bone-map is required".
- Também checa: canais `rotation_euler` (GTA usa quaternion), ossos inexistentes, fps ≠ 30.
- YCD usa o caminho de export legado do Sollumz ✔ (fora do ExportBundle que gera Native): sai `.ycd.xml`, por isso a conversão.
- Painel equivalente: `create_clip_dictionary` ✔, `animations_set_target` ✔, `anim_apply_nla` ✔ (prévia de clip composto).
- Nome do clip ≠ nome do arquivo: o dicionário é o arquivo (`meu_dict.ycd`), o clip é o hash dado no Sollumz (`meu_clip`).
- `ycdconv.ps1` precisa do Windows PowerShell 5.1 (`powershell.exe`, não `pwsh`) para carregar o `CodeWalker.Core.dll`.

## FiveM

- Coloque o `.ycd` em `stream/`; nenhum data_file necessário.
- Lua (client):
  ```lua
  RequestAnimDict('meu_dict')
  while not HasAnimDictLoaded('meu_dict') do Wait(0) end
  TaskPlayAnim(PlayerPedId(), 'meu_dict', 'meu_clip', 8.0, -8.0, -1, flags, 0.0, false, false, false)
  RemoveAnimDict('meu_dict') -- quando não for mais usar
  ```
  Flags comuns (bitmask; confira na página TASK_PLAY_ANIM do docs.fivem.net): 1 loop, 2 parar no último frame,
  16 só parte superior, 32 permitir controle do jogador. Combine somando (49 = 1+16+32).
- Prop na mão: `AttachEntityToEntity(prop, ped, GetPedBoneIndex(ped, 57005), x, y, z, rx, ry, rz, true, true, false, true, 1, true)` (57005 = mão direita).

## Referência a partir de animação do jogo

Extraia o `.ycd` vanilla (OpenIV/CodeWalker), converta para XML e importe no Sollumz como referência de timing e poses.
Amostrar frame a frame e reaplicar no seu clip dá movimento com "cara de GTA" melhor que mocap genérico.

## Checagens antes de mandar para o jogo

- Pés: Z dos pés no apoio constante (variação < 1 cm); sem atravessar o chão.
- Pico de aceleração angular por frame: compare antes/depois do smoothing; picos isolados = tremida.
- Contact sheet de 8–12 frames (`review_render.py` ou render da câmera) lido antes de exportar.
- Teste no jogo: em pé, em movimento (flag 16/32), em rampa, com prop anexado.
