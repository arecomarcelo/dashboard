"""
Painéis de visualização para os dashboards do DashBoard
Réplicas EXATAS dos layouts do SGR conforme imagens de referência
"""

import base64
import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from django.utils import timezone

from dashboard.models import VendaConfiguracao, VendaProdutos, Vendas, Vendedores

erro_logger = logging.getLogger("erro_logger")

# Import para requirements.txt
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # Se não tiver instalado, criar fallback
    pass

# Lista completa de vendedores (mesma ordem do SGR) — Nome → ID da foto (1-12.png)
# Compartilhada entre render_ranking_vendedores e render_resumo_dia.
VENDEDORES_TABELA = [
    {"nome": "Noé Dutra", "foto": "1"},
    {"nome": "Nilton Jonas Gonçalves de Moraes", "foto": "2"},
    {"nome": "César Henrique Rodrigues", "foto": "3"},
    {"nome": "Rocha Jr.", "foto": "4"},
    {"nome": "Diney Scalabrini", "foto": "5"},
    {"nome": "João Paulo", "foto": "6"},
    {"nome": "Lauro Jarbas de Oliveira", "foto": "7"},
    {"nome": "Giovana Lelis", "foto": "8"},
    {"nome": "Carlos Gabriel Carvalho Macedo", "foto": "9"},
    {"nome": "Cássio Gadagnoto", "foto": "10"},
    {"nome": "André Souza", "foto": "11"},
    {"nome": "João Victor", "foto": "12"},
]


