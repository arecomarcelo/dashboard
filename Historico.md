# 📋 Histórico de Alterações - SGD

---

## 📅 08/10/2026

### 🕒 15:17 — Corte da Onda 3: DashBoard em produção sobre o oficial_db

**📝 O que foi pedido:** executar o corte coordenado da Onda 3 (etapa 32 do Plano de Implementação - Migração RPA para Oficial DB, multi-aplicacao).

**🔧 Solução:**
- 🔀 Merge do branch `migracao-oficial-db` no `master` e deploy às 15:11. O `migrate` criou `Dashboard`, `Dashboard_Config` e `Dashboard_Log` no schema `dashboard`.
- 🔐 Nova role `dashboard_user`, dona do schema `dashboard`. A senha foi gerada na VPS e nunca exibida, e o `.env` da VPS aponta para o `oficial_db` com `DB_SCHEMA=dashboard`.
- 📦 Configuração copiada uma única vez do legado: 6 painéis, 12 vendedores e a Meta.
- ✅ Smoke test: conexão `dashboard_user`/`oficial_db`, 4.952 vendas, os 5 painéis ativos, rodapé com a última execução do RPA de Vendas e health 200.
- ↩️ Rollback: `.env.bak-pre-corte-20261008-1510` + imagem `sha256:82188bf7…`.

**📁 Arquivos alterados:** `Historico.md`, `documentacao/Ajustes.md`.

*Realizado em Note_Oficial via Claude Code.*

---

### 🕐 14:32 — Migração do DashBoard para o oficial_db (etapa 28)

**📝 O que foi pedido:** seguir com o Plano de Implementação - Migração RPA para Oficial DB (multi-aplicacao) — etapa 28, DashBoard deixando de ler o legado `sga`.

**🔧 Solução:**
- 🗄️ Tabelas próprias (`Dashboard`, `Dashboard_Config`, `Dashboard_Log`) no novo schema `dashboard` (`managed=True`), com uma `0001_initial` limpa no lugar das migrations da época do legado.
- 📊 Vendas, itens, meta, vendedores e situações lidos do schema `vendas`; produtos de `compartilhado."Produtos"`.
- 🕐 Rodapé "Data Atualização" passa a vir de `rpa."ControleAtualizacao"` (última execução do RPA de Vendas), no lugar do `RPA_Atualizacao`.
- 📝 Log Duplo no padrão de `compartilhado."Log"` (`Modulo=dashboard`).
- 🐳 `stack.yml` na rede `oficial_db_net` (sem `extra_hosts`) e `migrate dashboard` no entrypoint.
- 🧪 Validado no local: 14 testes, Slideshow e Gerenciar executados sem exceção, Meta salva pela tela com alerta de sucesso e Log.
- 🚦 Branch `migracao-oficial-db`: publicação só no corte coordenado da Onda 3 (etapa 32).

**📁 Arquivos alterados:** `app/settings.py`, `dashboard/models.py`, `dashboard/admin.py`, `dashboard/services.py`, `dashboard/migrations/` (0001 nova, 0002–0004 removidas), `pages/01_🎬_Slideshow.py`, `entrypoint.sh`, `stack.yml`, `.env.example`, `documentacao/Ajustes.md`, `Historico.md`.

*Realizado em Note_Oficial via Claude Code.*

---

## 📅 11/05/2026

### 🕐 09:47 — Verificação Geral: Correção de Tipos de Campos dos Modelos

**🔍 O que foi pedido:**
Verificar a aplicação após ajustes nos tipos de campos dos modelos e corrigir possíveis quebras.

**🛠️ Detalhamento da Solução:**

**Problema crítico identificado:**
O banco de dados foi atualizado para usar tipos numéricos nos campos de valor, mas os modelos Django ainda declaravam esses campos como `CharField`. Isso causava falha silenciosa nos cálculos de todos os painéis financeiros:
- Os campos `ValorCusto`, `ValorProdutos`, `ValorDesconto`, `ValorTotal` em `Vendas` retornavam `Decimal` do banco, mas a função `parse_valor()` chamava `.strip()` em objetos `Decimal` (sem esse método), caindo no `except` e retornando `Decimal("0")` para todos os valores.
- O campo `Quantidade` em `VendaProdutos` retornava `int`, mas `parse_quantidade()` chamava `.strip()` em inteiros, causando o mesmo problema.
- Resultado: **todos os painéis (Meta do Mês, Métricas, Ranking) exibiam R$ 0,00**.

**Divergências encontradas entre Banco e Modelos:**

