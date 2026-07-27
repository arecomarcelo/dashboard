"""
DashBoard - Sistema de Gestão de Dashboard
Aplicação Streamlit para exibição de dashboards em slideshow com rotação automática
Utiliza Django ORM para gerenciar modelos PostgreSQL
"""

import streamlit as st

import django_setup  # Configura Django ORM

# Configuração da página
st.set_page_config(
    page_title="DashBoard - Sistema de Gestão de Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Redirecionar automaticamente para o slideshow
st.switch_page("pages/01_🎬_Slideshow.py")
