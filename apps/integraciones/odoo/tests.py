"""Tests de integración SIGHU -> Odoo."""
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.employees.models import (
    Ciudad, Departamento, Empleado, EstadoEmpleado, Escolaridad,
    HistorialCargo, SolicitudVacacion, TipoDocumento,
)
from apps.organizational.models import AreaEmpresa, Cargo, Sede

from .models import OdooSyncFalla
from .serializers import OdooEmpleadoSerializer
from .services import push_empleado_a_odoo


User = get_user_model()


def _crear_empleado_minimo():
    user = User.objects.create_user(username='odoo_test', password='x')
    tipo_doc, _ = TipoDocumento.objects.get_or_create(codigo='CED', defaults={'nombre': 'Cedula'})
    estado, _ = EstadoEmpleado.objects.get_or_create(
        codigo='999', defaults={'nombre': 'Activo', 'permite_acceso_sistema': True},
    )
    sede, _ = Sede.objects.get_or_create(
        codigo='BOG', defaults={
            'nombre': 'Bogota Centro', 'direccion': 'X', 'ciudad': 'Bogota',
            'departamento': 'Cundinamarca', 'telefono': '1234567',
        },
    )
    depto, _ = Departamento.objects.get_or_create(codigo='ANT', defaults={'nombre': 'Antioquia'})
    ciudad, _ = Ciudad.objects.get_or_create(nombre='Medellin', departamento=depto)
    escolaridad, _ = Escolaridad.objects.get_or_create(
        codigo='UNI', defaults={'nivel': 'Profesional', 'orden': 5},
    )
    area, _ = AreaEmpresa.objects.get_or_create(codigo='RH', defaults={'nombre': 'Recursos Humanos'})
    cargo, _ = Cargo.objects.get_or_create(
        codigo='ANL-RH-001', defaults={'nombre': 'Analista RH', 'area': area},
    )
    emp = Empleado.objects.create(
        usuario=user,
        tipo_documento=tipo_doc,
        numero_documento='1020304050',
        nombres='Juan Carlos',
        apellidos='Perez Gomez',
        telefono_contacto='3001234567',
        fecha_ingreso=date(2023, 8, 1),
        sede=sede,
        estado=estado,
        fecha_nacimiento=date(1990, 3, 15),
        ciudad_nacimiento=ciudad,
        escolaridad=escolaridad,
        correo_electronico='juan@test.com',
        direccion='Carrera 10 # 20 - 30',
        contacto_emergencia_nombre='Maria',
        contacto_emergencia_telefono='3007654321',
        creado_por=user,
    )
    HistorialCargo.objects.create(
        empleado=emp, cargo=cargo, fecha_inicio=date(2024, 2, 1),
        salario=Decimal('3500000.00'), activo=True, creado_por=user,
    )
    return emp


@override_settings(SIGHU_ODOO_WEBHOOK_URL='', SIGHU_ODOO_WEBHOOK_TOKEN='')
class OdooEmpleadoSerializerTests(TestCase):

    def test_contrato_json_shape_completo(self):
        emp = _crear_empleado_minimo()
        data = OdooEmpleadoSerializer(emp).data
        keys_esperadas = {
            'sighu_uuid', 'tipo_documento', 'numero_documento', 'nombres',
            'apellidos', 'nombre_completo', 'fecha_nacimiento', 'ciudad_nacimiento',
            'correo_electronico', 'telefono_contacto', 'direccion', 'fecha_ingreso',
            'estado', 'sede', 'escolaridad', 'contacto_emergencia',
            'cargo_actual', 'centro_costo', 'fecha_actualizacion',
        }
        self.assertEqual(set(data.keys()), keys_esperadas)

    def test_tipo_documento_incluye_codigo_dian(self):
        emp = _crear_empleado_minimo()
        data = OdooEmpleadoSerializer(emp).data
        self.assertEqual(data['tipo_documento']['codigo_sighu'], 'CED')
        self.assertEqual(data['tipo_documento']['codigo_dian'], '13')

    def test_estado_codigo_canonico(self):
        emp = _crear_empleado_minimo()
        data = OdooEmpleadoSerializer(emp).data
        self.assertEqual(data['estado']['codigo'], '999')

    def test_salario_string_para_evitar_perdida_precision(self):
        emp = _crear_empleado_minimo()
        data = OdooEmpleadoSerializer(emp).data
        self.assertEqual(data['cargo_actual']['salario'], '3500000.00')
        self.assertIsInstance(data['cargo_actual']['salario'], str)

    def test_jefe_directo_uuid_null_cuando_no_aplica(self):
        emp = _crear_empleado_minimo()
        data = OdooEmpleadoSerializer(emp).data
        self.assertIsNone(data['cargo_actual']['jefe_directo_uuid'])

    def test_payload_es_json_serializable_para_requests(self):
        """Regresión: requests.post(json=payload) usa json.dumps estándar
        que no maneja datetime/UUID. Si el serializer devuelve esos tipos
        crudos, el push síncrono explota con TypeError."""
        import json as _json
        emp = _crear_empleado_minimo()
        data = OdooEmpleadoSerializer(emp).data
        # No debe lanzar TypeError: Object of type X is not JSON serializable
        _json.dumps(data)


