
# =============================================================================
# apps/organizational/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'sedes', api_views.SedeViewSet)
# router.register(r'areas', api_views.AreaEmpresaViewSet)
# router.register(r'cargos', api_views.CargoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
