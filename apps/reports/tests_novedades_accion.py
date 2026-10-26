"""Quién puede aprobar novedades de nómina.

Estos tests existen por una regresión real: al endurecer los permisos de
apps/reports se le puso StaffRequiredMixin a NovedadesAccionView, que es la
única vista del módulo pensada también para directores. Los directores no son
is_staff, así que su bandeja seguía abriéndose pero al aprobar recibían un 403.
"""
from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.employees.models import (
    Empleado, EstadoEmpleado, HistorialCargo, NovedadNomina, TipoDocumento,
)
from apps.organizational.models import AreaEmpresa, Cargo, Sede

User = get_user_model()


class AprobacionNovedadesTests(TestCase):

    def crear_empleado(self, username, documento, staff=False):
        user = User.objects.create_user(
            username=username, password='x-9slek31', is_staff=staff,
        )
        empleado = Empleado.objects.create(
            usuario=user,
            tipo_documento=self.tipo_doc,
            nombres=username.split('.')[0].capitalize(),
            apellidos='Prueba',
            numero_documento=documento,
            telefono_contacto='3101234567',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3109876543',
            direccion='Calle 1',
            creado_por=user,
        )
        return user, empleado

    def setUp(self):
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='S1', nombre='Sede Principal')
        self.area = AreaEmpresa.objects.create(codigo='PROD', nombre='Producción')
        self.cargo = Cargo.objects.create(codigo='C1', nombre='Coordinador', area=self.area)

        # Director (NO es staff) ← coordinador ← operario
        self.user_director, self.director = self.crear_empleado('dir.prueba', '100')
        self.user_coord, self.coordinador = self.crear_empleado('coord.prueba', '200')
        self.user_operario, self.operario = self.crear_empleado('oper.prueba', '300')

        # El coordinador le reporta directamente al director
        HistorialCargo.objects.create(
            empleado=self.coordinador, cargo=self.cargo,
            fecha_inicio=date.today(), activo=True, jefe_directo=self.director,
            creado_por=self.user_director,
        )

        # Novedad del operario, registrada por el coordinador
        self.novedad = NovedadNomina.objects.create(
            empleado=self.operario,
            fecha=date.today(),
            tipo='hora_extra_diurna',
            hora_inicio=time(18, 0),
            hora_fin=time(20, 0),
            total_horas=Decimal('2.00'),
            registrado_por=self.coordinador,
            estado_aprobacion='pendiente',
            creado_por=self.user_coord,
        )
        self.url = reverse('reports:novedades_accion')

    def _aprobar(self, ids=None):
        return self.client.post(self.url, {
            'accion': 'aprobar',
            'novedad_ids': ids if ids is not None else [str(self.novedad.pk)],
        })

    def test_el_director_puede_aprobar_las_de_su_equipo(self):
        """La regresión: devolvía 403 antes de ejecutar la vista."""
        self.client.force_login(self.user_director)
        r = self._aprobar()
        self.assertNotEqual(r.status_code, 403, 'el director volvió a quedar bloqueado')
        self.novedad.refresh_from_db()
        self.assertEqual(self.novedad.estado_aprobacion, 'aprobada')

    def test_rrhh_puede_aprobar_cualquiera(self):
        user_rrhh, _ = self.crear_empleado('rrhh.prueba', '400', staff=True)
        self.client.force_login(user_rrhh)
        r = self._aprobar()
        self.assertNotEqual(r.status_code, 403)
        self.novedad.refresh_from_db()
        self.assertEqual(self.novedad.estado_aprobacion, 'aprobada')

    def test_un_empleado_sin_subalternos_no_aprueba_nada(self):
        """Sin el mixin la vista queda abierta a cualquier sesión, así que la
        autorización real tiene que estar en el acotado del queryset."""
        self.client.force_login(self.user_operario)
        self._aprobar()
        self.novedad.refresh_from_db()
        self.assertEqual(self.novedad.estado_aprobacion, 'pendiente')

    def test_un_director_no_aprueba_novedades_de_otro_equipo(self):
        otro_user, otro_director = self.crear_empleado('otro.dir', '500')
        self.client.force_login(otro_user)
        self._aprobar()
        self.novedad.refresh_from_db()
        self.assertEqual(self.novedad.estado_aprobacion, 'pendiente')

    def test_exige_sesion(self):
        r = self._aprobar()
        self.assertEqual(r.status_code, 302)
        self.assertIn('login', r['Location'])

    def test_sin_seleccion_el_director_no_acaba_en_un_403(self):
        """El fallback de los errores de validación apuntaba al listado de
        RRHH, que para un director también responde 403."""
        self.client.force_login(self.user_director)
        r = self.client.post(self.url, {'accion': 'aprobar', 'novedad_ids': []})
        self.assertEqual(r.status_code, 302)
        destino = r['Location']
        seguimiento = self.client.get(destino)
        self.assertNotEqual(
            seguimiento.status_code, 403,
            f'tras el error de validación el director acabó en un 403 ({destino})',
        )

    def test_el_listado_de_rrhh_sigue_siendo_solo_de_rrhh(self):
        """La restricción que introdujo la regresión era correcta aquí."""
        self.client.force_login(self.user_director)
        r = self.client.get(reverse('reports:novedades_report'))
        self.assertEqual(r.status_code, 403)
