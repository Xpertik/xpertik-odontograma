# Skill Registry — xpertik-odontograma

Skills available for this project. Sub-agents receive pre-resolved paths from the orchestrator.

## SDD workflow skills

| Skill | Path | Triggers on |
|-------|------|-------------|
| sdd-init | `/home/jhonatan/.claude/skills/sdd-init/SKILL.md` | Project bootstrap |
| sdd-explore | `/home/jhonatan/.claude/skills/sdd-explore/SKILL.md` | Exploration phase |
| sdd-propose | `/home/jhonatan/.claude/skills/sdd-propose/SKILL.md` | Create proposal |
| sdd-spec | `/home/jhonatan/.claude/skills/sdd-spec/SKILL.md` | Write specifications |
| sdd-design | `/home/jhonatan/.claude/skills/sdd-design/SKILL.md` | Technical design |
| sdd-tasks | `/home/jhonatan/.claude/skills/sdd-tasks/SKILL.md` | Task breakdown |
| sdd-apply | `/home/jhonatan/.claude/skills/sdd-apply/SKILL.md` | Implementation |
| sdd-verify | `/home/jhonatan/.claude/skills/sdd-verify/SKILL.md` | Validation |
| sdd-archive | `/home/jhonatan/.claude/skills/sdd-archive/SKILL.md` | Completion |

## Project-relevant coding skills

| Skill | Path | Triggers on |
|-------|------|-------------|
| engram:memory | `/home/jhonatan/.claude/skills/engram/memory/SKILL.md` | ALWAYS — persistent memory protocol |
| skill-creator | `/home/jhonatan/.claude/skills/skill-creator/SKILL.md` | Creating new skills (unlikely in this project) |

## Project conventions

- Global user instructions: `/home/jhonatan/.claude/CLAUDE.md`
- Project contexto: `/home/jhonatan/trunk/xpertik/xpertik-odontograma/contexto.md`

## Persistence backend

- **Mode**: engram
- **Project name**: `xpertik-odontograma`
- **Topic key prefix for SDD artifacts**: `sdd/<change-name>/<artifact>`
- **Project context key**: `sdd-init/xpertik-odontograma` (already saved)
