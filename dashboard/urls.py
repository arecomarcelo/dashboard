# NOTA (auditoria de qualidade, 17/08/2026): estas rotas e as views/templates que
# elas servem (`dashboard/views.py`, `templates/dashboard/slideshow.html`) são
# remanescentes de uma versão anterior do projeto (slideshow puro em Django/JS,
# antes da migração para Streamlit). Nunca são servidas em produção — o Dockerfile
# roda só `streamlit run app.py` (porta 8113), Django nunca sobe como servidor HTTP.
# Mantidas por ora sem remoção (decisão consciente, fora do escopo desta auditoria).
from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.slideshow_view, name='slideshow'),
    path('api/config/', views.get_dashboards_config, name='api_config'),
]
