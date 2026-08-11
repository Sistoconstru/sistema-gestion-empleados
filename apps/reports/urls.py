# =============================================================================
# apps/reports/urls.py
# =============================================================================

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard principal con datos reales
    path('', views.DashboardView.as_view(), name='index'),

    # Reporte de evaluaciones de desempeño
    path('evaluations/', views.PerformanceReportView.as_view(), name='evaluations_report'),

    # Exportaciones de reportes
    path('evaluations/export/excel/', views.ExportEvaluationsExcelView.as_view(), name='export_evaluations_excel'),
    path('evaluations/export/pdf/', views.ExportEvaluationsPDFView.as_view(), name='export_evaluations_pdf'),

    # Reporte de asistencia (RRHH)
    path('asistencia/', views.AsistenciaReportView.as_view(), name='asistencia_report'),
    path('asistencia/ausencias/excel/', views.AsistenciaAusenciasExcelView.as_view(), name='asistencia_ausencias_excel'),

    # Novedades de nómina (RRHH y jefes — la vista detecta el scope)
    path('novedades/', views.NovedadesReportView.as_view(), name='novedades_report'),
    path('novedades/accion/', views.NovedadesAccionView.as_view(), name='novedades_accion'),
    path('novedades/export/excel/', views.NovedadesExportExcelView.as_view(), name='novedades_export_excel'),

    # Aprendices SENA — cuota, cumplimiento y sanción estimada
    path('aprendices-sena/', views.AprendicesSenaReportView.as_view(), name='aprendices_sena_report'),

    # URLs para futuras funcionalidades
    # path('generate/', views.GenerateReportView.as_view(), name='generate_report'),
    # path('list/', views.ReportListView.as_view(), name='report_list'),
    # path('<uuid:pk>/download/', views.DownloadReportView.as_view(), name='download_report'),
]

