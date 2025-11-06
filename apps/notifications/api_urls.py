
# =============================================================================
# apps/notifications/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'notificaciones', api_views.NotificacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]