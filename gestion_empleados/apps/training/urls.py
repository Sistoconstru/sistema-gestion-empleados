
# =============================================================================
# apps/training/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'training'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='training/index.html'), name='index'),
    
    # Capacitaciones
    # path('list/', views.CapacitacionListView.as_view(), name='capacitacion_list'),
    # path('create/', views.CapacitacionCreateView.as_view(), name='capacitacion_create'),
    # path('<uuid:pk>/', views.CapacitacionDetailView.as_view(), name='capacitacion_detail'),
    
    # Inscripciones
    # path('mis-capacitaciones/', views.MisCapacitacionesView.as_view(), name='mis_capacitaciones'),
    # path('<uuid:pk>/inscribir/', views.InscribirCapacitacionView.as_view(), name='inscribir_capacitacion'),
    
    # Módulos y lecciones
    # path('<uuid:pk>/modulos/', views.ModuloListView.as_view(), name='modulo_list'),
    # path('modulo/<uuid:pk>/lecciones/', views.LeccionListView.as_view(), name='leccion_list'),
]