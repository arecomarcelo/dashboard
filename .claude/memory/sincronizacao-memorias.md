---
name: sincronizacao-memorias
description: Dashboard tem sync de memórias via .githooks desde 05/10/2026 — checar canônico x repo antes do 1º commit em máquina nova
metadata:
  node_type: memory
  type: project
  originSessionId: 13266d95-7b49-4e18-a05a-cb8f3d2267c2
  modified: 2026-10-05T23:56:45.449Z
---

Sincronização de memórias configurada em 05/10/2026 (skill `com-sincronizar-memorias`), mesmo padrão do `cadastros`: `.githooks/{pre-commit,post-merge,post-checkout}` + `scripts/claude-sync-{push,pull}.sh`, espelho em `.claude/memory/`. Realizado em Note_Casa via Claude Code.

**Why:** o `pre-commit` copia o canônico (`~/.claude/projects/-home-areco-Projetos-Oficial-dashboard/memory/`) por cima do repo; se o canônico da máquina estiver defasado (hook sem +x ou `core.hooksPath` não ativado), o primeiro commit trunca o `MEMORY.md` do repo — já aconteceu em estoque e gestor-imagem.

**How to apply:** em cada máquina, rodar uma vez `git config core.hooksPath .githooks` e `bash scripts/claude-sync-pull.sh`; antes do primeiro commit numa máquina nova, comparar canônico x `.claude/memory/` e copiar repo → canônico se o canônico for subconjunto. Hooks devem estar versionados como 100755.
