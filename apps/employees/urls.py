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
    
    # APIs y exportación
    path('api/search/', views.empleado_search_api, name='empleado_search_api'),
    path('export/', views.empleado_export, name='empleado_export'),
    
    # Historial de cargos (para futuras funcionalidades)
    # path('<uuid:pk>/historial/', views.HistorialCargoView.as_view(), name='historial_cargo'),
    # path('<uuid:pk>/cambiar-cargo/', views.CambiarCargoView.as_view(), name='cambiar_cargo'),
]