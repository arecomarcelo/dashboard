---
title: Auditoria de Fidelidade — DashBoard
description: Auditoria de Qualidade de Código e Segurança do DashBoard (skill com-auditoria-final, escopo adaptado)
version: 1.0.0
status: Oficial
owner: Oficial Sport
authors:
  - Marcelo Areco
created: 2026-08-17
updated: 2026-08-17
---

## Auditoria — 17/08/2026 (Realizado em Note_Oficial via Claude Code)

> **Legado:** Não aplicável no sentido usual (extração 1:1 de um módulo do SGA
> monólito). O DashBoard importa painéis do **SGR** (Sistema de Gestão de
> Relatórios, app Streamlit separada, `/media/.../Projetos/sgr`), não do `sga`
> monólito — arquitetura diferente das demais apps do ambiente oficial. Auditoria
> restrita a Qualidade de Código e Segurança, mesmo escopo já usado no
> `monitor-rpa` (outra app sem equivalente no legado).

**Contexto técnico real:** apesar de ter `manage.py`/`app/settings.py` (Django) e
`dashboard/` (app Django com `models.py`/`views.py`/`urls.py`/`templates/`), a app
é uma **aplicação Streamlit** de verdade — `Dockerfile`/`entrypoint.sh` só rodam
`streamlit run app.py` (porta 8113). Django é usado só como ORM (`django_setup.py`),
nunca serve HTTP em produção. Todas as tabelas de negócio (`Vendas`, `Vendedores`,
`Dashboard`, `Dashboard_Config`, `VendaConfiguracao`, etc.) são `managed=False`,
conectadas direto ao banco nativo do legado `sga` (não ao `sga_multiapp`).

### Achados

| # | Severidade | Achado |
|---|---|---|
| 1 | **CRÍTICA** | A tela "Gerenciar" (`pages/02_⚙️_Gerenciar.py`) — que edita Meta de Vendas, percentuais de Vendedores, Mensagem dinâmica e Ordem/Duração de exibição — **não tem nenhuma autenticação**. Confirmado ao vivo: `https://dashboard.oficialsport.com.br/Gerenciar` responde `200` sem login, para qualquer pessoa com o link. |
| 2 | ALTA | 4 blocos `except:` genéricos em `dashboard/panels.py` (`parse_valor`, `parse_quantidade`, filtro de vendas, busca de Meta) engoliam qualquer erro e caíam silenciosamente para `Decimal("0")`/pulavam o registro — um bug real (dado malformado, falha de conexão) apareceria como métrica zerada na tela pública, sem log/alerta nenhum. |
| 3 | ALTA | Zero testes automatizados — `dashboard/tests.py` era o stub padrão vazio do `startapp`. |
| 4 | MÉDIA | As 6 gravações (`.save()`) da tela "Gerenciar" não tinham Log Duplo (nem banco, nem sistema) — regra 11 do CLAUDE.md — nenhum rastro de quem alterou o quê. |
| 5 | BAIXA | `datetime.now()` sem timezone em 2 pontos de `panels.py` (`get_filtros_periodo`, `render_ranking_vendedores`) — funcionava só porque o container define `TZ=America/Sao_Paulo` no SO; frágil e fora do padrão do projeto (`timezone.localdate()`/`localtime()`). |
| 6 | BAIXA | `DEBUG = True` fixo em `app/settings.py`, sem controle por `.env` — hoje inofensivo (Django nunca serve HTTP em produção), mas bomba-relógio se isso mudar. `ALLOWED_HOSTS = []` (mesmo risco, mesma causa). |
| 7 | Informativo | `dashboard/views.py`/`urls.py`/`templates/dashboard/slideshow.html` existem e estão registrados em `app/urls.py`, mas nunca são servidos em produção — remanescente de uma versão anterior do projeto (slideshow em Django/JS puro, antes da migração para Streamlit). |

### Correções Aplicadas — 17/08/2026

