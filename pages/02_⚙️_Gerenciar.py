"""
Página de Gerenciamento de Dashboards
Permite atualizar configurações de dashboards existentes
"""

import pandas as pd
import streamlit as st

import django_setup  # Configura Django ORM

# Importa os modelos Django
from dashboard.models import Dashboard, Dashboard_Config, VendaConfiguracao, Vendedores
from dashboard.services import registrar_log

st.set_page_config(page_title="Gerenciar Dashboards", page_icon="⚙️", layout="wide")

# Header com título e botão de voltar
col_title, col_button = st.columns([5, 1])
with col_title:
    st.title("⚙️ Gerenciar Dashboards")
with col_button:
    st.write("")  # Espaçamento vertical
    if st.button("🎬 Voltar ao Slideshow", key="btn_voltar"):
        st.switch_page("pages/01_🎬_Slideshow.py")

st.markdown("---")

# Painel de Meta de Vendas
st.subheader("🎯 Meta de Vendas")

# Buscar valor atual da meta
try:
    config_meta = VendaConfiguracao.objects.get(Descricao="Meta")
    valor_meta_atual = config_meta.Valor
except VendaConfiguracao.DoesNotExist:
    valor_meta_atual = "0"
    st.warning("⚠️ Configuração de Meta não encontrada no banco de dados")

# Layout em colunas para o campo de meta
col_meta1, col_meta2 = st.columns([3, 1])

with col_meta1:
    nova_meta = st.text_input(
        "Valor da Meta",
        value=valor_meta_atual,
        placeholder="Digite o valor da meta",
        help="💡 Digite o valor da meta de vendas",
        key="input_meta",
    )

with col_meta2:
    st.write("")  # Espaçamento vertical para alinhar o botão
    st.write("")  # Mais espaçamento
    if st.button(
        "💾 Salvar Meta",
        key="btn_salvar_meta",
        help="Clique para salvar o valor da meta",
    ):
        if nova_meta and nova_meta.strip():
            try:
                config_meta = VendaConfiguracao.objects.get(Descricao="Meta")
                valor_anterior = config_meta.Valor
                config_meta.Valor = nova_meta.strip()
                config_meta.save()
                registrar_log(
                    f"Dashboard [Gerenciar] - Meta de Vendas alterada de "
                    f"'{valor_anterior}' para '{nova_meta.strip()}'"
                )
                st.success(f"✅ Meta atualizada com sucesso para: {nova_meta}")
                st.rerun()
            except VendaConfiguracao.DoesNotExist:
                st.error(
                    "❌ Erro: Configuração de Meta não encontrada no banco de dados"
                )
            except Exception as e:
                st.error(f"❌ Erro ao salvar meta: {str(e)}")
        else:
            st.warning("⚠️ Por favor, digite um valor válido para a meta")

st.markdown("---")

# Grid de Vendedores - Percentual de Meta
st.subheader("👥 Vendedores - Percentual de Meta Pessoal")

vendedores_list = Vendedores.objects.all().order_by('nome')

if vendedores_list.exists():
    for idx, vendedor in enumerate(vendedores_list):
        col_nome, col_curto, col_percentual, col_acao = st.columns([3, 2, 2, 1])

        with col_nome:
            st.text_input(
                "Nome",
                value=vendedor.nome or "",
                disabled=True,
                key=f"vend_nome_{idx}",
                label_visibility="collapsed" if idx > 0 else "visible",
            )

        with col_curto:
            novo_curto = st.text_input(
                "Curto",
                value=vendedor.curto or "",
                placeholder="Nome curto",
                key=f"vend_curto_{idx}",
                label_visibility="collapsed" if idx > 0 else "visible",
            )

        with col_percentual:
            novo_percentual = st.number_input(
                "Percentual",
                value=vendedor.percentual if vendedor.percentual else 0,
                min_value=0,
                max_value=100,
                step=1,
                key=f"vend_perc_{idx}",
                label_visibility="collapsed" if idx > 0 else "visible",
            )

        with col_acao:
            if idx == 0:
                st.write("Ações")
            if st.button(
                "💾",
                key=f"vend_save_{idx}",
                help=f"Salvar alterações do vendedor {vendedor.nome}",
            ):
                try:
                    vendedor.curto = novo_curto.strip() if novo_curto else ""
                    vendedor.percentual = novo_percentual
                    vendedor.save(update_fields=["curto", "percentual"])
                    registrar_log(
                        f"Dashboard [Gerenciar] - Vendedor '{vendedor.nome}' atualizado "
                        f"(curto='{vendedor.curto}', percentual={vendedor.percentual})"
                    )
                    st.success(f"✅ Vendedor '{vendedor.nome}' atualizado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {str(e)}")
