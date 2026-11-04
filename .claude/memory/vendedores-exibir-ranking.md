---
name: vendedores-exibir-ranking
description: "Ranking de Vendedores e Resumo do Dia leem vendas.\"Vendedores\" WHERE \"ExibirRanking\" (com Foto do banco) desde 04/11/2026; VENDEDORES_TABELA virou só fallback de foto"
metadata:
  node_type: memory
  type: project
  originSessionId: 9ea10fa7-d302-45eb-8337-882204884d8d
  modified: 2026-11-04T17:09:52.682Z
---

Desde 04/11/2026 (commit d5d3589, em produção), quem aparece no Ranking de Vendedores e nos cards de Vendedores do Resumo do Dia vem de `get_vendedores_ranking()` em `dashboard/panels.py`: SQL direto em `vendas."Vendedores" WHERE "ExibirRanking"`, o mesmo critério do `relatorios`, com Curto, Percentual e Foto (PNG em bytea). O checkbox "Exibir no Ranking" fica na tela Vendedores da app Vendas. A lista fixa `VENDEDORES_TABELA` ficou só como fallback de foto (`imagens/fotos/<id>`). Totais e metas continuam somando todas as vendas.

**Why:** o usuário pediu o mesmo critério de exibição da Vendas. A lista fixa exigia commit a cada renomeação ou vendedor novo (ex.: Diney → Valdiney).

**How to apply:** ao mexer em vendedor ou ranking, não voltar a usar a lista fixa nem adicionar `exibir_ranking`/`foto` ao model `managed=False` (geraria migração — regra 08); manter o SQL direto. Para ocultar ou mostrar um vendedor, o caminho é a app Vendas, não o código. Ver [[projeto_dashboard_visao_geral]] e [[migracao_oficial_db_dashboard]].

Realizado em Note_Oficial via Claude Code.
