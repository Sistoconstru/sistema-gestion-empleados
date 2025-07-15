
# =============================================================================
# apps/notifications/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'notifications'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='notifications/index.html'), name='index'),
    
    # Notificaciones
    # path('list/', views.NotificationListView.as_view(), name='notification_list'),
    # path('<uuid:pk>/mark-read/', views.MarkNotificationReadView.as_view(), name='mark_read'),
    # path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
]