def get_vendedor_foto(foto_id):
    """Carrega foto do vendedor em base64 (imagens/fotos/<id>.jpg|png)"""
    fotos_dir = Path("imagens/fotos")
    for ext in ['.jpg', '.png']:
        foto_path = fotos_dir / f"{foto_id}{ext}"
        if foto_path.exists():
            try:
                with open(foto_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                    return f"data:image/png;base64,{img_data}"
            except Exception:
                continue
    return None


def get_gradient(rank):
    """Gradiente do card de ranking por posição (ouro/prata/bronze/padrão)"""
    if rank == 1:
        return "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)"  # Ouro
    elif rank == 2:
        return "linear-gradient(135deg, #C0C0C0 0%, #808080 100%)"  # Prata
    elif rank == 3:
        return "linear-gradient(135deg, #CD7F32 0%, #8B4513 100%)"  # Bronze
    else:
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"  # Roxo padrão


def get_filtros_periodo():
    """
    Retorna filtros fixos do DashBoard:
    - Data Inicial: 01 do mês atual
    - Data Final: Dia atual
    """
    # `timezone.localdate()` (Django, timezone-aware) em vez de `datetime.now()` —
    # achado de auditoria (17/08/2026): funcionava até aqui só porque o container
    # define TZ=America/Sao_Paulo no SO; frágil (quebraria em dev local ou se a env
    # var sumisse), regra do projeto é nunca usar horário "naive".
    hoje = timezone.localdate()
    data_inicial = f"01/{hoje.month:02d}/{hoje.year}"
    data_final = hoje.strftime("%d/%m/%Y")
    return data_inicial, data_final


def parse_valor(valor):
    """Converte valor monetário para Decimal (aceita Decimal, int, float ou string)"""
    try:
        if isinstance(valor, Decimal):
            return valor
        if isinstance(valor, (int, float)):
            return Decimal(str(valor))
        valor_limpo = str(valor).strip().replace(",", ".")
        return Decimal(valor_limpo)
    except (InvalidOperation, ValueError, TypeError) as exc:
        # Achado de auditoria (17/08/2026): `except:` genérico engolia qualquer erro
        # e caía para 0 silenciosamente — um dado malformado real apareceria como
        # "R$ 0,00" na tela pública sem log nenhum. Agora loga o valor problemático.
        erro_logger.error(f"parse_valor: falha ao converter {valor!r} — {exc}")
        return Decimal("0")


def parse_quantidade(quantidade):
    """Converte quantidade para Decimal (aceita int, float, Decimal ou string)"""
    try:
        if isinstance(quantidade, Decimal):
            return quantidade
        if isinstance(quantidade, (int, float)):
            return Decimal(str(quantidade))
        valor_limpo = str(quantidade).strip().replace(",", ".")
        return Decimal(valor_limpo)
    except (InvalidOperation, ValueError, TypeError) as exc:
        erro_logger.error(
            f"parse_quantidade: falha ao converter {quantidade!r} — {exc}"
        )
        return Decimal("0")


def format_currency(value):
    """Formata valor como moeda brasileira"""
    return (
        f"R$ {float(value):,.2f}".replace(".", "#").replace(",", ".").replace("#", ",")
    )


@st.cache_data(ttl=300)  # Cache de 5 minutos
def get_vendas_periodo():
    """
    Busca vendas do período com filtros fixos aplicados
    Retorna queryset filtrado
    Exclui vendas com situação "Cancelada (sem financeiro)" e "Não considerar - Excluidos"
    Filtra apenas vendedores que existem na tabela Vendedores
    """
    data_inicial, data_final = get_filtros_periodo()

    di_parts = data_inicial.split("/")
    df_parts = data_final.split("/")

    data_inicio = date(int(di_parts[2]), int(di_parts[1]), int(di_parts[0]))
    data_fim = date(int(df_parts[2]), int(df_parts[1]), int(df_parts[0]))

    # Situações a serem excluídas
    situacoes_excluidas = ["Cancelada (sem financeiro)", "Não considerar - Excluidos"]

    # Buscar lista de vendedores válidos
    vendedores_validos = set(Vendedores.objects.values_list('nome', flat=True))

    vendas = Vendas.objects.all()

    vendas_filtradas = []
    for venda in vendas:
        try:
            # Filtrar por situação
            if venda.situacaonome in situacoes_excluidas:
                continue

            # Filtrar apenas vendedores válidos (trim do nome)
            vendedor_nome = venda.vendedornome.strip() if venda.vendedornome else ""
            if vendedor_nome not in vendedores_validos:
                continue

            if not venda.data:
                continue

            if data_inicio <= venda.data <= data_fim:
                vendas_filtradas.append(venda)
        except (AttributeError, TypeError) as exc:
            erro_logger.error(
                f"get_vendas_periodo: registro de venda id={getattr(venda, 'id', '?')} "
                f"pulado — {exc}"
            )
            continue

    return vendas_filtradas


def render_meta_mes(theme='dark'):
    """
    Renderiza painel Meta Mês - RÉPLICA EXATA da imagem de referência
    """
    # Buscar meta do mês na configuração
    try:
        meta_config = VendaConfiguracao.objects.filter(Descricao='Meta').first()
        meta_mes = parse_valor(meta_config.Valor) if meta_config else Decimal("0")
    except Exception as exc:
        # Exceção ampla proposital aqui (não é parsing, é acesso a banco — pode ser
        # qualquer erro de conectividade) — mas agora logada, não mais silenciosa.
        erro_logger.error(f"render_meta_mes: falha ao buscar Meta em VendaConfiguracao — {exc}")
        meta_mes = Decimal("0")

    # Buscar vendas do período
    vendas = get_vendas_periodo()
    total_vendido = sum(parse_valor(v.valortotal) for v in vendas)

    # Calcular percentual
    percentual = float(
        (total_vendido / meta_mes * 100) if meta_mes > 0 else Decimal("0")
    )

    # Cores do tema Dracula at Night
    if theme == 'dark':
        bg_color = "#1a1d2e"  # Background escuro do Dracula
        text_color_primary = "#8be9fd"  # Ciano
        text_color_secondary = "#6272a4"  # Comentário
        card_bg = "#000000"  # Preto para cards
        progress_bar_bg = "#f8f8f2"  # Barra branca
        cor_realizado = "#8be9fd"  # Ciano para progresso
        cor_faltando = "#44475a"  # Cinza do Dracula
    else:
        bg_color = "#f0f0f0"
        text_color_primary = "#1a73e8"
        text_color_secondary = "#5f6368"
        card_bg = "#000000"  # Preto para cards
        progress_bar_bg = "#ffffff"
        cor_realizado = "#4285f4"
        cor_faltando = "#e8eaed"

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: {bg_color};
                    overflow-y: auto;
                }}
                .meta-container {{
                    background: {bg_color};
                    min-height: 100vh;
                    width: 100vw;
                    padding: 30px 20px 30px 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                }}
                .meta-title {{
                    color: {text_color_primary};
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    letter-spacing: -0.5px;
                }}
                .meta-title-icon {{
                    font-size: 2.8rem;
                }}
                .progress-bar-container {{
                    width: 90%;
                    max-width: 750px;
                    margin-bottom: 20px;
                }}
                .progress-bar {{
                    background: {progress_bar_bg};
                    border-radius: 25px;
                    height: 30px;
                    width: 100%;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                }}
                .donut-container {{
                    position: relative;
                    width: 280px;
                    height: 280px;
                    margin: 20px 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .donut-chart {{
                    width: 280px;
                    height: 280px;
                }}
                .donut-center {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                }}
                .donut-percent {{
                    color: {text_color_primary};
                    font-size: 4rem;
                    font-weight: 700;
                    line-height: 1;
                    margin-bottom: 5px;
                }}
                .donut-label {{
                    color: {text_color_secondary};
                    font-size: 1.2rem;
                    font-weight: 500;
                }}
                .info-cards {{
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                    width: 90%;
                    max-width: 750px;
                    margin-top: 15px;
                    margin-bottom: 30px;
                }}
                .info-card {{
                    background: {card_bg};
                    border-radius: 16px;
                    padding: 20px 40px;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
                    border: 1px solid #44475a;
                }}
                .info-label {{
                    color: #f8f8f2;
                    font-size: 1rem;
                    font-weight: 600;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }}
                .info-value {{
                    color: {text_color_primary};
                    font-size: 2rem;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }}

                @media (max-width: 768px) {{
                    .meta-title {{
                        font-size: 2rem;
                    }}
                    .donut-container {{
                        width: 280px;
                        height: 280px;
                    }}
                    .donut-chart {{
                        width: 280px;
                        height: 280px;
                    }}
                    .donut-percent {{
                        font-size: 3.5rem;
                    }}
                    .info-value {{
                        font-size: 1.8rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="meta-container">
                <div class="meta-title">
                    <span class="meta-title-icon">🎯</span>
                    <span>Meta de Vendas do Mês</span>
                </div>

                <div class="progress-bar-container">
                    <div class="progress-bar"></div>
                </div>

                <div class="donut-container">
                    <svg class="donut-chart" viewBox="0 0 100 100">
                        <!-- Círculo de fundo (cinza) -->
                        <circle cx="50" cy="50" r="35"
                                fill="none"
                                stroke="{cor_faltando}"
                                stroke-width="12"/>
                        <!-- Círculo de progresso (azul/ciano) -->
                        <circle cx="50" cy="50" r="35"
                                fill="none"
                                stroke="{cor_realizado}"
                                stroke-width="12"
                                stroke-dasharray="{percentual * 2.199} 219.9"
                                stroke-linecap="round"
                                transform="rotate(-90 50 50)"
                                style="transition: stroke-dasharray 0.5s ease;"/>
                        <!-- Círculo interno (background) -->
                        <circle cx="50" cy="50" r="28" fill="{bg_color}"/>
                    </svg>
                    <div class="donut-center">
                        <div class="donut-percent">{percentual:.0f}%</div>
                        <div class="donut-label">da Meta</div>
                    </div>
                </div>

                <div class="info-cards">
                    <div class="info-card">
                        <div class="info-label">💰 Realizado no Mês</div>
                        <div class="info-value">{format_currency(total_vendido)}</div>
                    </div>

                    <div class="info-card">
                        <div class="info-label">🎯 Meta do Mês</div>
                        <div class="info-value">{format_currency(meta_mes)}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """

    # Usar height adequado para evitar sobreposição com rodapé
    components.html(html_content, height=850, scrolling=False)


def render_metricas_vendas(theme='dark'):
    """
    Renderiza painel Métricas de Vendas - RÉPLICA EXATA da imagem de referência
    """
    # Buscar vendas do período
    vendas = get_vendas_periodo()

    # Calcular métricas
    qtd_vendas = len(vendas)
    total_vendido = sum(parse_valor(v.valortotal) for v in vendas)
    total_custo = sum(parse_valor(v.valorcusto) for v in vendas)

    # Calcular entradas e parcelado (40% entradas, 60% parcelado - aproximação)
    total_entradas = total_vendido * Decimal("0.40")
    total_parcelado = total_vendido * Decimal("0.60")

    ticket_medio = (total_vendido / qtd_vendas) if qtd_vendas > 0 else Decimal("0")
    margem_lucro = total_vendido - total_custo
    percentual_margem = (
        ((margem_lucro / total_vendido) * 100) if total_vendido > 0 else Decimal("0")
    )

    # Cores do tema Dracula at Night
    if theme == 'dark':
        bg_color = "#1a1d2e"  # Background escuro
        text_color_primary = "#8be9fd"  # Ciano
        card_bg = "#000000"  # Preto para cards
        btn_bg = "#44475a"  # Cinza do Dracula
        btn_text = "#f8f8f2"  # Texto claro
    else:
        bg_color = "#f0f0f0"
        text_color_primary = "#1a73e8"
        card_bg = "#000000"  # Preto para cards
        btn_bg = "#ffffff"
        btn_text = "#1a73e8"

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: {bg_color};
                    overflow-y: auto;
                }}
                .metricas-container {{
                    background: {bg_color};
                    min-height: 100vh;
                    width: 100vw;
                    padding: 40px 60px 40px 60px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }}
                .metricas-title {{
                    color: {text_color_primary};
                    font-size: 2.5rem;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                    margin-bottom: 50px;
                    text-align: center;
                }}
                .metricas-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 30px;
                    width: 100%;
                    max-width: 1600px;
                }}
                .metric-card {{
                    background: {card_bg};
                    border-radius: 20px;
                    padding: 40px 30px;
                    text-align: center;
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
                    border: 1px solid #44475a;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                    min-height: 160px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }}
                .metric-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7);
                    border-color: #8be9fd;
                }}
                .metric-label {{
                    color: #f59e0b;
                    font-size: 1.15rem;
                    font-weight: 600;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                }}
                .metric-value {{
                    color: {text_color_primary};
                    font-size: 2.2rem;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }}

                @media (max-width: 1400px) {{
                    .metricas-container {{
                        padding: 40px 40px 40px 40px;
                    }}
                    .metricas-grid {{
                        gap: 25px;
                    }}
                }}

                @media (max-width: 1200px) {{
                    .metricas-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                }}

                @media (max-width: 768px) {{
                    .metricas-container {{
                        padding: 30px 20px 30px 20px;
                    }}
                    .metricas-title {{
                        font-size: 2rem;
                    }}
                    .metricas-grid {{
                        grid-template-columns: 1fr;
                        gap: 20px;
                    }}
                    .metric-card {{
                        padding: 30px 20px;
                    }}
                    .metric-value {{
                        font-size: 1.8rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="metricas-container">
                <div class="metricas-title">
                    <span>💎</span>
                    <span>Métricas de Vendas</span>
                </div>

                <div class="metricas-grid">
                    <div class="metric-card">
                        <div class="metric-label">💰 Total Entradas</div>
                        <div class="metric-value">{format_currency(total_entradas)}</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-label">⏳ Total Parcelado</div>
                        <div class="metric-value">{format_currency(total_parcelado)}</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-label">💎 Valor Total</div>
                        <div class="metric-value">{format_currency(total_vendido)}</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-label">📊 Total de Vendas</div>
                        <div class="metric-value">{qtd_vendas}</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-label">🎯 Ticket Médio</div>
                        <div class="metric-value">{format_currency(ticket_medio)}</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-label">📈 Margem Média</div>
                        <div class="metric-value">{float(percentual_margem):.1f}%</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """

    components.html(html_content, height=750, scrolling=False)


def render_ranking_vendedores(theme='dark'):
    """
    Renderiza painel Ranking Vendedores - ADAPT ADO DO SGR
    Lógica completa de cálculos e exibição de fotos do SGR
    """
    from dateutil.relativedelta import relativedelta

    vendedores_tabela = VENDEDORES_TABELA

    # Calcular período atual (mês atual) — `timezone.localdate()` em vez de
    # `datetime.now()` (achado de auditoria, 17/08/2026: ver `get_filtros_periodo`).
    hoje = timezone.localdate()
    data_inicio = date(hoje.year, hoje.month, 1)
    data_fim = hoje
    ano_anterior = (data_inicio - relativedelta(years=1)).year

    # Buscar nomes curtos e percentuais dos vendedores
    dados_vendedores = {}
    try:
        for v in Vendedores.objects.all():
            dados_vendedores[v.nome] = {
                "curto": v.curto if v.curto else v.nome,
                "percentual": float(v.percentual) if v.percentual else 0.0,
            }
    except Exception:
        pass

    # Calcular vendas do mesmo período no ano anterior via ORM
    def calcular_vendas_periodo_anterior(data_inicio, data_fim):
        """Calcula vendas do mesmo período no ano anterior usando ORM com filtragem em Python"""
        try:
            data_inicio_ant = data_inicio - relativedelta(years=1)
            data_fim_ant = data_fim - relativedelta(years=1)

            vendedores_validos = set(Vendedores.objects.values_list("nome", flat=True))

            vendas_por_vendedor = {}
            for venda in Vendas.objects.all():
                vendedor = venda.vendedornome.strip() if venda.vendedornome else ""
                if not vendedor or vendedor not in vendedores_validos:
                    continue

                if not venda.data:
                    continue

                if not (data_inicio_ant <= venda.data <= data_fim_ant):
                    continue

                valor = (
                    parse_valor(venda.valortotal) if venda.valortotal else Decimal("0")
                )
                if vendedor not in vendas_por_vendedor:
                    vendas_por_vendedor[vendedor] = Decimal("0")
                vendas_por_vendedor[vendedor] += valor

            return {k: float(v) for k, v in vendas_por_vendedor.items()}
        except Exception:
            return {}

    vendas_periodo_anterior = calcular_vendas_periodo_anterior(data_inicio, data_fim)

    # Buscar vendas do período (seguem os filtros aplicados)
    vendas = get_vendas_periodo()

    # Agrupar por vendedor
    vendedores_stats = {}
    for venda in vendas:
        vendedor = venda.vendedornome
        if not vendedor or vendedor.strip() == "":
            continue

        valor = parse_valor(venda.valortotal)

        if vendedor not in vendedores_stats:
            vendedores_stats[vendedor] = {"total": Decimal("0"), "qtd": 0}

        vendedores_stats[vendedor]["total"] += valor
        vendedores_stats[vendedor]["qtd"] += 1

    # Preparar dados completos dos vendedores
    vendedores_completos = []
    for vendedor in vendedores_tabela:
        nome = vendedor["nome"]
        dados_vend = dados_vendedores.get(nome, {})
        nome_curto = dados_vend.get("curto", nome)
        percentual_meta = dados_vend.get("percentual", 0.0)
        vendas_ant = float(vendas_periodo_anterior.get(nome, 0))
        total_valor = (
            float(vendedores_stats[nome]["total"]) if nome in vendedores_stats else 0.0
        )

        vendedores_completos.append(
            {
                "nome": nome,
                "nome_curto": nome_curto,
                "foto": vendedor["foto"],
                "total_valor": total_valor,
                "vendas_ano_anterior": vendas_ant,
                "percentual_meta": percentual_meta,
            }
        )

    # Ordenar por valor total (maior para menor)
    vendedores_ordenados = sorted(
        vendedores_completos, key=lambda x: x["total_valor"], reverse=True
    )

    # Cores do tema
    if theme == 'dark':
        bg_color = "#1a1d2e"
        text_color_primary = "#8be9fd"
        card_bg = "#000000"  # Preto para cards
    else:
        bg_color = "#f0f0f0"
        text_color_primary = "#1a73e8"
        card_bg = "#000000"  # Preto para cards

    # Gerar HTML dos cards
    cards_html = ""
    for vendedor in vendedores_ordenados:
        # Calcular percentual meta batida: vendas_atuais / (vendas_ant * (1 + %/100)) * 100
        vendas_ant = vendedor["vendas_ano_anterior"]
        percentual_meta = vendedor["percentual_meta"]
        meta = vendas_ant * (1 + percentual_meta / 100) if vendas_ant > 0 else 0
        percentual_meta_batida = (
            (vendedor["total_valor"] / meta * 100) if meta > 0 else 0
        )

        # Carregar foto
        foto_base64 = get_vendedor_foto(vendedor["foto"])

        # Avatar HTML
        if foto_base64:
            avatar_html = f'<img src="{foto_base64}" class="vendedor-avatar-img" />'
        else:
            iniciais = "".join(
                [nome[0] for nome in vendedor["nome"].split()[:2]]
            ).upper()
            avatar_html = f'<div class="vendedor-avatar-iniciais">{iniciais}</div>'

        cards_html += f"""
        <div class="vendedor-card">
            <div class="vendedor-avatar">
                {avatar_html}
            </div>
            <div class="vendedor-nome">{vendedor["nome_curto"]}</div>
            <div class="vendedor-valor">{format_currency(vendedor["total_valor"])}</div>
            <div class="vendedor-mes-label">Mês de {ano_anterior}= {format_currency(vendas_ant)}</div>
            <div class="vendedor-meta">{percentual_meta_batida:.1f}% meta do mês batida</div>
        </div>
        """

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: {bg_color};
                    overflow: hidden;
                }}
                .ranking-vendedores-container {{
                    background: {bg_color};
                    width: 100vw;
                    padding: 15px 30px 10px 30px;
                }}
                .ranking-title {{
                    color: {text_color_primary};
                    font-size: 1.8rem;
                    font-weight: 700;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    text-align: center;
                }}
                .ranking-grid {{
                    display: grid;
                    grid-template-columns: repeat(6, 1fr);
                    gap: 12px 10px;
                    max-width: 1650px;
                    margin: 0 auto;
                }}
                .vendedor-card {{
                    background: {card_bg};
                    border-radius: 14px;
                    padding: 12px 10px;
                    text-align: center;
                    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.5);
                    border: 1px solid #44475a;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                    min-width: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                .vendedor-card:hover {{
                    transform: translateY(-4px);
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.7);
                    border-color: #8be9fd;
                }}
                .vendedor-avatar {{
                    width: 70px;
                    height: 70px;
                    border-radius: 50%;
                    margin: 0 auto 8px;
                    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
                    overflow: hidden;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }}
                .vendedor-avatar-img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    border-radius: 50%;
                }}
                .vendedor-avatar-iniciais {{
                    width: 70px;
                    height: 70px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    font-weight: 700;
                }}
                .vendedor-nome {{
                    color: {text_color_primary};
                    font-weight: 600;
                    font-size: 0.85rem;
                    margin-bottom: 4px;
                    min-height: 32px;
                    max-height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    line-height: 1.2;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    padding: 0 3px;
                    word-break: break-word;
                }}
                .vendedor-valor {{
                    color: {text_color_primary};
                    font-size: 1.1rem;
                    font-weight: 700;
                    margin-bottom: 6px;
                    letter-spacing: -0.5px;
                }}
                .vendedor-mes-label {{
                    color: #f8f8f2;
                    font-size: 0.75rem;
                    font-weight: 700;
                    margin-bottom: 5px;
                }}
                .vendedor-meta {{
                    color: #f8f8f2;
                    font-size: 0.75rem;
                    font-weight: 700;
                }}

                @media (max-width: 1600px) {{
                    .ranking-grid {{
                        grid-template-columns: repeat(4, 1fr);
                    }}
                }}

                @media (max-width: 1200px) {{
                    .ranking-grid {{
                        grid-template-columns: repeat(3, 1fr);
                    }}
                }}

                @media (max-width: 900px) {{
                    .ranking-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                }}

                @media (max-width: 600px) {{
                    .ranking-vendedores-container {{
                        padding: 15px 15px 10px 15px;
                    }}
                    .ranking-title {{
                        font-size: 1.5rem;
                    }}
                    .ranking-grid {{
                        grid-template-columns: 1fr;
                        gap: 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="ranking-vendedores-container">
                <div class="ranking-title">
                    <span>🏆</span>
                    <span>Ranking de Vendedores</span>
                </div>

                <div class="ranking-grid">
                    {cards_html}
                </div>
            </div>
        </body>
        </html>
    """

    # 12 vendedores em grid 6x2 = sem barra de rolagem
    components.html(html_content, height=620, scrolling=False)


def render_texto(texto, titulo="", theme='dark'):
    """
    Renderiza painel de Texto - Formatação elegante e profissional
    Suporta quebras de linha e formatação rica

    Args:
        texto: Texto a ser exibido (suporta \\n para quebra de linha)
        titulo: Título opcional do slide
        theme: Tema do painel ('dark' ou 'light')
    """
    # Processar quebras de linha no texto
    # Suporta tanto \n literal quanto <br> em HTML
    texto_formatado = texto.replace('\\n', '<br>').replace('\n', '<br>')

    # Cores do tema Dracula at Night
    if theme == 'dark':
        bg_color = "#1a1d2e"  # Background escuro do Dracula
        text_color_primary = "#f8f8f2"  # Texto principal (branco suave)
        text_color_titulo = "#8be9fd"  # Ciano para título
        text_color_secundario = "#6272a4"  # Comentário/secundário
        card_bg = "rgba(0, 0, 0, 0.4)"  # Card semi-transparente
        border_color = "#44475a"  # Borda do Dracula
        accent_color = "#bd93f9"  # Roxo accent
    else:
        bg_color = "#f0f0f0"
        text_color_primary = "#1a1a1a"
        text_color_titulo = "#1a73e8"
        text_color_secundario = "#5f6368"
        card_bg = "rgba(255, 255, 255, 0.9)"
        border_color = "#e0e0e0"
        accent_color = "#4285f4"

    # HTML com título opcional
    titulo_html = ""
    if titulo and titulo.strip():
        titulo_html = f"""
            <div class="texto-titulo">
                <span class="titulo-icon">📝</span>
                <span>{titulo}</span>
            </div>
        """

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: {bg_color};
                    overflow-y: auto;
                }}
                .texto-container {{
                    background: {bg_color};
                    min-height: 100vh;
                    width: 100vw;
                    padding: 50px 60px 50px 60px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }}
                .texto-titulo {{
                    color: {text_color_titulo};
                    font-size: 2.8rem;
                    font-weight: 700;
                    margin-bottom: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 15px;
                    text-align: center;
                    letter-spacing: -0.5px;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .titulo-icon {{
                    font-size: 3rem;
                }}
                .texto-card {{
                    background: {card_bg};
                    border-radius: 24px;
                    padding: 50px 70px;
                    max-width: 1200px;
                    width: 90%;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                    border: 1px solid {border_color};
                    backdrop-filter: blur(10px);
                    position: relative;
                    overflow: hidden;
                }}
                .texto-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 6px;
                    height: 100%;
                    background: linear-gradient(180deg, {accent_color}, {text_color_titulo});
                    border-radius: 24px 0 0 24px;
                }}
                .texto-conteudo {{
                    color: {text_color_primary};
                    font-size: 5.4rem;
                    line-height: 1.5;
                    text-align: center;
                    font-weight: 500;
                    letter-spacing: 0.5px;
                }}
                .texto-conteudo strong,
                .texto-conteudo b {{
                    color: {text_color_titulo};
                    font-weight: 700;
                }}
                .texto-decoracao {{
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    margin-top: 40px;
                    opacity: 0.5;
                }}
                .decoracao-dot {{
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    background: {accent_color};
                }}

                /* Animação de entrada suave */
                @keyframes fadeInUp {{
                    from {{
                        opacity: 0;
                        transform: translateY(30px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                .texto-card {{
                    animation: fadeInUp 0.8s ease-out;
                }}
                .texto-titulo {{
                    animation: fadeInUp 0.6s ease-out;
                }}

                @media (max-width: 1200px) {{
                    .texto-container {{
                        padding: 40px 40px 40px 40px;
                    }}
                    .texto-card {{
                        padding: 40px 50px;
                    }}
                    .texto-conteudo {{
                        font-size: 4.8rem;
                    }}
                }}

                @media (max-width: 768px) {{
                    .texto-container {{
                        padding: 30px 20px 30px 20px;
                    }}
                    .texto-titulo {{
                        font-size: 2rem;
                    }}
                    .titulo-icon {{
                        font-size: 2.2rem;
                    }}
                    .texto-card {{
                        padding: 30px 25px;
                        border-radius: 16px;
                    }}
                    .texto-card::before {{
                        width: 4px;
                    }}
                    .texto-conteudo {{
                        font-size: 3.9rem;
                        line-height: 1.4;
                    }}
                }}

                @media (max-width: 480px) {{
                    .texto-titulo {{
                        font-size: 1.6rem;
                        flex-direction: column;
                        gap: 10px;
                    }}
                    .texto-conteudo {{
                        font-size: 3rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="texto-container">
                {titulo_html}

                <div class="texto-card">
                    <div class="texto-conteudo">
                        {texto_formatado}
                    </div>
                    <div class="texto-decoracao">
                        <div class="decoracao-dot"></div>
                        <div class="decoracao-dot"></div>
                        <div class="decoracao-dot"></div>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """

    components.html(html_content, height=750, scrolling=False)


def render_ranking_produtos(theme='dark'):
    """
    Renderiza painel Ranking Produtos - ADAPTADO DO SGR
    Lógica completa de cálculos e layout do SGR
    """
    # Buscar vendas do período (seguem os filtros aplicados)
    vendas = get_vendas_periodo()
    vendas_ids = [v.id_gestao for v in vendas]

    if not vendas_ids:
        # Renderizar mensagem vazia em HTML
        st.markdown(
            """
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                height: 400px;
                color: #8be9fd;
                font-size: 1.5rem;
            ">
                📦 Nenhum produto encontrado para o período selecionado
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Buscar produtos vendidos
    produtos_vendidos = VendaProdutos.objects.filter(venda_id__in=vendas_ids)

    if not produtos_vendidos.exists():
        st.markdown(
            """
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                height: 400px;
                color: #8be9fd;
                font-size: 1.5rem;
            ">
                📦 Nenhum produto encontrado para o período selecionado
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Agrupar por produto (mesmo do SGR)
    produtos_stats = {}
    for item in produtos_vendidos:
        nome = item.nome.strip() if item.nome else "Produto sem nome"
        qtd = parse_quantidade(item.quantidade)

        if nome not in produtos_stats:
            produtos_stats[nome] = {"quantidade": Decimal("0"), "num_vendas": 0}

        produtos_stats[nome]["quantidade"] += qtd
        produtos_stats[nome]["num_vendas"] += 1

    # Ordenar por quantidade total e pegar TOP 10 (mesmo do SGR)
    ranking = sorted(
        produtos_stats.items(), key=lambda x: x[1]["quantidade"], reverse=True
    )[:10]

    if not ranking:
        st.markdown(
            """
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                height: 400px;
                color: #8be9fd;
                font-size: 1.5rem;
            ">
                📦 Nenhum produto encontrado
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Cores do tema
    if theme == 'dark':
        bg_color = "#1a1d2e"
        text_color_primary = "#8be9fd"
    else:
        bg_color = "#f0f0f0"
        text_color_primary = "#1a73e8"

    # Gerar HTML dos cards
    cards_html = ""
    for idx, (produto, stats) in enumerate(ranking):
        rank = idx + 1
        gradient = get_gradient(rank)

        cards_html += f"""
        <div class="produto-card" style="background: {gradient};">
            <div class="produto-rank">#{rank}</div>
            <div class="produto-nome" title="{produto}">
                {produto.upper()}
            </div>
            <div class="produto-metric">
                <span class="produto-metric-label">📦 Qtd. Total</span>
                <span class="produto-metric-value">{int(stats["quantidade"])}</span>
            </div>
            <div class="produto-metric">
                <span class="produto-metric-label">🛒 Nº Vendas</span>
                <span class="produto-metric-value">{stats["num_vendas"]}</span>
            </div>
        </div>
        """

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: {bg_color};
                    overflow-y: auto;
                }}
                .ranking-produtos-container {{
                    background: {bg_color};
                    min-height: 100vh;
                    width: 100vw;
                    padding: 30px 40px 30px 40px;
                }}
                .ranking-title {{
                    color: {text_color_primary};
                    font-size: 2rem;
                    font-weight: 700;
                    margin-bottom: 35px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                    text-align: center;
                }}
                .ranking-grid {{
                    display: grid;
                    grid-template-columns: repeat(5, 1fr);
                    gap: 20px 18px;
                    max-width: 1650px;
                    margin: 0 auto;
                }}
                .produto-card {{
                    border-radius: 16px;
                    padding: 20px 15px;
                    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.5);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    color: white;
                    display: flex;
                    flex-direction: column;
                    min-width: 0;
                }}
                .produto-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.7);
                    border-color: rgba(255, 255, 255, 0.3);
                }}
                .produto-rank {{
                    font-size: 2.3rem;
                    font-weight: 700;
                    opacity: 0.4;
                    line-height: 1;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .produto-nome {{
                    font-size: 1rem;
                    font-weight: 700;
                    margin-bottom: 15px;
                    min-height: 48px;
                    max-height: 48px;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.4);
                    line-height: 1.3;
                    word-break: break-word;
                }}
                .produto-metric {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 6px 0;
                    padding: 10px 12px;
                    background: rgba(0, 0, 0, 0.25);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .produto-metric-label {{
                    font-size: 0.9rem;
                    font-weight: 600;
                    opacity: 1;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
                }}
                .produto-metric-value {{
                    font-size: 1.3rem;
                    font-weight: 900;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
                }}

                @media (max-width: 1600px) {{
                    .ranking-grid {{
                        grid-template-columns: repeat(4, 1fr);
                    }}
                }}

                @media (max-width: 1200px) {{
                    .ranking-grid {{
                        grid-template-columns: repeat(3, 1fr);
                    }}
                }}

                @media (max-width: 900px) {{
                    .ranking-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                }}

                @media (max-width: 600px) {{
                    .ranking-produtos-container {{
                        padding: 30px 20px 30px 20px;
                    }}
                    .ranking-title {{
                        font-size: 1.8rem;
                    }}
                    .ranking-grid {{
                        grid-template-columns: 1fr;
                        gap: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="ranking-produtos-container">
                <div class="ranking-title">
                    <span>🏆</span>
                    <span>Ranking de Produtos</span>
                </div>

                <div class="ranking-grid">
                    {cards_html}
                </div>
            </div>
        </body>
        </html>
    """

    components.html(html_content, height=700, scrolling=False)


@st.cache_data(ttl=300)  # Cache de 5 minutos
def get_vendas_dia_atual():
    """
    Busca vendas do dia atual (hoje), aplicando os mesmos filtros de
    get_vendas_periodo (situações excluídas, apenas vendedores válidos).
    """
    hoje = date.today()

    situacoes_excluidas = ["Cancelada (sem financeiro)", "Não considerar - Excluidos"]
    vendedores_validos = set(Vendedores.objects.values_list('nome', flat=True))

    vendas_filtradas = []
    for venda in Vendas.objects.all():
        try:
            if venda.situacaonome in situacoes_excluidas:
                continue

            vendedor_nome = venda.vendedornome.strip() if venda.vendedornome else ""
            if vendedor_nome not in vendedores_validos:
                continue

            if venda.data == hoje:
                vendas_filtradas.append(venda)
        except Exception:
            continue

    return vendas_filtradas


def render_resumo_dia(theme='dark'):
    """
    Renderiza painel Resumo do Dia: card com o total vendido hoje, painel de
    Vendedores (cards no mesmo estilo do Ranking de Vendedores, mas com o
    total do dia) e painel de Produtos (cards no mesmo estilo do Ranking de
    Produtos, restrito ao que foi vendido hoje).
    """
    hoje = date.today()
    data_titulo = hoje.strftime("%d/%m/%Y")

    vendas_dia = get_vendas_dia_atual()
    total_dia = sum(parse_valor(v.valortotal) for v in vendas_dia)

    # --- Vendedores: total do dia por vendedor (mesma lista fixa do Ranking) ---
    vendedores_stats = {}
    for venda in vendas_dia:
        vendedor = venda.vendedornome
        if not vendedor or vendedor.strip() == "":
            continue
        vendedores_stats[vendedor] = vendedores_stats.get(
            vendedor, Decimal("0")
        ) + parse_valor(venda.valortotal)

    vendedores_dia = [
        {
            "nome": vendedor["nome"],
            "foto": vendedor["foto"],
            "total_valor": float(vendedores_stats.get(vendedor["nome"], Decimal("0"))),
        }
        for vendedor in VENDEDORES_TABELA
    ]
    # Somente vendedores com vendas hoje
    vendedores_dia_ordenados = sorted(
        (v for v in vendedores_dia if v["total_valor"] > 0),
        key=lambda x: x["total_valor"],
        reverse=True,
    )

    vendedores_cards_html = ""
    for vendedor in vendedores_dia_ordenados:
        foto_base64 = get_vendedor_foto(vendedor["foto"])
        if foto_base64:
            avatar_html = f'<img src="{foto_base64}" class="vendedor-avatar-img" />'
        else:
            iniciais = "".join(
                [nome[0] for nome in vendedor["nome"].split()[:2]]
            ).upper()
            avatar_html = f'<div class="vendedor-avatar-iniciais">{iniciais}</div>'

        # Somente foto + valor (sem nome)
        vendedores_cards_html += f"""
        <div class="vendedor-card">
            <div class="vendedor-avatar">
                {avatar_html}
            </div>
            <div class="vendedor-valor">{format_currency(vendedor["total_valor"])}</div>
        </div>
        """

    if not vendedores_cards_html:
        vendedores_cards_html = (
            '<div class="sem-dados">👥 Nenhuma venda registrada hoje ainda</div>'
        )

    # --- Produtos: somente os vendidos hoje (mesmo TOP 10 do Ranking de Produtos) ---
    vendas_ids_dia = [v.id_gestao for v in vendas_dia]
    produtos_stats = {}
    if vendas_ids_dia:
        produtos_vendidos = VendaProdutos.objects.filter(venda_id__in=vendas_ids_dia)
        for item in produtos_vendidos:
            nome = item.nome.strip() if item.nome else "Produto sem nome"
            qtd = parse_quantidade(item.quantidade)
            if nome not in produtos_stats:
                produtos_stats[nome] = {"quantidade": Decimal("0"), "num_vendas": 0}
            produtos_stats[nome]["quantidade"] += qtd
            produtos_stats[nome]["num_vendas"] += 1

    ranking_produtos_dia = sorted(
        produtos_stats.items(), key=lambda x: x[1]["quantidade"], reverse=True
    )[:10]

    produtos_cards_html = ""
    for idx, (produto, stats) in enumerate(ranking_produtos_dia):
        rank = idx + 1
        gradient = get_gradient(rank)

        produtos_cards_html += f"""
        <div class="produto-card" style="background: {gradient};">
            <div class="produto-rank">#{rank}</div>
            <div class="produto-nome" title="{produto}">
                {produto.upper()}
            </div>
            <div class="produto-metric">
                <span class="produto-metric-label">📦 Qtd. Hoje</span>
                <span class="produto-metric-value">{int(stats["quantidade"])}</span>
            </div>
            <div class="produto-metric">
                <span class="produto-metric-label">🛒 Nº Vendas</span>
                <span class="produto-metric-value">{stats["num_vendas"]}</span>
            </div>
        </div>
        """

    if not produtos_cards_html:
        produtos_cards_html = (
            '<div class="sem-dados">📦 Nenhum produto vendido hoje ainda</div>'
        )

    # Cores do tema Dracula at Night
    if theme == 'dark':
        bg_color = "#1a1d2e"
        text_color_primary = "#8be9fd"
        text_color_secondary = "#6272a4"
        card_bg = "#000000"
    else:
        bg_color = "#f0f0f0"
        text_color_primary = "#1a73e8"
        text_color_secondary = "#5f6368"
        card_bg = "#000000"

    # Altura fixa (não 100vh): o script de auto-resize do slideshow nem sempre
    # encolhe o iframe a tempo, e um painel alto demais fica coberto pelo
    # rodapé fixo. 720px cabe com folga mesmo em janelas menores que uma TV.
    panel_height = 720

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: {bg_color};
                    overflow: hidden;
                }}
                .resumo-container {{
                    background: {bg_color};
                    width: 100vw;
                    height: {panel_height}px;
                    padding: 15px 30px 10px 30px;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }}
                .resumo-header {{
                    flex: 0 0 auto;
                }}
                .resumo-title {{
                    color: {text_color_primary};
                    font-size: 2rem;
                    font-weight: 700;
                    margin-bottom: 14px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    text-align: center;
                }}
                .vendas-card {{
                    background: {card_bg};
                    border-radius: 16px;
                    padding: 12px 40px;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
                    border: 1px solid #44475a;
                    max-width: 500px;
                    margin: 0 auto;
                }}
                .vendas-label {{
                    color: #f8f8f2;
                    font-size: 1.1rem;
                    font-weight: 600;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }}
                .vendas-valor {{
                    color: {text_color_primary};
                    font-size: 2.4rem;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }}
                .secao-titulo {{
                    flex: 0 0 auto;
                    color: {text_color_secondary};
                    font-size: 1.2rem;
                    font-weight: 700;
                    margin: 10px 0 8px 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    text-align: center;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}

                /* Seção Vendedores: porção reservada do tamanho do conteúdo,
                   cards centralizados na horizontal — Produtos herda o restante */
                .secao-vendedores {{
                    flex: 0 0 auto;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }}
                .vendedores-linha {{
                    flex: 1 1 auto;
                    min-height: 0;
                    display: flex;
                    flex-wrap: wrap;
                    align-content: center;
                    align-items: center;
                    justify-content: center;
                    gap: 16px;
                }}
                .vendedor-card {{
                    background: {card_bg};
                    border-radius: 14px;
                    padding: 10px 8px;
                    text-align: center;
                    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.5);
                    border: 1px solid #44475a;
                    width: 100px;
                    flex-shrink: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                .vendedor-avatar {{
                    width: 64px;
                    height: 64px;
                    border-radius: 50%;
                    margin: 0 auto 8px;
                    overflow: hidden;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }}
                .vendedor-avatar-img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    border-radius: 50%;
                }}
                .vendedor-avatar-iniciais {{
                    width: 64px;
                    height: 64px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.3rem;
                    font-weight: 700;
                }}
                .vendedor-valor {{
                    color: {text_color_primary};
                    font-size: 1.05rem;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }}

                /* Seção Produtos: preenche o restante da tela, cards padronizados
                   no mesmo estilo/tamanho dos cards de Vendedores */
                .secao-produtos {{
                    flex: 1 1 auto;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }}
                .produtos-linha {{
                    flex: 1 1 auto;
                    min-height: 0;
                    display: grid;
                    grid-template-columns: repeat(5, 170px);
                    grid-auto-rows: min-content;
                    gap: 16px;
                    justify-content: center;
                    align-content: center;
                    overflow: hidden;
                }}
                .produto-card {{
                    border-radius: 14px;
                    padding: 10px 10px;
                    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.5);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    color: white;
                    display: flex;
                    flex-direction: column;
                    width: 170px;
                    flex-shrink: 0;
                }}
                .produto-rank {{
                    font-size: 1.3rem;
                    font-weight: 700;
                    opacity: 0.4;
                    line-height: 1;
                    margin-bottom: 6px;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .produto-nome {{
                    font-size: 0.85rem;
                    font-weight: 700;
                    margin-bottom: 8px;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.4);
                    line-height: 1.25;
                    word-break: break-word;
                    min-height: 2.1em;
                }}
                .produto-metric {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 3px 0;
                    padding: 5px 8px;
                    background: rgba(0, 0, 0, 0.25);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .produto-metric-label {{
                    font-size: 0.7rem;
                    font-weight: 600;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
                }}
                .produto-metric-value {{
                    font-size: 0.95rem;
                    font-weight: 900;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
                }}
                .sem-dados {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    color: {text_color_primary};
                    font-size: 1.3rem;
                }}

                @media (max-width: 600px) {{
                    .resumo-container {{ padding: 15px 15px 10px 15px; }}
                    .resumo-title {{ font-size: 1.5rem; }}
                    .vendedor-card {{ width: 80px; }}
                    .produtos-linha {{ grid-template-columns: repeat(2, 130px); }}
                    .produto-card {{ width: 130px; }}
                }}
            </style>
        </head>
        <body>
            <div class="resumo-container">
                <div class="resumo-header">
                    <div class="resumo-title">
                        <span>📋</span>
                        <span>Resumo - {data_titulo}</span>
                    </div>

                    <div class="vendas-card">
                        <div class="vendas-label">💰 Vendas</div>
                        <div class="vendas-valor">{format_currency(total_dia)}</div>
                    </div>
                </div>

                <div class="secao-vendedores">
                    <div class="secao-titulo">
                        <span>👥</span>
                        <span>Vendedores</span>
                    </div>
                    <div class="vendedores-linha">
                        {vendedores_cards_html}
                    </div>
                </div>

                <div class="secao-produtos">
                    <div class="secao-titulo">
                        <span>📦</span>
                        <span>Produtos</span>
                    </div>
                    <div class="produtos-linha">
                        {produtos_cards_html}
                    </div>
                </div>
            </div>
        </body>
        </html>
    """

    components.html(html_content, height=panel_height, scrolling=False)
