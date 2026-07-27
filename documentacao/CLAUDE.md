# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto DashBoard (Sistema de Gestão de Dashboard)

Este é um projeto Django 5.2.2 que controla a exibição de Dashboards em formato de slides com transição automática.

### Integração com SGS (Sistema de Gestão de Relatórios)

O DashBoard importa e exibe painéis do **SGS - Sistema de Gestão de Relatórios**, uma aplicação Streamlit localizada em:
- **Localização**: `/media/areco/Backup/Oficial/Projetos/sgr`
- **Tipo**: Aplicação Streamlit (Python)
- **Comando de execução**: `streamlit run app.py`
- **Painéis**: Meta Mês, Métricas de Venda, Ranking Vendedores, Ranking Produtos

## Diretrizes de Codificação

### Princípios Fundamentais

1. **Revisão de Alterações**: Sempre revise suas alterações de modo a não alterar ou prejudicar a execução já implementada
2. **Idioma**: Sempre responder em Português do Brasil
3. **Listagem de Arquivos**: Sempre listar os nomes dos arquivos alterados
4. **Finalização**: Sempre finalize suas respostas com uma linha em branco `*** FINALIZADO ***`
5. **Histórico de Interações**: Ao finalizar uma interação, armazene no arquivo `Historico.md` (crie se não existir) na pasta `documentacao/`:
   - Dia (somente na primeira interação do dia) e a cada nova interação a Hora da Tarefa
   - O que foi pedido
   - Detalhamento da Solução ou Implementação
   - Lista de Arquivos Alterados ou Criados
   - Utilize emojis para tornar clara a compreensão
   - Utilize UTF-8 e o Fuso Horário Local
6. **MODELOS**: Os modelos já existem no banco de dados e **NÃO devem gerar migrações**
7. **NOVOS MODELOS**: Quando um modelo não existir, será informado como "Novo Modelo" na descrição e pedido para que seja implementado

### Organização de Arquivos

- Todos os documentos criados devem ser armazenados na pasta `documentacao/`
- Toda pasta ou arquivo criado deve estar dentro do domínio da aplicação (`/media/areco/Backup/Oficial/Projetos/nova-estrutura/dashboard/`)
- Jamais criar arquivos fora do domínio do projeto

## Estrutura do Projeto

