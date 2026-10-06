---
name: ambiente-local-banco
description: Dashboard local lê o espelho sga_backup (sga_db_local:5440); como reclonar só as 12 tabelas de produção sem quebrar FKs/views
metadata:
  node_type: memory
  type: project
  originSessionId: 13266d95-7b49-4e18-a05a-cb8f3d2267c2
  modified: 2026-10-06T00:06:54.960Z
---

Produção lê o `sga` nativo da Hostinger (DB_HOST=host-postgres). Localmente o `.env` aponta para o espelho `sga_backup` no container `sga_db_local` (localhost:5440, usuário postgres — mesma senha local do `.env` do cadastros), com DEBUG=True e SECRET_KEY própria. Nenhum segredo de produção no `.env` local. Configurado em 05/10/2026 — Realizado em Note_Casa via Claude Code.

Clone Produção → Local das 12 tabelas do app (Dashboard, Dashboard_Config, Dashboard_Log, Vendas, VendaProdutos, Vendedores, Produtos, VendasSituacao, VendaConfiguracao, RPA, RPA_Atualizacao, Log): `ssh root@195.200.1.244 "sudo -u postgres pg_dump -d sga -Fc --data-only -t '\"public\".\"<T>\"' ..."` → `pg_restore -f -` → SQL com `SET session_replication_role = replica; DELETE FROM` das 12 → `psql -1 -v ON_ERROR_STOP=1`.

**Why:** outras tabelas do `sga_backup` têm FK para Produtos/RPA/Vendas (ComexPoliticaReposicao, EntradaProdutos, VendaPagamentos...) e há views (`vw_total_vendas`, `vw_levantamento_vendas`) — `--clean`/DROP ou TRUNCATE quebrariam o espelho. FK real de VendaProdutos é `Venda_ID → Vendas.ID_Gestao` (não `id`).

**How to apply:** antes de reclonar, conferir que as colunas prod x local são idênticas (information_schema.columns); validar depois por contagem por tabela. Alternativa ampla: skill `of-clonar-banco-sga` (Clonagem Geral). Aliases `rodar/predeploy/deploy-dashboard` apontam para `~/Projetos/Oficial/dashboard` (antes apontavam para `Oficial-Antigos/sgd`).
