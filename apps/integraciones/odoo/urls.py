from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    OdooEmpleadoViewSet,
    OdooHealthcheckView,
    OdooVacacionEstadoView,
    OdooVacacionImportarView,
)

router = DefaultRouter()
router.register(r'empleados', OdooEmpleadoViewSet, basename='odoo-empleado')

urlpatterns = [
    path('', include(router.urls)),
    path('healthcheck/', OdooHealthcheckView.as_view(), name='odoo-healthcheck'),
    path('vacaciones/estado/', OdooVacacionEstadoView.as_view(), name='odoo-vacacion-estado'),
    path('vacaciones/importar/', OdooVacacionImportarView.as_view(), name='odoo-vacacion-importar'),
]
