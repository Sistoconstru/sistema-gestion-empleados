
# =============================================================================
# apps/employees/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'empleados', api_views.EmpleadoViewSet)
# router.register(r'tipos-documento', api_views.TipoDocumentoViewSet)
# router.register(r'escolaridad', api_views.EscolaridadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]