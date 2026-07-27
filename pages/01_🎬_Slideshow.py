"""
Página de Slideshow
Exibe os dashboards em rotação automática com transição suave
"""

import os
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

import django_setup  # Configura Django ORM

# Importa os modelos Django
from dashboard.models import (
    Dashboard,
    Dashboard_Config,
    Dashboard_Log,
    RPA_Atualizacao,
)

# Importa os painéis customizados
from dashboard.panels import (
    render_meta_mes,
    render_metricas_vendas,
    render_ranking_produtos,
    render_ranking_vendedores,
    render_texto,
)

st.set_page_config(
    page_title="Slideshow",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Ler ação do localStorage (JavaScript → Python)
action = components.html(
    """
    <script>
        const action = localStorage.getItem('slideshow_action');
        if (action) {
            localStorage.removeItem('slideshow_action');
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: action}, '*');
        } else {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: null}, '*');
        }
    </script>
    """,
    height=0,
)

# Inicializar tema se não existir
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Tema padrão: escuro

# Inicializar controles de tempo e pausa
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

if 'is_paused' not in st.session_state:
    st.session_state.is_paused = False

if 'last_refresh_count' not in st.session_state:
    st.session_state.last_refresh_count = 0

# Armazenar última ação para debug
if 'last_action' not in st.session_state:
    st.session_state.last_action = "Nenhuma ação ainda"

# Processar ação do localStorage
if action:
    if action == 'toggle_theme':
        st.session_state.last_action = "🎨 TEMA ALTERNADO"
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
    elif action == 'prev':
        st.session_state.last_action = "⏮️ VOLTAR (aguardando processamento)"
        # Será processado depois que dashboards_config estiver disponível
        if 'action_prev' not in st.session_state:
            st.session_state.action_prev = True
    elif action == 'next':
        st.session_state.last_action = "⏭️ AVANÇAR (aguardando processamento)"
        # Será processado depois que dashboards_config estiver disponível
        if 'action_next' not in st.session_state:
            st.session_state.action_next = True
    elif action == 'toggle_pause':
        st.session_state.is_paused = not st.session_state.is_paused
        if st.session_state.is_paused:
            st.session_state.last_action = "⏸️ PAUSADO"
        else:
            st.session_state.last_action = "▶️ CONTINUANDO"
            st.session_state.start_time = time.time()
        st.rerun()

# Definir cores baseadas no tema
if st.session_state.theme == 'dark':
    bg_color = '#000000'
    text_color = '#ffffff'
    card_bg = 'rgba(255, 255, 255, 0.1)'
    border_color = 'rgba(255, 255, 255, 0.3)'
    footer_bg = 'rgba(0, 0, 0, 0.8)'
else:  # light
    bg_color = '#f0f0f0'
    text_color = '#000000'
    card_bg = 'rgba(0, 0, 0, 0.1)'
    border_color = 'rgba(0, 0, 0, 0.3)'
    footer_bg = 'rgba(255, 255, 255, 0.9)'

# Estilo CSS customizado
st.markdown(
    f"""
<style>
    /* Esconde header, footer e sidebar do Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    [data-testid="stSidebar"] {{display: none;}}

    /* Remove padding e margens do container principal */
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* Remove scrollbars */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
        overflow: hidden !important;
        height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* Estilo do card do dashboard - ocupa toda a tela */
    .dashboard-card {{
        background: {bg_color};
        padding: 0;
        text-align: center;
        color: {text_color};
        height: 100vh;
        width: 100vw;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        animation: fadeIn 0.8s ease-in-out;
        position: fixed;
        top: 0;
        left: 0;
        box-sizing: border-box;
    }}

    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: scale(0.95);
        }}
        to {{
            opacity: 1;
            transform: scale(1);
        }}
    }}

    .dashboard-title {{
        font-size: 4rem;
        font-weight: bold;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }}

    .dashboard-description {{
        font-size: 2rem;
        margin-bottom: 40px;
        line-height: 1.6;
    }}

    .dashboard-info {{
        background: rgba(255, 255, 255, 0.2);
        padding: 20px 40px;
        border-radius: 50px;
        font-size: 1.5rem;
        margin-top: 20px;
    }}

    /* Estilo para imagem centralizada em tela cheia */
    .dashboard-image-container {{
        width: 100vw;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        position: fixed;
        top: 0;
        left: 0;
        background: {bg_color};
    }}

    /* Ajusta a imagem para tela cheia centralizada */
    .stImage {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100vw !important;
        height: 100vh !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
    }}

    .stImage img {{
        max-width: 95vw !important;
        max-height: 85vh !important;
        width: auto !important;
        height: auto !important;
        object-fit: contain !important;
        margin: 0 auto !important;
        display: block !important;
    }}

    /* Botão de engrenagem fixo - Container Streamlit */
    div[data-testid="stVerticalBlock"] > div:has(button[kind="secondary"]) {{
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        z-index: 99999 !important;
        width: 60px !important;
        height: 60px !important;
    }}

    /* Estilo do botão de engrenagem */
    button[kind="secondary"] {{
        width: 60px !important;
        height: 60px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 50% !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}

    button[kind="secondary"]:hover {{
        background: rgba(255, 255, 255, 1) !important;
        transform: scale(1.1) rotate(90deg) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
    }}

    button[kind="secondary"] p {{
        font-size: 30px !important;
        margin: 0 !important;
        line-height: 1 !important;
    }}

    /* Painel fixo no rodapé */
    .footer-panel {{
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: {footer_bg} !important;
        backdrop-filter: blur(10px) !important;
        padding: 15px 30px !important;
        z-index: 9999 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 40px !important;
        border-top: none !important;
    }}

    .footer-card {{
        background: {card_bg} !important;
        padding: 12px 30px !important;
        border-radius: 12px !important;
        border: 1px solid {border_color} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }}

    .footer-label {{
        color: {text_color} !important;
        opacity: 0.7 !important;
        font-size: 0.9rem !important;
        margin-bottom: 5px !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }}

    .footer-value {{
        color: {text_color} !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3) !important;
    }}

    /* Botões HTML customizados no rodapé */
    .footer-button {{
        width: 50px !important;
        height: 50px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 50% !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        font-size: 24px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
    }}

    .footer-button:hover {{
        background: rgba(255, 255, 255, 1) !important;
        transform: scale(1.1) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }}

    .footer-controls {{
        display: flex !important;
        gap: 15px !important;
        align-items: center !important;
    }}

    /* Responsividade TV: garante que iframes não ultrapassem o espaço acima do footer */
    iframe {{
        max-height: calc(100vh - 110px) !important;
    }}

</style>
""",
    unsafe_allow_html=True,
)

# Buscar dashboards ativos ordenados
dashboards_config = (
    Dashboard_Config.objects.filter(Dashboard__Ativo=True)
    .select_related('Dashboard')
    .order_by('Ordem')
)

if not dashboards_config.exists():
    st.error("❌ Nenhum dashboard ativo encontrado!")
    st.info("👉 Clique no botão de engrenagem para gerenciar dashboards")
    st.stop()

# Inicializar estado da sessão
if 'current_index' not in st.session_state:
    st.session_state.current_index = (
        0  # 0=Meta Mês, 1=Métricas, 2=Ranking Vendedores, 3=Ranking Produtos
    )

# Obter dashboard atual
total_dashboards = dashboards_config.count()

# Processar ações de navegação (prev/next) do localStorage
if 'action_prev' in st.session_state and st.session_state.action_prev:
    st.session_state.current_index = (
        st.session_state.current_index - 1
    ) % total_dashboards
    st.session_state.start_time = time.time()
    st.session_state.is_paused = False
    st.session_state.last_action = (
        f"⏮️ VOLTOU para slide {st.session_state.current_index + 1}/{total_dashboards}"
    )
    del st.session_state.action_prev
    st.rerun()

if 'action_next' in st.session_state and st.session_state.action_next:
    st.session_state.current_index = (
        st.session_state.current_index + 1
    ) % total_dashboards
    st.session_state.start_time = time.time()
    st.session_state.is_paused = False
    st.session_state.last_action = (
        f"⏭️ AVANÇOU para slide {st.session_state.current_index + 1}/{total_dashboards}"
    )
    del st.session_state.action_next
    st.rerun()

current_config = list(dashboards_config)[st.session_state.current_index]
current_dashboard = current_config.Dashboard
duracao = current_config.Duracao

# Auto-refresh baseado na duração (somente se não estiver pausado)
if not st.session_state.is_paused:
    count = st_autorefresh(interval=duracao * 1000, key="slideshow_refresh")

    # Avançar para o próximo slide somente quando o autorefresh realmente
    # disparou de novo (count aumentou desde a última vez que processamos —
    # sem essa comparação, "count > 0" também era verdade em reruns causados
    # por outros motivos, ex.: prev/next). Recalcula current_config/
    # current_dashboard/duracao já com o índice novo, neste mesmo rerun, para
    # não renderizar o slide antigo mais uma vez (que era o bug original: o
    # primeiro dashboard aparecia duas vezes antes do segundo ser exibido).
    # Importante: NÃO usar st.rerun() aqui — chamar de novo o st_autorefresh
    # logo em seguida faz o componente reportar contagens em rajada, girando
    # os slides muito mais rápido que a duração configurada.
    if count > st.session_state.last_refresh_count:
        st.session_state.last_refresh_count = count
        st.session_state.current_index = (
            st.session_state.current_index + 1
        ) % total_dashboards
        st.session_state.start_time = time.time()  # Reiniciar o timer

        current_config = list(dashboards_config)[st.session_state.current_index]
        current_dashboard = current_config.Dashboard
        duracao = current_config.Duracao

# Renderizar painel dinâmico baseado no nome do dashboard
# Normalizar removendo acentos para comparação
import unicodedata


def remover_acentos(texto):
    """Remove acentos de uma string"""
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


nome_dashboard_normalizado = remover_acentos(current_dashboard.Nome.lower())

# Mapeamento de dashboards para funções de renderização
if 'meta' in nome_dashboard_normalizado and 'mes' in nome_dashboard_normalizado:
    render_meta_mes(theme=st.session_state.theme)
elif (
    'metrica' in nome_dashboard_normalizado or 'metricas' in nome_dashboard_normalizado
):
    render_metricas_vendas(theme=st.session_state.theme)
elif (
    'ranking' in nome_dashboard_normalizado and 'vendedor' in nome_dashboard_normalizado
):
    render_ranking_vendedores(theme=st.session_state.theme)
elif (
    'ranking' in nome_dashboard_normalizado and 'produto' in nome_dashboard_normalizado
):
    render_ranking_produtos(theme=st.session_state.theme)
elif 'mensagem' in nome_dashboard_normalizado or 'texto' in nome_dashboard_normalizado:
    # Slide de mensagem - busca texto do campo Mensagem do Dashboard_Config atual
    texto_mensagem = (
        current_config.Mensagem
        if current_config.Mensagem
        else "Mensagem não configurada"
    )

    render_texto(
        texto=texto_mensagem,
        titulo="",  # Sem título
        theme=st.session_state.theme,
    )
else:
    # Fallback: exibir card simples se não houver painel específico
    st.markdown(
        f"""
    <div class="dashboard-card">
        <div class="dashboard-title">{current_dashboard.Nome}</div>
        <div class="dashboard-description">{current_dashboard.Descricao}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Buscar informações de atualização (filtrar apenas RPA_id = 7)
try:
    rpa_atualizacao = RPA_Atualizacao.objects.filter(RPA_id=7).latest('id')
    periodo = rpa_atualizacao.Periodo
    data_atualizacao = f"{rpa_atualizacao.Data} {rpa_atualizacao.Hora}"
except RPA_Atualizacao.DoesNotExist:
    periodo = "N/A"
    data_atualizacao = "N/A"

# Ícone do botão de tema baseado no estado atual
tema_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
pause_icon = "⏸️" if not st.session_state.is_paused else "▶️"

# Painel fixo no rodapé com informações de atualização
st.markdown(
    f"""
    <div class="footer-panel">
        <div class="footer-card">
            <div class="footer-label">📅 Período</div>
            <div class="footer-value">{periodo}</div>
        </div>
        <div class="footer-card">
            <div class="footer-label">🕐 Data Atualização</div>
            <div class="footer-value">{data_atualizacao}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Ajuste dinâmico de altura dos painéis para evitar sobreposição do footer em TVs
components.html(
    """
    <script>
    (function() {
        function ajustarIframes() {
            try {
                var win = window.parent;
                var vh = win.innerHeight;
                var footer = win.document.querySelector('.footer-panel');
                var fh = footer ? footer.getBoundingClientRect().height + 12 : 110;
                var altura = Math.floor(vh - fh);
                win.document.querySelectorAll('iframe').forEach(function(el) {
                    var h = parseInt(el.getAttribute('height') || 0);
                    if (h > 300 && parseInt(el.style.height || h) !== altura) {
                        el.style.height = altura + 'px';
                        el.style.maxHeight = altura + 'px';
                    }
                });
            } catch(e) {}
        }
        setTimeout(ajustarIframes, 150);
        if (!window.parent._dashboardResizeAttached) {
            window.parent._dashboardResizeAttached = true;
            window.parent.addEventListener('resize', function() {
                setTimeout(ajustarIframes, 100);
            });
        }
    })();
    </script>
    """,
    height=0,
)

# Botão de engrenagem para navegação
if st.button("⚙️", key="settings_btn", type="secondary", help="Gerenciar Dashboards"):
    st.switch_page("pages/02_⚙️_Gerenciar.py")
