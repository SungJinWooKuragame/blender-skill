# blender-skill

Skill para [Claude Code](https://claude.com/claude-code) de produção 3D profissional no Blender 5.x.

`blender-3d-production`: modelagem e topologia, UV/bake/PBR, visual premium (logos, produto), rig e animação,
Geometry Nodes, simulação/VFX, otimização, malhas geradas por IA, e pipelines para GTA V/FiveM com Sollumz
(props, veículos, colisão, interiores MLO, roupas, animação YCD), Unreal, Unity, Godot e Minecraft.
APIs conferidas por introspecção no Blender 5.3 e no código do Sollumz 2.9.

## Instalação

### skills CLI (um comando)

```bash
npx skills add SungJinWooKuragame/blender-skill -g -a claude-code -y
```

Atualizar depois:

```bash
npx skills update -g
```

### Plugin do Claude Code

```
/plugin marketplace add SungJinWooKuragame/blender-skill
/plugin install blender-skill@blender-skill
```

### Manual

Copie `skills/blender-3d-production` para `~/.claude/skills/`.

## Requisitos

- Blender 5.2+ (testado no 5.3). Execução ao vivo via [blender-mcp](https://github.com/ahujasid/blender-mcp) ou headless (`blender -b`).
- GTA V/FiveM: [Sollumz](https://docs.sollumz.org) 2.9 e CodeWalker.

## Uso

A skill ativa sozinha em pedidos de 3D ("modela um logo 3D premium", "exporta esse prop pro FiveM", "anima esse ped").
Chamada direta: `/blender-3d-production`.

```bash
blender -b cena.blend --python skills/blender-3d-production/scripts/qa_report.py -- --objects MeuObjeto
```

## Estrutura

```
skills/blender-3d-production/
├── SKILL.md                    # regras, roteamento e ciclo de qualidade
├── references/                 # 13 especialidades, carregadas só quando a tarefa pede
│   ├── bpy-api-5x.md           ├── modeling-topology.md     ├── uv-baking-texturing.md
│   ├── lookdev-render.md       ├── rigging-animation.md     ├── gta-assets.md
│   ├── gta-maps-mlo.md         ├── gta-animation.md         ├── game-engines.md
│   ├── procedural-sim-vfx.md   ├── optimization.md          ├── ai-3d-tools.md
│   └── sources.md
└── scripts/
    ├── qa_report.py            # auditoria só-leitura: tris, non-manifold, escala, UV, color space
    ├── review_render.py        # 4 ângulos EEVEE para revisão; restaura a cena
    ├── logo_studio.py          # estúdio de logo/produto premium (Cycles + AgX) em cena separada
    ├── gta_ycd_export.py       # Actions → Clip Dictionary do Sollumz → .ycd.xml
    └── ycdconv.ps1             # .ycd.xml ⇄ .ycd via CodeWalker.Core (PowerShell 5.1)
```

## Licença

MIT
