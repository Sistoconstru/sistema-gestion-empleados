
# =============================================================================
# apps/surveys/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'encuestas', api_views.EncuestaViewSet)
# router.register(r'participaciones', api_views.ParticipacionEncuestaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]