# =============================================================================
# apps/reports/urls.py
# =============================================================================

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard principal con datos reales
    path('', views.DashboardView.as_view(), name='index'),
    
    # URLs para futuras funcionalidades
    # path('generate/', views.GenerateReportView.as_view(), name='generate_report'),
    # path('list/', views.ReportListView.as_view(), name='report_list'),
    # path('<uuid:pk>/download/', views.DownloadReportView.as_view(), name='download_report'),
]

