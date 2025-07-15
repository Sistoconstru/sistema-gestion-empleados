# =============================================================================
# apps/reports/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'reports'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='reports/index.html'), name='index'),
    
    # Reportes
    # path('generate/', views.GenerateReportView.as_view(), name='generate_report'),
    # path('list/', views.ReportListView.as_view(), name='report_list'),
    # path('<uuid:pk>/download/', views.DownloadReportView.as_view(), name='download_report'),
]

