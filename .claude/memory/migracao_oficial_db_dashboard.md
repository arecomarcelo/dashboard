---
name: migracao-oficial-db-dashboard
description: DashBoard roda sobre o oficial_db em produção desde o corte da Onda 3 (08/10/2026 15:11) — role dashboard_user, schema dashboard; rollback documentado
metadata:
  type: project
---

Em 08/10/2026 (sessão do guarda-chuva multi-aplicacao) o DashBoard foi migrado do legado `sga` para o `oficial_db` no **branch `migracao-oficial-db`** — etapa 28 do `Plano de Implementação - Migração RPA para Oficial DB` (multi-aplicacao). `master` continua lendo o legado e é o que está em produção.

- Tabelas próprias `Dashboard`/`Dashboard_Config`/`Dashboard_Log` no novo schema `dashboard` (`managed=True`); migrations 0001–0004 da época do legado trocadas por uma `0001_initial` limpa (autorizado pelo usuário).
- Vendas/itens/meta/vendedores/situações lidos de `vendas.*` (dona: app vendas); produtos de `compartilhado."Produtos"`; rodapé de atualização de `rpa."ControleAtualizacao"` (por `fim`, RPA 7); Log em `compartilhado."Log"` (`Modulo=dashboard`, sem `Hora`).
- `DB_SCHEMA=dashboard`, `stack.yml` na `oficial_db_net` sem `extra_hosts`, `migrate dashboard` no entrypoint.
- Configuração existente (meta, vendedores, painéis) chega por cópia única do legado no corte: `multi-aplicacao/scripts/carga_configuracao_dashboard.sh`.

**Corte feito em 08/10/2026 (15:11):** merge no `master` (`c2b2ed5`) e deploy. Role `dashboard_user` (dona do schema `dashboard`; senha gerada na VPS e guardada só no `.env` de lá), configuração copiada do legado (6 painéis, 12 vendedores, Meta). Rollback: `.env.bak-pre-corte-20261008-1510` + imagem `sha256:82188bf7…`. O branch `migracao-oficial-db` está superado.

**Why:** a Onda 3 desliga a escrita no legado; o dashboard precisa estar no oficial antes disso, mas só pode ser publicado no corte (etapa 32).

**How to apply:** produção já lê só o `oficial_db`; nunca reapontar para o legado `sga` (escrita nele foi desligada no corte). Toda tabela nova do dashboard vai no schema `dashboard` (migration própria). O `.env` local aponta para o legado de PRODUÇÃO — para testar o branch, exportar `DB_*` do `oficial_db` local (load_dotenv não sobrescreve variáveis já definidas).

Realizado em Note_Oficial via Claude Code.
