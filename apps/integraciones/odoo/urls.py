from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    OdooEmpleadoInactivarView,
    OdooEmpleadoViewSet,
    OdooHealthcheckView,
    OdooVacacionEstadoView,
    OdooVacacionImportarView,
)

router = DefaultRouter()
router.register(r'empleados', OdooEmpleadoViewSet, basename='odoo-empleado')

urlpatterns = [
    # Precede al include(router.urls) para que no capture 'inactivar' como pk.
    path('empleados/inactivar/', OdooEmpleadoInactivarView.as_view(), name='odoo-empleado-inactivar'),
    path('', include(router.urls)),
    path('healthcheck/', OdooHealthcheckView.as_view(), name='odoo-healthcheck'),
    path('vacaciones/estado/', OdooVacacionEstadoView.as_view(), name='odoo-vacacion-estado'),
    path('vacaciones/importar/', OdooVacacionImportarView.as_view(), name='odoo-vacacion-importar'),
]
