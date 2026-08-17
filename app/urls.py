"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

# `dashboard.urls` removido em 17/08/2026 (auditoria de qualidade) — era a
# implementação Django/JS puro do slideshow (Fase 2 original), nunca servida em
# produção (Dockerfile sempre rodou só `streamlit run app.py`, desde o primeiro
# commit) e já superada em conteúdo pelo Streamlit real (`panels.py`). Django
# segue no projeto só como ORM + Django Admin (`admin.py`, 11 models — ferramenta
# de backoffice legítima, mantida).
urlpatterns = [
    path("admin/", admin.site.urls),
]
