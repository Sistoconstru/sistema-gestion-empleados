# =============================================================================
# apps/documents/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'documentos', api_views.DocumentoEmpleadoViewSet)
# router.register(r'tipos-documento', api_views.TipoDocumentoEmpleadoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
