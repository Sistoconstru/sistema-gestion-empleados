
# =============================================================================
# apps/organizational/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views 

router = DefaultRouter()
# router.register(r'sedes', api_views.SedeViewSet)
# router.register(r'areas', api_views.AreaEmpresaViewSet)
# router.register(r'cargos', api_views.CargoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('sedes/', api_views.sede_api, name='sede_api'),
    path('areas/', api_views.area_api, name='area_api'),
    path('cargos/', api_views.cargo_api, name='cargo_api'),
    
    # APIs específicas
    path('area/<int:area_id>/cargos/', api_views.cargos_por_area_api, name='cargos_por_area_api'),
    path('estructura/', api_views.estructura_json_api, name='estructura_json_api'),
    
    # APIs de validación
    path('validar-cargo-area/', api_views.validar_cargo_area_api, name='validar_cargo_area_api'),
]