- **app/**: Diretório principal do projeto Django
  - `settings.py`: Configurações do projeto (PostgreSQL)
  - `urls.py`: Configuração de rotas principais
  - `wsgi.py` e `asgi.py`: Servidores de aplicação
- **dashboard/**: App Django para gerenciamento de dashboards
  - `models.py`: Modelos Dashboard, Dashboard_Config e VendaAtualizacao
  - `admin.py`: Configuração do Django Admin
- **pages/**: Páginas Streamlit
  - `01_🎬_Slideshow.py`: Página principal de exibição de dashboards
  - `02_⚙️_Gerenciar.py`: Página de gerenciamento de dashboards
- **imagens/**: Imagens temporárias dos dashboards (será removido na Fase 3)
  - `meta_mes.png`
  - `metricas_de_vendas.png`
  - `ranking_vendedores.png`
  - `ranking_produtos.png`
- **documentacao/**: Documentação do projeto
  - `CLAUDE.md`: Este arquivo
  - `Historico.md`: Histórico de interações
  - `Planejamento_DashBoard.md`: Roadmap do projeto
- **venv/**: Ambiente virtual Python
- **app.py**: Aplicação principal Streamlit (auto-redirect para slideshow)
- **django_setup.py**: Configuração standalone do Django para Streamlit
- **requirements.txt**: Dependências do projeto (Django, Streamlit, psycopg2-binary, etc.)

## Comandos de Desenvolvimento

### Ambiente Virtual
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Desativar ambiente virtual
deactivate
```

### Execução da Aplicação

**Streamlit (Interface Principal)**
```bash
# Executar aplicação Streamlit na porta padrão do projeto
streamlit run app.py --server.port 8001

# A aplicação abre automaticamente na página de slideshow
# Acesso: http://localhost:8001
```

**Django Admin (Gerenciamento de Dados)**
```bash
# Executar servidor Django admin
python manage.py runserver

# Executar em porta específica
python manage.py runserver 8000

# Acesso ao admin: http://localhost:8000/admin
```

### Migrações de Banco de Dados
```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Ver status das migrações
python manage.py showmigrations
```

### Gerenciamento de Aplicações
```bash
# Criar nova aplicação Django
python manage.py startapp <nome_da_app>

# Criar superusuário
python manage.py createsuperuser
```

### Testes
```bash
# Executar todos os testes
python manage.py test

# Executar testes de uma app específica
python manage.py test <nome_da_app>

# Executar teste específico
python manage.py test <nome_da_app>.tests.<NomeDoTeste>
```

### Shell Django
```bash
# Abrir shell interativo do Django
python manage.py shell
```

## Configurações Importantes

- **Banco de Dados**: PostgreSQL
  - Database: `sga`
  - Host: `$DB_HOST`
  - Port: `5432`
  - User: `postgres`
- **Timezone**: America/Sao_Paulo
- **Linguagem**: pt-br
- **Debug Mode**: Atualmente ativado (desenvolvimento)
- **Porta Padrão**: 8001 (deixar 8000 livre conforme padrão do projeto)

## Estrutura do Banco de Dados

### Modelos Implementados:

**Dashboard:**
- Nome (CharField, 50 caracteres)
- Descricao (CharField, 255 caracteres)
- Ativo (BooleanField, default=True)

**Dashboard_Config:**
- Dashboard (ForeignKey)
- Ordem (IntegerField) - ordem de exibição
- Duracao (IntegerField) - duração em segundos

**VendaAtualizacao:** (tabela existente, managed=False)
- Data (CharField, 255 caracteres)
- Hora (CharField, 255 caracteres)
- Periodo (CharField, 255 caracteres)
- Inseridos (CharField, 255 caracteres)
- Atualizados (CharField, 255 caracteres)
- **Observação**: Tabela existente no banco, não gerenciada pelo Django

### Observações:
- Sempre verificar se um modelo já existe antes de criar migrações
- Modelos existentes não devem gerar novas migrações (ver Diretrizes de Codificação)
- Modelos com `managed = False` não criam/alteram tabelas no banco

## Funcionalidades Implementadas

### Interface Streamlit (Fase 2 - Concluída)

**Página de Slideshow (`pages/01_🎬_Slideshow.py`):**
- Auto-rotação de dashboards baseada em duração configurável
- Tela cheia sem distrações (sem header, footer, sidebar)
- Background preto para exibição profissional
- Transições suaves com fadeIn animation
- Exibição de imagens temporárias (será substituído por dashboards reais)
- Botão de engrenagem fixo (topo direito) para acessar gerenciamento
- Painel de rodapé fixo com:
  - Período de vendas (VendaAtualizacao.Periodo)
  - Data e hora de atualização (VendaAtualizacao.Data + Hora)

**Página de Gerenciamento (`pages/02_⚙️_Gerenciar.py`):**
- Painel "Ordem Atual" mostrando sequência de exibição
- Controles para cada dashboard:
  - Alterar ordem de exibição (com reordenação automática)
  - Alterar duração em segundos
  - Ativar/desativar dashboard
- Interface com Pandas DataFrame estilizado
- Botão "Voltar ao Slideshow" no topo

**Sistema de Normalização de Nomes:**
- Converte nomes de dashboards para nomes de arquivo
- Remove acentos e substitui espaços por underscore
- Exemplo: "Métricas de Vendas" → "metricas_de_vendas.png"

## Dependências

As dependências do projeto devem ser mantidas no arquivo `requirements.txt`. Quando adicionar novas bibliotecas:

```bash
# Instalar dependências
pip install -r requirements.txt

# Adicionar nova dependência
pip install <pacote>
pip freeze > requirements.txt
```

**Principais Dependências:**
- Django 5.2.7
- Streamlit 1.50.0
- streamlit-autorefresh 1.0.1
- psycopg2-binary 2.9.11
- pandas 2.3.3
- black, isort, mypy, rich (ferramentas de desenvolvimento)
