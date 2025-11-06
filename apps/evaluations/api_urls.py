# =============================================================================
# apps/evaluations/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'valoraciones', api_views.ValoracionViewSet)
# router.register(r'evaluaciones', api_views.EvaluacionDesempeñoViewSet)
# router.register(r'asignaciones', api_views.AsignacionEvaluacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
