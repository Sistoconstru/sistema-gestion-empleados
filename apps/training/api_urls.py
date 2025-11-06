# =============================================================================
# apps/training/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'capacitaciones', api_views.CapacitacionViewSet)
# router.register(r'inscripciones', api_views.InscripcionCapacitacionViewSet)
# router.register(r'modulos', api_views.ModuloCapacitacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

