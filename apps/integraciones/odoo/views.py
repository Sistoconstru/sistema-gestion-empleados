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

# Mapa (tipo_solicitud, estado_local) → código del TipoNotificacion.
# Ver migraciones notifications.0002_tipos_vacaciones y 0003_tipos_compensacion.
ESTADO_A_TIPO_NOTIFICACION = {
    ('tiempo', 'aprobada_rrhh'): 'vacacion_aprobada',
    ('tiempo', 'rechazada_rrhh'): 'vacacion_rechazada',
    ('tiempo', 'cancelada_rrhh'): 'vacacion_cancelada',
    ('pago_dinero', 'aprobada_rrhh'): 'vacacion_comp_aprobada',
    ('pago_dinero', 'cancelada_rrhh'): 'vacacion_comp_cancelada',
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

        clave = (solicitud.tipo, solicitud.estado_local)
        codigo_tipo = ESTADO_A_TIPO_NOTIFICACION.get(clave)
        if not codigo_tipo:
            return
        usuario = getattr(solicitud.empleado, 'usuario', None)
        if not usuario:
            logger.info(
                f"Vacación {solicitud.pk}: empleado {solicitud.empleado} sin usuario, "
                f"se omite notificación."
            )
            return

        tipo_notif = TipoNotificacion.objects.filter(codigo=codigo_tipo, activo=True).first()
        if not tipo_notif:
            logger.warning(f"TipoNotificacion '{codigo_tipo}' no existe o está inactivo.")
            return

        # Preparar datos según el tipo de vacación
        datos = {
            'motivo': motivo or solicitud.motivo_rechazo or 'No especificado',
            'empleado': solicitud.empleado.nombre_completo,
        }
        if solicitud.tipo == 'tiempo':
            datos['fecha_inicio'] = solicitud.fecha_inicio.strftime('%d/%m/%Y') if solicitud.fecha_inicio else '—'
            datos['fecha_fin'] = solicitud.fecha_fin.strftime('%d/%m/%Y') if solicitud.fecha_fin else '—'
        else:
            datos['dias'] = str(solicitud.dias_compensados or '—')
            valor = solicitud.valor_compensacion
            datos['valor'] = f'${valor:,.0f}'.replace(',', '.') if valor is not None else '—'
            datos['fecha_lote'] = (
                solicitud.fecha_lote_nomina.strftime('%d/%m/%Y')
                if solicitud.fecha_lote_nomina else '—'
            )

        Notificacion.objects.create(
            usuario=usuario,
            tipo_notificacion=tipo_notif,
            titulo=tipo_notif.plantilla_titulo.format(**datos),
            mensaje=tipo_notif.plantilla_mensaje.format(**datos),
            datos_adicionales={
                'solicitud_id': str(solicitud.pk),
                'leave_id_odoo': solicitud.leave_id_odoo,
                'compensacion_id_odoo': solicitud.compensacion_id_odoo,
                'estado_local': solicitud.estado_local,
                'tipo': solicitud.tipo,
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


# Estados que Odoo puede enviar por el endpoint de importación (vacaciones
# nacidas en Odoo por RRHH, sin pasar por SIGHU).
ESTADO_ODOO_IMPORTAR_A_SIGHU = {
    'aprobada': 'aprobada_rrhh',
    'cancelada': 'cancelada_rrhh',
}

TIPO_ODOO_A_SIGHU = {
    'tiempo': 'tiempo',
    'pago_dinero': 'pago_dinero',
    'dinero': 'pago_dinero',  # sinónimo aceptado desde Odoo
}


def _actualizar_saldo_empleado(empleado, data):
    """Si el payload trae saldo_dias_disponibles, lo guarda en el empleado.

    Odoo es la fuente autoritativa del saldo (considera tiempo + dinero).
    SIGHU solo persiste el valor y la fecha del update para mostrarlo.
    """
    from decimal import Decimal, InvalidOperation
    from django.utils import timezone
    from apps.employees.models import Empleado

    raw = data.get('saldo_dias_disponibles')
    if raw is None or raw == '':
        return
    try:
        saldo = Decimal(str(raw))
    except (InvalidOperation, TypeError):
        return
    Empleado.objects.filter(pk=empleado.pk).update(
        saldo_vacaciones_dias=saldo,
        saldo_vacaciones_actualizado=timezone.now(),
    )


class OdooVacacionImportarView(APIView):
    """Importa/actualiza en SIGHU una vacación creada directamente en Odoo por RRHH.

    Soporta dos tipos:
    - tipo='tiempo': vacación con rango de fechas, upsert por `leave_id`.
    - tipo='dinero' (sinónimo: 'pago_dinero'): compensación en dinero, sin fechas,
      upsert por `compensacion_id`. NO usa leave_id porque puede ser null.

    Opcionalmente el payload puede traer `saldo_dias_disponibles` — SIGHU lo
    guarda en el empleado como el valor autoritativo de Odoo. SIGHU no calcula
    saldo, solo persiste lo que Odoo envía.

    Ver docs/INTEGRACION_ODOO_VACACIONES.md para el contrato completo.
    """
    authentication_classes = [OdooServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from datetime import date
        from decimal import Decimal, InvalidOperation
        from django.contrib.auth import get_user_model
        from apps.employees.models import SolicitudVacacion

        data = request.data if isinstance(request.data, dict) else {}

        # --- Validación tipo ---
        tipo_raw = (data.get('tipo') or 'tiempo').strip()
        tipo = TIPO_ODOO_A_SIGHU.get(tipo_raw)
        if not tipo:
            return Response(
                {'error': f"tipo invalido: '{tipo_raw}'. Permitidos: {sorted(TIPO_ODOO_A_SIGHU)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- Validación clave de idempotencia según tipo ---
        # tipo=tiempo → leave_id; tipo=pago_dinero → compensacion_id
        if tipo == 'tiempo':
            leave_id = data.get('leave_id')
            if leave_id in (None, ''):
                return Response(
                    {'error': 'leave_id requerido cuando tipo=tiempo'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                leave_id = int(leave_id)
            except (TypeError, ValueError):
                return Response({'error': 'leave_id debe ser entero'}, status=status.HTTP_400_BAD_REQUEST)
            compensacion_id = None
        else:
            compensacion_id = data.get('compensacion_id')
            if compensacion_id in (None, ''):
                return Response(
                    {'error': 'compensacion_id requerido cuando tipo=dinero'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                compensacion_id = int(compensacion_id)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'compensacion_id debe ser entero'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            leave_id = None

        # --- Validación estado ---
        estado_str = (data.get('estado') or '').strip()
        nuevo_estado = ESTADO_ODOO_IMPORTAR_A_SIGHU.get(estado_str)
        if not nuevo_estado:
            return Response(
                {'error': f"estado invalido: '{estado_str}'. Permitidos: {sorted(ESTADO_ODOO_IMPORTAR_A_SIGHU)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        motivo = (data.get('motivo') or '').strip()

        # --- Upsert según tipo ---
        if tipo == 'tiempo':
            solicitud = SolicitudVacacion.objects.filter(leave_id_odoo=leave_id).first()
        else:
            solicitud = SolicitudVacacion.objects.filter(compensacion_id_odoo=compensacion_id).first()

        if solicitud is None:
            # --- CREAR ---
            sighu_uuid = (data.get('sighu_uuid') or '').strip()
            cedula = (data.get('cedula') or '').strip()
            empleado = None
            if sighu_uuid:
                empleado = Empleado.objects.filter(pk=sighu_uuid).first()
            if not empleado and cedula:
                empleado = Empleado.objects.filter(numero_documento=cedula).first()
            if not empleado:
                return Response(
                    {'error': 'Empleado no encontrado por sighu_uuid ni cedula'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            aprobada_por = (data.get('aprobada_por') or '').strip()
            User = get_user_model()
            creador_sistema = User.objects.filter(is_superuser=True).first()

            campos_base = dict(
                empleado=empleado,
                jefe_solicitante=None,
                tipo=tipo,
                estado_local=nuevo_estado,
                motivo_rechazo=motivo,
                respuesta_odoo=data,
                creado_por=creador_sistema,
            )

            if tipo == 'tiempo':
                # Fechas requeridas
                try:
                    fecha_inicio = date.fromisoformat(data.get('fecha_inicio', ''))
                    fecha_fin = date.fromisoformat(data.get('fecha_fin', ''))
                except (TypeError, ValueError):
                    return Response(
                        {'error': 'fecha_inicio y fecha_fin requeridas para tipo=tiempo (YYYY-MM-DD)'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if fecha_fin < fecha_inicio:
                    return Response(
                        {'error': 'fecha_fin no puede ser anterior a fecha_inicio'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                observaciones = 'Origen: Odoo (RRHH).'
                if aprobada_por:
                    observaciones += f' Aprobada por: {aprobada_por}.'
                campos_base.update(
                    fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
                    leave_id_odoo=leave_id,
                    observaciones=observaciones,
                )
            else:
                # tipo=pago_dinero: sin fechas, con valor y fecha_lote
                valor_raw = data.get('valor')
                try:
                    valor = Decimal(str(valor_raw)) if valor_raw not in (None, '') else None
                except (InvalidOperation, TypeError):
                    return Response(
                        {'error': "valor invalido; debe ser numérico"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                dias_raw = data.get('dias')
                try:
                    dias = Decimal(str(dias_raw)) if dias_raw not in (None, '') else None
                except (InvalidOperation, TypeError):
                    dias = None
                fecha_lote_str = (data.get('fecha') or '').strip()
                fecha_lote = None
                if fecha_lote_str:
                    try:
                        fecha_lote = date.fromisoformat(fecha_lote_str)
                    except (TypeError, ValueError):
                        return Response(
                            {'error': "fecha invalida; formato YYYY-MM-DD"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                observaciones = motivo or 'Compensación de vacaciones en dinero aplicada por RRHH.'
                if aprobada_por:
                    observaciones += f' Aprobada por: {aprobada_por}.'
                campos_base.update(
                    compensacion_id_odoo=compensacion_id,
                    valor_compensacion=valor,
                    dias_compensados=dias,
                    fecha_lote_nomina=fecha_lote,
                    observaciones=observaciones,
                )

            solicitud = SolicitudVacacion.objects.create(**campos_base)
            _actualizar_saldo_empleado(empleado, data)
            _notificar_empleado_vacacion(solicitud, motivo=motivo)
            respuesta = {
                'status': 'creado',
                'sighu_uuid': str(solicitud.pk),
                'estado_local': nuevo_estado,
            }
            if tipo == 'tiempo':
                respuesta['leave_id'] = leave_id
            else:
                respuesta['compensacion_id'] = compensacion_id
            return Response(respuesta, status=status.HTTP_201_CREATED)

        # --- ACTUALIZAR (upsert) ---
        if solicitud.estado_local == nuevo_estado:
            # Aunque el estado no cambie, refrescamos el saldo si vino en el payload.
            _actualizar_saldo_empleado(solicitud.empleado, data)
            respuesta = {
                'status': 'ya_procesado',
                'sighu_uuid': str(solicitud.pk),
            }
            if tipo == 'tiempo':
                respuesta['leave_id'] = leave_id
            else:
                respuesta['compensacion_id'] = compensacion_id
            return Response(respuesta, status=status.HTTP_200_OK)

        solicitud.estado_local = nuevo_estado
        if motivo:
            solicitud.motivo_rechazo = motivo
        solicitud.respuesta_odoo = data
        solicitud.save(update_fields=[
            'estado_local', 'motivo_rechazo', 'respuesta_odoo', 'fecha_actualizacion',
        ])
        _actualizar_saldo_empleado(solicitud.empleado, data)
        _notificar_empleado_vacacion(solicitud, motivo=motivo)
        respuesta = {
            'status': 'actualizado',
            'sighu_uuid': str(solicitud.pk),
            'estado_local': nuevo_estado,
        }
        if tipo == 'tiempo':
            respuesta['leave_id'] = leave_id
        else:
            respuesta['compensacion_id'] = compensacion_id
        return Response(respuesta, status=status.HTTP_200_OK)
