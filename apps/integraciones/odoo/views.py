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

        # Por defecto INCLUIMOS inactivos: el pull es la red de seguridad cuando el
        # push síncrono falla, y los cambios de estado (activo↔inactivo/retirado)
        # tienen que poder reconciliarse desde aquí. Odoo decide qué hacer con
        # cada estado vía empleado.estado.codigo en el payload.
        # `?incluir_inactivos=false` se mantiene como opt-out por compatibilidad.
        incluir_inactivos = self.request.query_params.get('incluir_inactivos', 'true').lower() == 'true'
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


# Mapeo del valor `estado` que envía Odoo → estado_local en SIGHU.
# Solo aceptamos los tres eventos terminales: aprobada, rechazada, cancelada.
ESTADO_ODOO_A_SIGHU = {
    'aprobada': 'aprobada_rrhh',
    'rechazada': 'rechazada_rrhh',
    'cancelada': 'cancelada_rrhh',
}

# Cada estado terminal tiene un TipoNotificacion asociado que se dispara al
# empleado dueño de la solicitud (ver migración notifications.0002_tipos_vacaciones).
ESTADO_A_TIPO_NOTIFICACION = {
    'aprobada_rrhh': 'vacacion_aprobada',
    'rechazada_rrhh': 'vacacion_rechazada',
    'cancelada_rrhh': 'vacacion_cancelada',
}


def _notificar_empleado_vacacion(solicitud, motivo=''):
    """Crea la notificación in-app para el empleado dueño de la solicitud.

    No falla el callback si la notificación no se puede crear (el estado ya se
    guardó y Odoo espera un 200); registra el error y sigue.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from apps.notifications.models import Notificacion, TipoNotificacion

        codigo_tipo = ESTADO_A_TIPO_NOTIFICACION.get(solicitud.estado_local)
        if not codigo_tipo:
            return
        usuario = getattr(solicitud.empleado, 'usuario', None)
        if not usuario:
            logger.info(
                f"Vacación {solicitud.pk}: empleado {solicitud.empleado} sin usuario, "
                f"se omite notificación."
            )
            return

        tipo = TipoNotificacion.objects.filter(codigo=codigo_tipo, activo=True).first()
        if not tipo:
            logger.warning(f"TipoNotificacion '{codigo_tipo}' no existe o está inactivo.")
            return

        datos = {
            'fecha_inicio': solicitud.fecha_inicio.strftime('%d/%m/%Y'),
            'fecha_fin': solicitud.fecha_fin.strftime('%d/%m/%Y'),
            'motivo': motivo or solicitud.motivo_rechazo or 'No especificado',
            'empleado': solicitud.empleado.nombre_completo,
        }
        Notificacion.objects.create(
            usuario=usuario,
            tipo_notificacion=tipo,
            titulo=tipo.plantilla_titulo.format(**datos),
            mensaje=tipo.plantilla_mensaje.format(**datos),
            datos_adicionales={
                'solicitud_id': str(solicitud.pk),
                'leave_id_odoo': solicitud.leave_id_odoo,
                'estado_local': solicitud.estado_local,
                **datos,
            },
        )
    except Exception as e:
        logger.exception(f"Error notificando vacación {solicitud.pk}: {e}")


class OdooVacacionEstadoView(APIView):
    """Recibe el estado final de una solicitud de vacaciones desde Odoo.

    Contrato:
    - Auth: `Authorization: Token <SIGHU_ODOO_TOKEN>`.
    - Body JSON: { leave_id, estado, motivo?, aprobada_por?, fecha_estado? }
    - Idempotente: misma notificación dos veces → `status: ya_procesado`.
    - Identificación por `leave_id` (entero) → `SolicitudVacacion.leave_id_odoo`.
    """
    authentication_classes = [OdooServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.employees.models import SolicitudVacacion

        data = request.data if isinstance(request.data, dict) else {}

        leave_id = data.get('leave_id')
        if leave_id in (None, ''):
            return Response(
                {'error': 'leave_id requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            leave_id = int(leave_id)
        except (TypeError, ValueError):
            return Response(
                {'error': 'leave_id debe ser entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        estado_str = (data.get('estado') or '').strip()
        nuevo_estado = ESTADO_ODOO_A_SIGHU.get(estado_str)
        if not nuevo_estado:
            return Response(
                {'error': f"estado invalido: '{estado_str}'. Permitidos: {sorted(ESTADO_ODOO_A_SIGHU)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            solicitud = SolicitudVacacion.objects.get(leave_id_odoo=leave_id)
        except SolicitudVacacion.DoesNotExist:
            return Response(
                {'error': f'leave_id {leave_id} no encontrado en SIGHU'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Idempotencia: si ya está en el estado destino, no hacer nada.
        if solicitud.estado_local == nuevo_estado:
            return Response(
                {'status': 'ya_procesado', 'leave_id': leave_id},
                status=status.HTTP_200_OK,
            )

        solicitud.estado_local = nuevo_estado
        motivo = (data.get('motivo') or '').strip()
        if motivo:
            solicitud.motivo_rechazo = motivo
        # Guardar el payload completo para auditoría (sobreescribe el push inicial)
        solicitud.respuesta_odoo = data
        solicitud.save(update_fields=['estado_local', 'motivo_rechazo', 'respuesta_odoo', 'fecha_actualizacion'])

        # Notificar al empleado. La idempotencia del callback (chequeo de estado
        # igual arriba) garantiza que solo se dispara una vez por transición.
        _notificar_empleado_vacacion(solicitud, motivo=motivo)

        return Response(
            {'status': 'recibido', 'leave_id': leave_id, 'estado_local': nuevo_estado},
            status=status.HTTP_200_OK,
        )
