# =============================================================================
# apps/organizational/urls.py
# =============================================================================

from django.urls import path
from . import views
from apps.organizational.api_views import sede_api, area_api, cargo_api, cargos_por_area_api, estructura_json_api, validar_cargo_area_api

app_name = 'organizational'

urlpatterns = [
    # Vista principal
    path('', views.OrganizationalIndexView.as_view(), name='index'),
    
    # Organigrama/Estructura
    path('estructura/', views.OrganizationalStructureView.as_view(), name='estructura'),
    path('organigrama/', views.OrganizationalStructureView.as_view(), name='organigrama'),
    
    # === APIs PARA INTEGRACIÓN ===
    # APIs para autocompletado en formularios
    path('api/sedes/', sede_api, name='sede_api'),
    path('api/areas/', area_api, name='area_api'),
    path('api/cargos/', cargo_api, name='cargo_api'),
    
    # APIs específicas
    path('api/area/<int:area_id>/cargos/', cargos_por_area_api, name='cargos_por_area_api'),
    path('api/estructura/', estructura_json_api, name='estructura_json_api'),

    path('estructura/', views.OrganizationalStructureView.as_view(), name='estructura'),
    
    # APIs (JSON) - Incluir con prefijo 'api/'
   # path('api/', include('apps.organizational.api_urls')),
    
    # === ENLACES AL ADMIN (para administradores) ===
    # Estos redirigen al admin de Django para CRUD
    # path('admin/sedes/', RedirectView.as_view(url='/admin/organizational/sede/'), name='admin_sedes'),
    # path('admin/areas/', RedirectView.as_view(url='/admin/organizational/areaempresa/'), name='admin_areas'),
    # path('admin/cargos/', RedirectView.as_view(url='/admin/organizational/cargo/'), name='admin_cargos'),
]