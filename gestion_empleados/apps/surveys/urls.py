# =============================================================================
# apps/surveys/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'surveys'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='surveys/index.html'), name='index'),
    
    # Encuestas
    # path('list/', views.EncuestaListView.as_view(), name='encuesta_list'),
    # path('<uuid:pk>/', views.ResponderEncuestaView.as_view(), name='responder_encuesta'),
    # path('mis-encuestas/', views.MisEncuestasView.as_view(), name='mis_encuestas'),
    
    # Resultados
    # path('resultados/<uuid:pk>/', views.ResultadosEncuestaView.as_view(), name='resultados_encuesta'),
]