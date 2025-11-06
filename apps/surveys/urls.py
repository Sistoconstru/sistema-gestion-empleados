# =============================================================================
# apps/surveys/urls.py
# =============================================================================

from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='index'),
    
    # Encuestas
    path('lista/', views.EncuestaListView.as_view(), name='encuesta_list'),
    path('responder/<uuid:pk>/', views.ResponderEncuestaView.as_view(), name='responder_encuesta'),
    path('mis-encuestas/', views.MisEncuestasView.as_view(), name='mis_encuestas'),
    
    # Resultados (para implementar después)
    # path('resultados/<uuid:pk>/', views.ResultadosEncuestaView.as_view(), name='resultados_encuesta'),
]