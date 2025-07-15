# =============================================================================
# apps/organizational/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'organizational'

urlpatterns = [
    # URLs básicas - implementar views después
    path('', TemplateView.as_view(template_name='organizational/index.html'), name='index'),
    
    # Sedes
    # path('sedes/', views.SedeListView.as_view(), name='sede_list'),
    # path('sedes/create/', views.SedeCreateView.as_view(), name='sede_create'),
    # path('sedes/<int:pk>/', views.SedeDetailView.as_view(), name='sede_detail'),
    
    # Áreas
    # path('areas/', views.AreaListView.as_view(), name='area_list'),
    # path('areas/create/', views.AreaCreateView.as_view(), name='area_create'),
    # path('areas/<int:pk>/', views.AreaDetailView.as_view(), name='area_detail'),
    
    # Cargos
    # path('cargos/', views.CargoListView.as_view(), name='cargo_list'),
    # path('cargos/create/', views.CargoCreateView.as_view(), name='cargo_create'),
    # path('cargos/<int:pk>/', views.CargoDetailView.as_view(), name='cargo_detail'),
]