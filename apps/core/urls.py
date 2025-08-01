# =============================================================================
# apps/core/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView
from .views import dashboard_view

app_name = 'core'

urlpatterns = [
    # Dashboard principal
    #path('', TemplateView.as_view(template_name='core/dashboard.html'), name='dashboard'),
    path('', dashboard_view, name='dashboard'),
    #path('', login_required(TemplateView.as_view(template_name='core/dashboard.html')), name='dashboard'),
    
    # URLs para implementar después
    # path('settings/', views.SystemSettingsView.as_view(), name='settings'),
    # path('logs/', views.ActivityLogView.as_view(), name='activity_logs'),
]
