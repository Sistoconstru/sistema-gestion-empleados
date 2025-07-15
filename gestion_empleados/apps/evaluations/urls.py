
# =============================================================================
# apps/evaluations/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'evaluations'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='evaluations/index.html'), name='index'),
    
    # Valoraciones (exámenes)
    # path('valoraciones/', views.ValoracionListView.as_view(), name='valoracion_list'),
    # path('valoracion/<uuid:pk>/', views.TomarValoracionView.as_view(), name='tomar_valoracion'),
    
    # Evaluaciones de desempeño
    # path('desempeño/', views.EvaluacionDesempeñoListView.as_view(), name='evaluacion_list'),
    # path('desempeño/<uuid:pk>/', views.RealizarEvaluacionView.as_view(), name='realizar_evaluacion'),
    
    # Resultados
    # path('resultados/', views.MisResultadosView.as_view(), name='mis_resultados'),
    # path('resultado/<uuid:pk>/', views.ResultadoDetailView.as_view(), name='resultado_detail'),
]
