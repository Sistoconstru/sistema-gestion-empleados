
# =============================================================================
# apps/evaluations/urls.py
# =============================================================================

from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    # Página principal
    path('', views.EvaluacionesIndexView.as_view(), name='index'),
    
    # Listado completo de evaluaciones
    path('listado-completo/', views.ListadoCompletoEvaluacionesView.as_view(), name='listado_completo'),
    
    # Evaluaciones como supervisor
    path('supervisor/pendientes/', views.MisEvaluacionesPendientesView.as_view(), name='supervisor_pendientes'),
    path('completar/<uuid:asignacion_id>/', views.completar_evaluacion, name='completar'),
    
    # Evaluaciones como empleado
    path('mis-evaluaciones/', views.EvaluacionHistorialView.as_view(), name='mis_evaluaciones'),
    
    # Resultados para empleados
    path('ver-resultados/<uuid:asignacion_id>/', views.ver_resultados_evaluacion, name='ver_resultados'),
    path('aceptar-resultados/<uuid:asignacion_id>/', views.aceptar_resultados_evaluacion, name='aceptar_resultados'),
    
    # Resultados para supervisores/admin
    path('resultado/<uuid:asignacion_id>/', views.ver_resultado_evaluacion, name='ver_resultado'),
    
    # Aprobación administrativa 
    path('admin/pendientes-aprobacion/', views.EvaluacionesPendientesAprobacionView.as_view(), name='pendientes_aprobacion'),
    path('admin/aprobar/<uuid:asignacion_id>/', views.aprobar_evaluacion, name='aprobar_evaluacion'),
    path('admin/revisar/<uuid:asignacion_id>/', views.revisar_evaluacion, name='revisar_evaluacion'),
    
    # URLs comentadas para futuro desarrollo
    # Valoraciones (exámenes)
    # path('valoraciones/', views.ValoracionListView.as_view(), name='valoracion_list'),
    # path('valoracion/<uuid:pk>/', views.TomarValoracionView.as_view(), name='tomar_valoracion'),
    # path('desempeño/<uuid:pk>/', views.RealizarEvaluacionView.as_view(), name='realizar_evaluacion'),
    
    # Resultados
    # path('resultados/', views.MisResultadosView.as_view(), name='mis_resultados'),
    # path('resultado/<uuid:pk>/', views.ResultadoDetailView.as_view(), name='resultado_detail'),
]
