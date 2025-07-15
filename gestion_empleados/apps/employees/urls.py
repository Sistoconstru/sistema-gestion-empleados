
# =============================================================================
# apps/employees/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'employees'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='employees/index.html'), name='index'),
    
    # Empleados
    # path('list/', views.EmpleadoListView.as_view(), name='empleado_list'),
    # path('create/', views.EmpleadoCreateView.as_view(), name='empleado_create'),
    # path('<uuid:pk>/', views.EmpleadoDetailView.as_view(), name='empleado_detail'),
    # path('<uuid:pk>/edit/', views.EmpleadoUpdateView.as_view(), name='empleado_edit'),
    
    # Historial de cargos
    # path('<uuid:pk>/historial/', views.HistorialCargoView.as_view(), name='historial_cargo'),
]