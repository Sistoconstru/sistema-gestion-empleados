# =============================================================================
# apps/core/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView
from .views import dashboard_view, documentos_institucionales

app_name = 'core'

urlpatterns = [
    # Dashboard principal
    path('', dashboard_view, name='dashboard'),

    # Documentos institucionales (reglamentos, políticas, manuales)
    path('documentos-institucionales/', documentos_institucionales, name='documentos_institucionales'),
]
