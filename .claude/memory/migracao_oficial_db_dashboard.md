---
name: migracao-oficial-db-dashboard
description: DashBoard migrado para o oficial_db no branch migracao-oficial-db (etapa 28 do plano de migração RPA, 08/10/2026) — não publicar antes do corte coordenado da Onda 3
metadata:
  type: project
---

Em 08/10/2026 (sessão do guarda-chuva multi-aplicacao) o DashBoard foi migrado do legado `sga` para o `oficial_db` no **branch `migracao-oficial-db`** — etapa 28 do `Plano de Implementação - Migração RPA para Oficial DB` (multi-aplicacao). `master` continua lendo o legado e é o que está em produção.

- Tabelas próprias `Dashboard`/`Dashboard_Config`/`Dashboard_Log` no novo schema `dashboard` (`managed=True`); migrations 0001–0004 da época do legado trocadas por uma `0001_initial` limpa (autorizado pelo usuário).
- Vendas/itens/meta/vendedores/situações lidos de `vendas.*` (dona: app vendas); produtos de `compartilhado."Produtos"`; rodapé de atualização de `rpa."ControleAtualizacao"` (por `fim`, RPA 7); Log em `compartilhado."Log"` (`Modulo=dashboard`, sem `Hora`).
- `DB_SCHEMA=dashboard`, `stack.yml` na `oficial_db_net` sem `extra_hosts`, `migrate dashboard` no entrypoint.
- Configuração existente (meta, vendedores, painéis) chega por cópia única do legado no corte: `multi-aplicacao/scripts/carga_configuracao_dashboard.sh`.

**Why:** a Onda 3 desliga a escrita no legado; o dashboard precisa estar no oficial antes disso, mas só pode ser publicado no corte (etapa 32).

**How to apply:** não fazer merge/deploy do branch antes da etapa 32 (pré-requisitos: role, schema, grants e `.env` da VPS, listados na etapa 32 do plano). O `.env` local aponta para o legado de PRODUÇÃO — para testar o branch, exportar `DB_*` do `oficial_db` local (load_dotenv não sobrescreve variáveis já definidas).

Realizado em Note_Oficial via Claude Code.
