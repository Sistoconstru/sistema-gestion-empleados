

# =============================================================================
# apps/evaluations/urls.py
# =============================================================================

from django.urls import path
from . import views
from .admin_views import activar_evaluaciones_form

app_name = 'evaluations'

urlpatterns = [
    # Página principal
    path('', views.EvaluacionesIndexView.as_view(), name='index'),
    
    # Listado completo de evaluaciones
    path('listado-completo/', views.ListadoCompletoEvaluacionesView.as_view(), name='listado_completo'),
    
    # Evaluaciones como supervisor (jefe inmediato)
    path('supervisor/pendientes/', views.MisEvaluacionesPendientesView.as_view(), name='supervisor_pendientes'),
    path('supervisor/completadas/', views.MisEvaluacionesCompletadasView.as_view(), name='supervisor_completadas'),
    path('supervisor/seguimientos-pendientes/', views.seguimientos_pendientes_supervisor, name='supervisor_seguimientos_pendientes'),
    path('completar/<uuid:asignacion_id>/', views.completar_evaluacion, name='completar'),

    # Vista administrativa: TODAS las evaluaciones pendientes del sistema
    path('admin/todas-pendientes/', views.AdminTodasPendientesView.as_view(), name='admin_todas_pendientes'),
    
    # Evaluaciones como empleado
    path('mis-evaluaciones/', views.EvaluacionHistorialView.as_view(), name='mis_evaluaciones'),
    
    # Resultados para empleados
    path('ver-resultados/<uuid:asignacion_id>/', views.ver_resultados_evaluacion, name='ver_resultados'),
    path('aceptar-resultados/<uuid:asignacion_id>/', views.aceptar_resultados_evaluacion, name='aceptar_resultados'),

    # Asignación manual de evaluaciones (AJAX/modal)
    path('asignar-evaluacion-manual/', views.asignar_evaluacion_manual, name='asignar_evaluacion_manual'),
    path('ver-plan-mejora/<uuid:plan_id>/', views.ver_plan_mejora_empleado, name='ver_plan_mejora_empleado'),
    path('aceptar-plan/<uuid:plan_id>/', views.aceptar_plan_mejora, name='aceptar_plan_mejora'),
    path('imprimir-plan/<uuid:plan_id>/', views.imprimir_plan_mejora, name='imprimir_plan_mejora'),
    
    
    # Aprobación administrativa y planes de mejora
    path('admin/pendientes-aprobacion/', views.EvaluacionesPendientesAprobacionView.as_view(), name='admin_pendientes_aprobacion'),
    path('admin/aprobar/<uuid:asignacion_id>/', views.aprobar_evaluacion, name='aprobar_evaluacion'),
    path('admin/revisar/<uuid:asignacion_id>/', views.revisar_evaluacion, name='revisar_evaluacion'),
    
    # Planes de mejora predefinidos
    path('admin/generar-plan-predefinido/<uuid:asignacion_id>/', views.generar_plan_predefinido, name='generar_plan_predefinido'),
    path('admin/revisar-plan-predefinido/<uuid:plan_id>/', views.revisar_plan_predefinido, name='revisar_plan_predefinido'),
    path('admin/seguimiento-bimensual/<uuid:seguimiento_id>/', views.gestionar_seguimiento_bimensual, name='seguimiento_bimensual'),
    path('admin/evaluacion-final/<uuid:plan_id>/', views.evaluacion_final_plan, name='evaluacion_final'),

    # Resultados finales
    path('admin/resultados-finales/', views.resultados_finales_admin, name='resultados_finales_admin'),

    # Evaluación final - Aceptación por empleado
    path('empleado/aceptar-evaluacion-final/<uuid:evaluacion_final_id>/', views.aceptar_evaluacion_final_empleado, name='aceptar_evaluacion_final_empleado'),

    # Gestión Humana - Validación de evaluaciones finales rechazadas
    path('admin/evaluaciones-finales-rechazadas/', views.evaluaciones_finales_rechazadas_rrhh, name='evaluaciones_finales_rechazadas_rrhh'),
    path('admin/validar-evaluacion-final/<uuid:evaluacion_final_id>/', views.validar_evaluacion_final_rrhh, name='validar_evaluacion_final_rrhh'),

    # Vista consolidada de todos los rechazos
    path('admin/todos-los-rechazos/', views.todos_los_rechazos, name='todos_los_rechazos'),

    # URLs comentadas para futuro desarrollo
    # Valoraciones (exámenes)
    # path('valoraciones/', views.ValoracionListView.as_view(), name='valoracion_list'),
    # path('valoracion/<uuid:pk>/', views.TomarValoracionView.as_view(), name='tomar_valoracion'),
    # path('desempeño/<uuid:pk>/', views.RealizarEvaluacionView.as_view(), name='realizar_evaluacion'),
    
    # Resultados
    # path('resultados/', views.MisResultadosView.as_view(), name='mis_resultados'),
    # path('resultado/<uuid:pk>/', views.ResultadoDetailView.as_view(), name='resultado_detail'),

    # Admin: Activar evaluaciones
    path('admin/activar-evaluaciones/', activar_evaluaciones_form, name='activar_evaluaciones_form'),
]
