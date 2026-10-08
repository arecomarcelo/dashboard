---
name: rename-sgd-dashboard
description: "Histórico do ajuste de nome SGD → DashBoard (27/07/2026): pasta, repositório GitHub, produção Docker Swarm e decommission do Streamlit Community Cloud"
metadata:
  node_type: memory
  type: project
---

Realizado em Note_Oficial via Claude Code, 27/07/2026, via skill `ajustar-nome-app` (escopo Completo).

**O que mudou:**
- Pasta local: `/media/areco/Backup/Oficial/Projetos/sgd` → `/media/areco/Backup/Oficial/Projetos/nova-estrutura/dashboard`
- Repositório GitHub: `arecomarcelo/sgd` → `arecomarcelo/dashboard`
- Produção (VPS `195.200.1.244`): stack Docker Swarm `sgd` → `dashboard` (serviço `dashboard_web`), imagem `ghcr.io/arecomarcelo/dashboard:latest`, clone em `/home/deploy/apps/dashboard`
- Domínio/vhost OpenLiteSpeed **não mudaram** — já nasceram como `dashboard`/`dashboard.oficialsport.com.br` antes deste rename, então não houve provisionamento novo de vhost/SSL

**O que NÃO mudou (levantado antes de agir, ver [[projeto-dashboard-visao-geral]]):**
- Banco de dados: sem schema/`DB_SCHEMA` dedicado, conecta direto no `sga` (schema `public`) — Passo 3 da skill não se aplicou
- Não é app da esteira de extração SGA — não está em `apps.conf`/`Score Implantacao.md`/`prometheus.yml` do `multi-aplicacao` — Passo 9 da skill não se aplicou
- Nenhum alias de shell existia em `~/.zshrc`/`~/.bashrc` nesta máquina (Note_Oficial) apontando para os scripts do projeto — Passo 8 sem ação

**Achado fora do levantamento inicial do Passo 1:** a app tinha um segundo deploy paralelo no **Streamlit Community Cloud** (share.streamlit.io, app "sgd", subdomínio `oficialsport-slideshow`), não coberto pelos itens padrão da skill (que assume NPM, não Docker Swarm nem Streamlit Cloud). A UI do Streamlit Cloud não permite editar o repositório de um app existente — só excluir e recriar. O usuário confirmou que o mesmo tratamento já dado ao **SGR** (app irmã "relatórios", cujo Streamlit Cloud já não existe mais na conta) se aplica aqui: **excluído sem recriar**, já que a produção real é 100% Docker Swarm.

**Como aplicar em renames futuros neste ambiente**: antes de assumir que Passo 7 (NPM) da skill `ajustar-nome-app` é o único ponto de "produção" a verificar, checar também: (1) se existe stack/serviço Docker Swarm com o nome antigo (`docker stack ls` na VPS), e (2) se existe um deploy paralelo no Streamlit Community Cloud para apps Streamlit — nenhum dos dois é coberto pelos passos padrão da skill (escritos pensando em NPM/containers Compose comuns).