@override_settings(
    SIGHU_ODOO_TOKEN='test-token-secreto',
    SIGHU_ODOO_WEBHOOK_URL='',
    SIGHU_ODOO_WEBHOOK_TOKEN='',
)
class OdooEndpointTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.emp = _crear_empleado_minimo()

    def test_healthcheck_publico(self):
        resp = self.client.get('/api/v1/odoo/healthcheck/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'status': 'ok'})

    def test_listado_sin_token_401(self):
        resp = self.client.get('/api/v1/odoo/empleados/')
        self.assertEqual(resp.status_code, 401)

    def test_listado_token_invalido_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token wrong-token')
        resp = self.client.get('/api/v1/odoo/empleados/')
        self.assertEqual(resp.status_code, 401)

    def test_listado_token_correcto_devuelve_empleado(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token test-token-secreto')
        resp = self.client.get('/api/v1/odoo/empleados/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['numero_documento'], '1020304050')

    def test_modified_since_filtra_por_fecha(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token test-token-secreto')
        fecha_futura = '2099-01-01T00:00:00Z'
        resp = self.client.get(f'/api/v1/odoo/empleados/?modified_since={fecha_futura}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['count'], 0)


@override_settings(
    SIGHU_ODOO_WEBHOOK_URL='http://fake.test/webhook',
    SIGHU_ODOO_WEBHOOK_TOKEN='fake-token',
)
class OdooPushServiceTests(TestCase):

    def setUp(self):
        self.emp = _crear_empleado_minimo()
        # Limpiar fallas creadas por el signal del setUp
        OdooSyncFalla.objects.all().delete()

    def test_push_200_no_crea_falla(self):
        with patch('apps.integraciones.odoo.services.requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=200, text='{"status":"ok"}')
            push_empleado_a_odoo(self.emp, 'updated')
        self.assertEqual(OdooSyncFalla.objects.count(), 0)

    def test_push_timeout_crea_falla(self):
        with patch('apps.integraciones.odoo.services.requests.post',
                   side_effect=requests.Timeout('boom')):
            push_empleado_a_odoo(self.emp, 'updated')
        falla = OdooSyncFalla.objects.get()
        self.assertEqual(falla.motivo, 'timeout_o_conexion')
        self.assertEqual(falla.evento, 'updated')

    def test_push_500_crea_falla_con_http_status(self):
        with patch('apps.integraciones.odoo.services.requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=500, text='boom')
            push_empleado_a_odoo(self.emp, 'updated')
        falla = OdooSyncFalla.objects.get()
        self.assertEqual(falla.motivo, '5xx_odoo')
        self.assertEqual(falla.http_status, 500)

    def test_push_400_crea_falla_contrato(self):
        with patch('apps.integraciones.odoo.services.requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=400, text='bad')
            push_empleado_a_odoo(self.emp, 'updated')
        falla = OdooSyncFalla.objects.get()
        self.assertEqual(falla.motivo, '4xx_contrato')
        self.assertEqual(falla.http_status, 400)


@override_settings(
    SIGHU_ODOO_WEBHOOK_URL='',
    SIGHU_ODOO_WEBHOOK_TOKEN='',
)
class OdooPushSkipSinConfiguracionTests(TestCase):

    def test_skip_silencioso_sin_webhook_configurado(self):
        emp = _crear_empleado_minimo()
        with patch('apps.integraciones.odoo.services.requests.post') as mock_post:
            push_empleado_a_odoo(emp, 'updated')
        self.assertFalse(mock_post.called)
        self.assertEqual(OdooSyncFalla.objects.count(), 0)


@override_settings(
    SIGHU_ODOO_WEBHOOK_URL='http://fake.test/webhook',
    SIGHU_ODOO_WEBHOOK_TOKEN='fake-token',
)
class OdooSignalTests(TestCase):

    def test_post_save_empleado_dispara_push_updated(self):
        emp = _crear_empleado_minimo()
        with patch('apps.integraciones.odoo.signals.push_empleado_a_odoo') as mock_push:
            with self.captureOnCommitCallbacks(execute=True):
                emp.telefono_contacto = '3019999999'
                emp.save()
        mock_push.assert_called()
        args, _ = mock_push.call_args
        self.assertEqual(args[0].id, emp.id)
        self.assertEqual(args[1], 'updated')

    def test_post_save_historial_cargo_activo_dispara_push(self):
        emp = _crear_empleado_minimo()
        cargo = Cargo.objects.first()
        user = User.objects.first()
        with patch('apps.integraciones.odoo.signals.push_empleado_a_odoo') as mock_push:
            with self.captureOnCommitCallbacks(execute=True):
                HistorialCargo.objects.create(
                    empleado=emp, cargo=cargo, fecha_inicio=date(2024, 6, 1),
                    salario=Decimal('4000000.00'), activo=True, creado_por=user,
                )
        mock_push.assert_called()
        args, _ = mock_push.call_args
        self.assertEqual(args[0].id, emp.id)
        self.assertEqual(args[1], 'updated')


@override_settings(
    SIGHU_ODOO_TOKEN='test-token-secreto',
    SIGHU_ODOO_WEBHOOK_URL='',
    SIGHU_ODOO_WEBHOOK_TOKEN='',
)
class OdooVacacionEstadoEndpointTests(TestCase):
    """Callback Odoo→SIGHU al cambiar el estado de una solicitud de vacaciones."""

    URL = '/api/v1/odoo/vacaciones/estado/'

    def setUp(self):
        self.client = APIClient()
        self.emp = _crear_empleado_minimo()
        self.user = User.objects.get(username='odoo_test')
        self.solicitud = SolicitudVacacion.objects.create(
            empleado=self.emp,
            jefe_solicitante=self.emp,  # mismo empleado para el test, no importa quién
            fecha_inicio=date(2026, 8, 10),
            fecha_fin=date(2026, 8, 14),
            estado_local='enviada_pendiente_rrhh',
            leave_id_odoo=42,
            creado_por=self.user,
        )

    def _auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token test-token-secreto')

    def test_sin_token_401(self):
        resp = self.client.post(self.URL, {'leave_id': 42, 'estado': 'aprobada'}, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_token_invalido_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token wrong')
        resp = self.client.post(self.URL, {'leave_id': 42, 'estado': 'aprobada'}, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_leave_id_inexistente_404(self):
        self._auth()
        resp = self.client.post(self.URL, {'leave_id': 999, 'estado': 'aprobada'}, format='json')
        self.assertEqual(resp.status_code, 404)
        self.assertIn('999', resp.json()['error'])

    def test_leave_id_faltante_400(self):
        self._auth()
        resp = self.client.post(self.URL, {'estado': 'aprobada'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_estado_invalido_400(self):
        self._auth()
        resp = self.client.post(self.URL, {'leave_id': 42, 'estado': 'pendiente'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn("'pendiente'", resp.json()['error'])

    def test_aprobada_actualiza_estado(self):
        self._auth()
        resp = self.client.post(self.URL, {
            'leave_id': 42, 'estado': 'aprobada', 'aprobada_por': 'RRHH',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'recibido')
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado_local, 'aprobada_rrhh')

    def test_rechazada_guarda_motivo(self):
        self._auth()
        resp = self.client.post(self.URL, {
            'leave_id': 42, 'estado': 'rechazada', 'motivo': 'No procede en agosto',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado_local, 'rechazada_rrhh')
        self.assertEqual(self.solicitud.motivo_rechazo, 'No procede en agosto')

    def test_cancelada_actualiza_estado(self):
        self._auth()
        resp = self.client.post(self.URL, {'leave_id': 42, 'estado': 'cancelada'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado_local, 'cancelada_rrhh')

    def test_idempotencia_segunda_llamada_devuelve_ya_procesado(self):
        self._auth()
        # Primera llamada: actualiza
        resp1 = self.client.post(self.URL, {'leave_id': 42, 'estado': 'aprobada'}, format='json')
        self.assertEqual(resp1.json()['status'], 'recibido')
        # Segunda llamada: idempotente
        resp2 = self.client.post(self.URL, {'leave_id': 42, 'estado': 'aprobada'}, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()['status'], 'ya_procesado')

    def test_respuesta_odoo_guardada_para_auditoria(self):
        self._auth()
        payload = {
            'leave_id': 42, 'estado': 'aprobada',
            'aprobada_por': 'Maria Gomez', 'fecha_estado': '2026-08-20T10:00:00Z',
        }
        self.client.post(self.URL, payload, format='json')
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.respuesta_odoo, payload)