else:
    st.info("📭 Nenhum vendedor cadastrado")

st.markdown("---")

# Painel de Texto Dinâmico
st.subheader("💬 Texto Dinâmico")

# Buscar valor atual do texto dinâmico no Dashboard_Config do Dashboard "Mensagem"
try:
    config_mensagem = (
        Dashboard_Config.objects.select_related('Dashboard')
        .filter(Dashboard__Nome__icontains='Mensagem')
        .first()
    )
    if config_mensagem:
        valor_texto_atual = config_mensagem.Mensagem or ""
    else:
        valor_texto_atual = ""
        st.warning("⚠️ Dashboard 'Mensagem' não encontrado no banco de dados")
except Exception as e:
    valor_texto_atual = ""
    st.warning(f"⚠️ Erro ao buscar configuração de mensagem: {str(e)}")

# Layout em colunas para o campo de texto dinâmico
col_texto1, col_texto2 = st.columns([3, 1])

with col_texto1:
    novo_texto = st.text_input(
        "Mensagem",
        value=valor_texto_atual,
        placeholder="Digite a mensagem dinâmica",
        help="💡 Digite o texto que será exibido dinamicamente",
        key="input_texto_dinamico",
    )

with col_texto2:
    st.write("")  # Espaçamento vertical para alinhar o botão
    st.write("")  # Mais espaçamento
    if st.button(
        "💾 Salvar Texto",
        key="btn_salvar_texto",
        help="Clique para salvar a mensagem",
    ):
        try:
            config_mensagem = (
                Dashboard_Config.objects.select_related('Dashboard')
                .filter(Dashboard__Nome__icontains='Mensagem')
                .first()
            )
            if config_mensagem:
                config_mensagem.Mensagem = novo_texto.strip() if novo_texto else ""
                config_mensagem.save()
                registrar_log(
                    "Dashboard [Gerenciar] - Texto Dinâmico (Mensagem) alterado para: "
                    f"'{config_mensagem.Mensagem}'"
                )
                st.success("✅ Mensagem atualizada com sucesso!")
                st.rerun()
            else:
                st.error(
                    "❌ Erro: Dashboard 'Mensagem' não encontrado no banco de dados"
                )
        except Exception as e:
            st.error(f"❌ Erro ao salvar mensagem: {str(e)}")

st.markdown("---")

# Painel de Ordem Atual
st.subheader("📊 Ordem Atual")

# Buscar dashboards com configuração ordenados
dashboards_ordenados = Dashboard_Config.objects.select_related('Dashboard').order_by(
    'Ordem'
)

if dashboards_ordenados.exists():
    # Criar tabela de ordem atual
    ordem_data = []
    for config in dashboards_ordenados:
        status_icon = "✅" if config.Dashboard.Ativo else "❌"
        ordem_data.append(
            {
                "Ordem": config.Ordem,
                "Dashboard": f"{status_icon} {config.Dashboard.Nome}",
                "Duração": f"{config.Duracao}s",
            }
        )

    # Exibir em formato de tabela
    df_ordem = pd.DataFrame(ordem_data)

    # Exibir tabela estilizada
    st.dataframe(
        df_ordem,
        hide_index=True,
        width="stretch",
        column_config={
            "Ordem": st.column_config.NumberColumn(
                "Ordem", help="Ordem de exibição no slideshow", width="small"
            ),
            "Dashboard": st.column_config.TextColumn(
                "Dashboard",
                help="Nome do dashboard (✅ Ativo / ❌ Inativo)",
                width="large",
            ),
            "Duração": st.column_config.TextColumn(
                "Duração", help="Tempo de exibição em segundos", width="small"
            ),
        },
    )
else:
    st.info("📭 Nenhum dashboard cadastrado com configuração de exibição")

st.markdown("---")


