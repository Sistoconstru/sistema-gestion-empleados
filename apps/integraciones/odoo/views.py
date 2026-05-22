from django.utils.dateparse import parse_datetime
from django.db.models import Q
from rest_framework import mixins, viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.models import Empleado

from .auth import OdooServiceTokenAuthentication
from .serializers import OdooEmpleadoSerializer


class OdooPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


class OdooEmpleadoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Endpoint read-only para que Odoo sincronice empleados.

    Contrato: docs/INTEGRACION_ODOO.md §3.3 y §3.4.
    """
    authentication_classes = [OdooServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OdooEmpleadoSerializer
    pagination_class = OdooPagination
    lookup_field = 'id'

    def get_queryset(self):
        qs = Empleado.objects.select_related(
            'tipo_documento', 'estado', 'sede', 'escolaridad',
            'ciudad_nacimiento__departamento',
        ).prefetch_related(
            'historialcargo_set__cargo__area',
            'historialcargo_set__jefe_directo',
        )

        incluir_inactivos = self.request.query_params.get('incluir_inactivos', 'false').lower() == 'true'
        if not incluir_inactivos:
            qs = qs.filter(estado__permite_acceso_sistema=True)

        modified_since_raw = self.request.query_params.get('modified_since')
        if modified_since_raw:
            modified_since = parse_datetime(modified_since_raw)
            if modified_since:
                qs = qs.filter(
                    Q(fecha_actualizacion__gte=modified_since)
                    | Q(historialcargo__fecha_actualizacion__gte=modified_since, historialcargo__activo=True)
                ).distinct()

        return qs.order_by('fecha_actualizacion')


class OdooHealthcheckView(APIView):
    """Endpoint público para que Odoo verifique conectividad antes del cron."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
