---
name: projeto-dashboard-visao-geral
description: "O que é o DashBoard (ex-SGD), como se conecta ao banco legado sga, e o gotcha recorrente de tipos de coluna mudando sem aviso em models managed=False"
metadata: 
  node_type: memory
  type: project
  originSessionId: bf6a3b75-8a84-43d4-b0f6-acff6e8b5d69
---

Realizado em Note_Oficial via Claude Code.

O **DashBoard** (ex-SGD, Sistema de Gestão de Dashboard — renomeado em 27/07/2026, ver [[rename_sgd_dashboard]]), em `/media/areco/Backup/Oficial/Projetos/nova-estrutura/dashboard`, é uma app Django 5.2 + Streamlit que exibe painéis de vendas (Meta Mês, Métricas de Vendas, Ranking Vendedores, Ranking Produtos, **Resumo Dia** — adicionado em 27/07/2026) em formato de slideshow rotativo (ex.: TVs de loja). Não tem tela de login/banner "Em Desenvolvimento" — é puramente um visualizador.

**Testar novo painel sem afetar produção**: como o banco `sga` é compartilhado com a produção (Docker Swarm lê a mesma tabela `Dashboard_Config` ao vivo), inserir um `Dashboard`/`Dashboard_Config` com `Ativo=True` ou mudar a `Ordem` de um já existente aparece na TV real em segundos — não é um teste "só local". Para prévia visual isolada, criar um script standalone temporário (`import django_setup; from dashboard.panels import render_X; render_X()` rodado via `streamlit run` numa porta livre) que só faz leitura, sem tocar `Dashboard_Config`. As tabelas `Dashboard`/`Dashboard_Config` têm sequência de ID (`Dashboard_id_seq`/`Dashboard_Config_id_seq`) dessincronizada (dados originais inseridos fora do ORM) — sempre rodar `setval(pg_get_serial_sequence(...), (SELECT MAX(id)+1 ...))` antes de inserir via Django ORM, senão `IntegrityError: duplicate key`.

**Painéis novos ficam cobertos pelo rodapé fixo do slideshow**: o script de auto-resize de `pages/01_🎬_Slideshow.py` (que encolhe o iframe do painel para caber acima do rodapé) nem sempre aplica a tempo — painéis com `height: 100vh` maiores que o espaço realmente disponível ficam com conteúdo por baixo do rodapé. Preferir altura fixa em px (ver `render_resumo_dia`, 720px) em vez de confiar no resize.

Diferente das apps `multi-*` do ecossistema **oficial** (que usam o banco compartilhado `sga_multiapp`/`sga_db_local`), o DashBoard conecta **diretamente no banco legado monolítico `sga`** (VPS Hostinger, `DB_HOST` em `.env`) e lê as tabelas `Vendas`, `VendaProdutos`, `Vendedores`, `Produtos`, `VendasSituacao` via models Django com `managed = False` (só leitura, sem gerar migração — regra 08 do CLAUDE.md global).

**Gotcha recorrente**: como o DashBoard não controla o schema dessas tabelas, mudanças de tipo de coluna feitas direto no Postgres (ex.: `character varying` → `date` ou `bigint`) não avisam o Django. Os models continuam declarando `CharField` e o ORM passa a devolver tipos nativos (`datetime.date`, `int`) em vez de string, quebrando qualquer lógica que faça `.strip()`/`.split("/")` no valor. Isso já aconteceu pelo menos duas vezes (commit "Ajuste Modelos Alteração Tipo de Campos" em 11/05/2026, e de novo em 17/07/2026 nas tabelas `Vendas`/`VendaProdutos` — colunas `Data`, `PrazoEntrega`, `ID_Gestao`, `Venda_ID`).

**Como aplicar**: sempre que o dashboard aparecer zerado sem erro visível, suspeitar primeiro de descompasso entre o tipo declarado no model (`CharField`/`IntegerField`) e o tipo real da coluna no banco — verificar com `information_schema.columns` antes de investigar a lógica de negócio. `dashboard/panels.py` tem `except: continue` silenciosos em `get_vendas_periodo()` que mascaram esse tipo de erro.

**Infraestrutura de produção (atípica para o ambiente Oficial)**: não usa NPM nem o fluxo padrão das apps `multi-*` — deploy via Docker Swarm (`stack.yml`, `docker stack deploy dashboard`, serviço `dashboard_web`) na VPS Hostinger `195.200.1.244` (clone em `/home/deploy/apps/dashboard`), atrás de um vhost OpenLiteSpeed real (porta 443) já chamado `dashboard`, que faz proxy para o container publicado em `127.0.0.1:8113` com os 3 ajustes de WebSocket documentados em `documentacao/deploy/vhost_dashboard_oficialsport.conf` (sem eles o slideshow trava em loading infinito). Traefik roda internamente (rede `traefik_public`, TLS interno) mas não é o que recebe tráfego público real. Sem volumes/banco próprio no stack — sem risco de dados numa migração de nome de stack (já migrada em 27/07/2026, ver [[rename_sgd_dashboard]]).

Não tem documento de Planejamento com % Desenvolvido (`GERAL`) — mesma natureza do SGR (sistema legado já em produção, fora da esteira de extração SGA e do protocolo de % Desenvolvido de projetos novos). Não registrado em `apps.conf`/`Score Implantacao.md` (exclusivos do Score centralizado hauxtech/oficial).