# Função para ajustar ordens automaticamente
def ajustar_ordens(dashboard_id, nova_ordem, ordem_antiga):
    """
    Ajusta as ordens dos demais dashboards para evitar duplicatas
    """
    configs = Dashboard_Config.objects.exclude(Dashboard__id=dashboard_id).order_by(
        'Ordem'
    )

    if nova_ordem > ordem_antiga:
        # Movendo para baixo (aumentando ordem)
        # Todos os dashboards entre ordem_antiga+1 e nova_ordem devem subir (ordem-1)
        for config in configs:
            if ordem_antiga < config.Ordem <= nova_ordem:
                config.Ordem -= 1
                config.save()
    elif nova_ordem < ordem_antiga:
        # Movendo para cima (diminuindo ordem)
        # Todos os dashboards entre nova_ordem e ordem_antiga-1 devem descer (ordem+1)
        for config in configs:
            if nova_ordem <= config.Ordem < ordem_antiga:
                config.Ordem += 1
                config.save()


# Listar Dashboards
st.header("📋 Dashboards Cadastrados")

dashboards = Dashboard.objects.all().order_by('Nome')

if dashboards.exists():
    for dash in dashboards:
        with st.expander(f"{'✅' if dash.Ativo else '❌'} {dash.Nome}", expanded=False):

            # Buscar configuração
            try:
                config = Dashboard_Config.objects.get(Dashboard=dash)

                # Layout em colunas
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.write(f"**Descrição:** {dash.Descricao}")
                    st.write(
                        f"**Status:** {'Ativo ✅' if dash.Ativo else 'Inativo ❌'}"
                    )

                with col2:
                    st.write("**Configurações de Exibição:**")

                    # Controle updown para Ordem
                    nova_ordem = st.number_input(
                        "Ordem de Exibição",
                        min_value=1,
                        value=config.Ordem,
                        step=1,
                        key=f"ordem_{dash.id}",
                    )

                    # Controle updown para Duração
                    nova_duracao = st.number_input(
                        "Duração (segundos)",
                        min_value=1,
                        value=config.Duracao,
                        step=1,
                        key=f"duracao_{dash.id}",
                    )

                with col3:
                    st.write("**Ações:**")

                    # Botão para ativar/desativar
                    if st.button(
                        f"{'🔴 Desativar' if dash.Ativo else '🟢 Ativar'}",
                        key=f"toggle_{dash.id}",
                    ):
                        dash.Ativo = not dash.Ativo
                        dash.save()
                        registrar_log(
                            f"Dashboard [Gerenciar] - Dashboard '{dash.Nome}' "
                            f"{'ativado' if dash.Ativo else 'desativado'}"
                        )
                        st.success(
                            f"Dashboard {'ativado' if dash.Ativo else 'desativado'} com sucesso!"
                        )
                        st.rerun()

                    # Botão para salvar alterações
                    if st.button("💾 Salvar", key=f"save_{dash.id}"):
                        ordem_alterada = nova_ordem != config.Ordem

                        # Ajustar ordens dos demais se necessário
                        if ordem_alterada:
                            ajustar_ordens(dash.id, nova_ordem, config.Ordem)

                        # Atualizar config
                        config.Ordem = nova_ordem
                        config.Duracao = nova_duracao
                        config.save()

                        registrar_log(
                            f"Dashboard [Gerenciar] - Dashboard '{dash.Nome}' "
                            f"atualizado (ordem={nova_ordem}, duração={nova_duracao}s"
                            f"{', com reordenação dos demais' if ordem_alterada else ''})"
                        )
                        st.success(
                            f"✅ Dashboard '{dash.Nome}' atualizado com sucesso!"
                        )
                        st.rerun()

            except Dashboard_Config.DoesNotExist:
                st.warning("⚠️ Sem configuração de exibição")
                st.info(
                    "💡 Este dashboard precisa de uma configuração para ser exibido no slideshow"
                )
else:
    st.info("📭 Nenhum dashboard cadastrado ainda.")
    st.warning(
        "⚠️ A funcionalidade de cadastro foi desabilitada. Entre em contato com o administrador."
    )

st.markdown("---")
st.caption(
    "💡 **Dica**: Ajuste a ordem e duração dos dashboards conforme necessário. Clique em 'Salvar' para aplicar as alterações."
)