| # | Decisão do usuário | Correção |
|---|---|---|
| 1 | **"Deixe como está"** — autenticação não foi implementada por decisão explícita do usuário | Nenhuma correção de código. Mitigado parcialmente pelo item 4 (toda gravação agora fica registrada em `Log`, mesmo sem identificar o autor real — grava o identificador fixo `"Dashboard (sem autenticação)"`, deixando a limitação explícita no próprio log). **Risco permanece aberto por decisão consciente, registrado aqui para referência futura.** |
| 2 | Corrigir agora | `except:` genéricos trocados por exceções específicas (`InvalidOperation`/`ValueError`/`TypeError` nos parsers; `AttributeError`/`TypeError` no filtro de vendas; `Exception` só na busca de Meta, por ser acesso a banco) — todos agora logam via `erro_logger` antes do fallback. `LOGGING` adicionado a `app/settings.py` (mesmo padrão `admin_logger`/`erro_logger` do resto do ecossistema; `logs/` criado). |
| 3 | Corrigir agora | `dashboard/tests.py`: 12 testes novos para as funções puras de `panels.py` (`parse_valor`, `parse_quantidade`, `format_currency`, `get_filtros_periodo`) e para `dashboard/services.py::registrar_log` — cobrem os casos de entrada inválida (regressão do achado #2) e confirmam que a falha ao logar nunca propaga. Escopo não inclui os models `managed=False` (fora do padrão de teste automatizado já aceito em `comex`/`monitor-rpa` para apps ligadas direto ao legado). |
| 4 | Corrigir agora | `dashboard/models.py` ganhou o model `Log` (mesma tabela/estrutura `Log` do legado `sga`, já usada em todo o ecossistema oficial). `dashboard/services.py::registrar_log` criado (Log Duplo — banco + `admin_logger`). As 6 gravações de `pages/02_⚙️_Gerenciar.py` (Meta, Vendedor, Mensagem, toggle Ativo, Ordem/Duração) chamam `registrar_log` logo após o `.save()`. |
| 5 | Corrigir agora | `get_filtros_periodo`/`render_ranking_vendedores` trocados para `django.utils.timezone.localdate()`. |
| 6 | Corrigir agora | `DEBUG`/`ALLOWED_HOSTS` passam a ler de `.env` (default seguro: `DEBUG=False`, `ALLOWED_HOSTS=localhost,127.0.0.1`) — confirmado que a produção não tinha essas variáveis no `.env`, então o novo default seguro já se aplica automaticamente no próximo deploy. `.env.example` atualizado. |
| 7 | Corrigir agora (documentar, sem remover) | Comentário adicionado no topo de `dashboard/urls.py` explicando que as rotas nunca são servidas em produção — decisão consciente de não remover nesta sessão (fora do escopo de uma auditoria de qualidade tocar em arquitetura). |

**Validação:** `manage.py check` limpo em todas as etapas. Testes novos não puderam ser
executados nesta sessão a partir do Note_Oficial (`.env` local aponta direto para o
Postgres nativo de produção, `195.200.1.244:5432`, e a autenticação falhou a partir
desta rede — limitação de ambiente pré-existente, não causada por esta auditoria; ver
[[rotacao_senha_legado_ago2026]]). Compatibilidade do novo model `Log` validada via
`INSERT`/`ROLLBACK` direto no Postgres nativo da VPS (SSH), confirmando que a
estrutura do model bate exatamente com a tabela real. Validação funcional completa
feita após o deploy (ver `documentacao/Ajustes.md`).

### Resultado

CRÍTICAS: 1 (mantida aberta por decisão do usuário) · ALTAS: 0 (2 corrigidas) ·
MÉDIAS: 0 (1 corrigida) · BAIXAS: 0 (2 corrigidas) · 1 informativo (documentado, sem
remoção). **Único item aberto é a CRÍTICA de autenticação — risco aceito
conscientemente pelo usuário, não uma falha não tratada.**
