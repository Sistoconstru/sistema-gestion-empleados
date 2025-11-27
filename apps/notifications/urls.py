
# =============================================================================
# apps/notifications/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'notifications'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='notifications/index.html'), name='index'),

    # Notificaciones
    path('list/', views.NotificacionesListView.as_view(), name='list'),
    path('marcar-leida/<uuid:notification_id>/', views.marcar_leida, name='marcar_leida'),
    path('marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('count/', views.notificaciones_count, name='count'),
]

