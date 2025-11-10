# =============================================================================
# apps/employees/urls.py - URLs VERIFICADAS
# =============================================================================

from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Lista de empleados
    path('', views.EmpleadoListView.as_view(), name='empleado_list'),
    
    # CRUD de empleados
    path('crear/', views.EmpleadoCreateView.as_view(), name='empleado_create'),
    path('<uuid:pk>/', views.EmpleadoDetailView.as_view(), name='empleado_detail'),
    path('<uuid:pk>/editar/', views.EmpleadoUpdateView.as_view(), name='empleado_edit'),

    # Exportaciones individuales
    path('<uuid:pk>/export/', views.empleado_export_individual, name='empleado_export_individual'),
    path('<uuid:pk>/print/', views.empleado_print_view, name='empleado_print'),
    path('<uuid:pk>/historial/export/', views.empleado_historial_export, name='empleado_historial_export'),
    path('mi-perfil/', views.empleado_perfil_redirect, name='empleado_perfil'),
    path('perfil/<uuid:pk>/', views.EmpleadoPerfilView.as_view(), name='empleado_perfil_detail'),
    # APIs y exportación
    path('api/search/', views.empleado_search_api, name='empleado_search_api'),
    path('export/', views.empleado_export, name='empleado_export'),
    
    # Gestión de cargos
    path('<uuid:pk>/cambiar-cargo/', views.cambiar_cargo_empleado, name='cambiar_cargo'),
    
    # Reportes especiales
    path('periodo-prueba/', views.empleados_periodo_prueba_reporte, name='periodo_prueba_reporte'),
    
    # Historial de cargos (para futuras funcionalidades)
    # path('<uuid:pk>/historial/', views.HistorialCargoView.as_view(), name='historial_cargo'),
]