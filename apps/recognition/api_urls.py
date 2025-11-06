# =============================================================================
# apps/recognition/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'puntos', api_views.HistorialPuntosViewSet)
# router.register(r'reconocimientos', api_views.ReconocimientoViewSet)
# router.register(r'insignias', api_views.InsigniaEmpleadoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]