| Tabela | Campo | Banco | Modelo (antes) | Modelo (depois) |
|--------|-------|-------|----------------|-----------------|
| `Vendas` | `ValorCusto/Produtos/Desconto/Total` | `numeric(15,2)` | `CharField` | `DecimalField(15,2)` |
| `VendaProdutos` | `Quantidade` | `integer` | `CharField` | `IntegerField` |
| `VendaProdutos` | `ValorCusto/Venda/Desconto/Total` | `numeric(15,2)` | `CharField` | `DecimalField(15,2)` |
| `Produtos` | `ValorVenda`, `ValorCusto` | `numeric(15,2)` | `CharField(10)` | `DecimalField(15,2)` |

**Correções aplicadas:**

1. **`dashboard/models.py`** — Atualização dos tipos de campos para refletir o banco real:
   - `Vendas`: 4 campos de valor → `DecimalField(max_digits=15, decimal_places=2)`
   - `VendaProdutos`: `quantidade` → `IntegerField`; 4 campos de valor → `DecimalField(15,2)`
   - `Produtos`: `valorvenda`, `valorcusto` → `DecimalField(15,2, null=True, blank=True)`

2. **`dashboard/panels.py`** — Funções `parse_valor()` e `parse_quantidade()` tornadas resilientes a tipos numéricos:
   - Se o valor já é `Decimal`: retorna diretamente
   - Se é `int` ou `float`: converte via `Decimal(str(valor))`
   - Se é string: mantém lógica original

3. **`dashboard/migrations/0004_...`** — Migração gerada para registrar `managed=False` nos modelos (operação no-op no banco)

**Validação:**
- `parse_valor(Decimal('728755.16'))` → `Decimal('728755.16')` ✅ (antes: `Decimal('0')`)
- `parse_quantidade(5)` → `Decimal('5')` ✅ (antes: `Decimal('0')`)
- Total Vendas do período calculado: `R$ 4.269.815,52` ✅ (antes: `R$ 0,00`)
- `python manage.py check` → 0 issues ✅

**📁 Arquivos Alterados:**

| Arquivo | Alteração |
|---------|-----------|
| `dashboard/models.py` | Tipos de campos numéricos corrigidos (`DecimalField`, `IntegerField`) |
| `dashboard/panels.py` | Funções `parse_valor()` e `parse_quantidade()` atualizadas para suportar tipos numéricos |
| `dashboard/migrations/0004_alter_dashboard_options_and_more.py` | Migração criada e aplicada (no-op no banco) |

---

## 📅 08/05/2026

### 🕐 15:50 — Correção de Responsividade: Footer sobrepondo Painel na TV

**🔍 O que foi pedido:**
O footer do slideshow estava sobrepondo o painel quando executado em TV. No desktop funcionava corretamente.

**🛠️ Detalhamento da Solução:**

**Causa raiz identificada:**
- Os painéis são renderizados via `components.html()` dentro de **iframes com altura fixa** (ex: 850px, 750px).
- O footer usa `position: fixed; bottom: 0` na página principal (fora do iframe).
- Em TVs com zoom de browser maior ou viewport reduzida, o footer (em `viewport - 100px`) ficava **dentro da área visível do iframe**, causando sobreposição visual.
- Os `padding-bottom: 200px/180px` nos painéis eram um "hack" aplicado no lugar errado (dentro do iframe, sem efeito sobre o footer externo).

**Correções aplicadas:**

1. **CSS `max-height` como proteção imediata** — adicionado em `01_🎬_Slideshow.py`:
   ```css
   iframe { max-height: calc(100vh - 110px) !important; }
   ```
   Garante que nenhum iframe ultrapasse a área disponível acima do footer.

2. **JavaScript dinâmico** — componente `components.html(height=0)` adicionado em `01_🎬_Slideshow.py`:
   - Mede a altura real do viewport (`window.parent.innerHeight`)
   - Mede a altura real do footer (`.footer-panel.getBoundingClientRect().height`)
   - Redimensiona todos os iframes de painel (height > 300px) para exatamente `viewport - footer - 12px`
   - Responde a eventos de resize (rotação de tela, zoom, etc.)
   - Usa flag `window.parent._sgdResizeAttached` para evitar múltiplos listeners em rerenders

3. **Remoção dos paddings excessivos** em `dashboard/panels.py`:
   - `render_meta_mes`: `padding-bottom: 200px` → `30px`
   - `render_metricas_vendas`: `padding-bottom: 180px` → `40px` (incluindo media queries)
   - `render_texto`: `padding-bottom: 200px/180px` → `50px/40px/30px`
   - `render_ranking_produtos`: `padding-bottom: 180px` → `30px` (incluindo media queries)

**📁 Arquivos Alterados:**

| Arquivo | Alteração |
|---------|-----------|
| `pages/01_🎬_Slideshow.py` | CSS `max-height` + componente JS de redimensionamento dinâmico |
| `dashboard/panels.py` | Redução de `padding-bottom` excessivo em todos os painéis |
