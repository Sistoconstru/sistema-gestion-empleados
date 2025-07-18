# =============================================================================
# apps/reports/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'tipos-reporte', api_views.TipoReporteViewSet)
# router.register(r'reportes-generados', api_views.ReporteGeneradoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]