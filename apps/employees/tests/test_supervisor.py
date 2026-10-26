"""EmpleadoDetailSupervisorView: la jerarquía se resuelve por jefe_directo.

Antes era la única vista que la decidía por cargo (cargo_jefe y
nivel_jerarquico), en contradicción con el resto del sistema.
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.employees.models import Empleado, EstadoEmpleado, HistorialCargo, TipoDocumento
from apps.employees.views import _es_superior_en_cadena
from apps.organizational.models import AreaEmpresa, Cargo, Sede

User = get_user_model()


class SupervisorJerarquiaTests(TestCase):

    def crear(self, username, documento, cargo, jefe=None, staff=False):
        user = User.objects.create_user(username=username, password='x-9slek31', is_staff=staff)
        emp = Empleado.objects.create(
            usuario=user, tipo_documento=self.tipo_doc,
            nombres=username.split('.')[0].capitalize(), apellidos='Prueba',
            numero_documento=documento, telefono_contacto='3101234567',
            fecha_ingreso=date.today(), sede=self.sede, estado=self.estado,
            contacto_emergencia_telefono='3109876543', direccion='Calle 1',
            creado_por=user,
        )
        HistorialCargo.objects.create(
            empleado=emp, cargo=cargo, fecha_inicio=date.today(), activo=True,
            jefe_directo=jefe, creado_por=user,
        )
        return user, emp

    def url(self, empleado):
        return reverse('employees:empleado_detail_supervisor', kwargs={'pk': empleado.pk})

    def setUp(self):
        self.estado = EstadoEmpleado.objects.create(codigo='999', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='S1', nombre='Sede')
        self.area = AreaEmpresa.objects.create(codigo='PROD', nombre='Producción')
        self.c_director = Cargo.objects.create(codigo='DIR', nombre='Director', area=self.area, nivel_jerarquico=1)
        self.c_coord = Cargo.objects.create(codigo='COO', nombre='Coordinador', area=self.area,
                                            nivel_jerarquico=2, cargo_jefe=self.c_director)
        self.c_oper = Cargo.objects.create(codigo='OPE', nombre='Operario', area=self.area,
                                           nivel_jerarquico=3, cargo_jefe=self.c_coord)

        # Cadena real: director ← coordinador A ← operario A
        self.u_dir, self.director = self.crear('dir.prueba', '1', self.c_director)
        self.u_coord_a, self.coord_a = self.crear('coora.prueba', '2', self.c_coord, jefe=self.director)
        self.u_oper_a, self.oper_a = self.crear('opera.prueba', '3', self.c_oper, jefe=self.coord_a)

        # Otro equipo de la misma área: coordinador B ← operario B
        self.u_coord_b, self.coord_b = self.crear('coorb.prueba', '4', self.c_coord)
        self.u_oper_b, self.oper_b = self.crear('operb.prueba', '5', self.c_oper, jefe=self.coord_b)

    def test_el_jefe_directo_ve_a_su_subalterno(self):
        self.client.force_login(self.u_coord_a)
        self.assertEqual(self.client.get(self.url(self.oper_a)).status_code, 200)

    def test_el_director_ve_a_los_operarios_de_sus_coordinadores(self):
        self.client.force_login(self.u_dir)
        self.assertEqual(self.client.get(self.url(self.oper_a)).status_code, 200)

    def test_un_coordinador_no_ve_a_otro_equipo_de_su_misma_area(self):
        """La regla vieja ("misma área y nivel mayor") lo permitía: el
        coordinador A, de nivel 2, veía al operario B, de nivel 3, aunque
        no fuera de su equipo."""
        self.client.force_login(self.u_coord_a)
        self.assertEqual(self.client.get(self.url(self.oper_b)).status_code, 404)

    def test_manda_jefe_directo_aunque_el_cargo_diga_otra_cosa(self):
        """La regla vieja daba 404 aquí: el perfil listaba al subalterno por
        jefe_directo, pero esta vista validaba por cargo."""
        # Otra área y sin cargo_jefe: así ninguna de las dos reglas por cargo
        # lo cubre y solo jefe_directo decide.
        otra_area = AreaEmpresa.objects.create(codigo='LOG', nombre='Logística')
        c_auxiliar = Cargo.objects.create(codigo='AUX', nombre='Auxiliar', area=otra_area,
                                          nivel_jerarquico=3, cargo_jefe=None)
        _, auxiliar = self.crear('aux.prueba', '6', c_auxiliar, jefe=self.coord_a)
        self.client.force_login(self.u_coord_a)
        self.assertEqual(self.client.get(self.url(auxiliar)).status_code, 200)

    def test_un_subalterno_no_ve_a_su_jefe(self):
        self.client.force_login(self.u_oper_a)
        self.assertEqual(self.client.get(self.url(self.coord_a)).status_code, 404)

    def test_staff_entra_aunque_no_sea_superusuario(self):
        # En otra área, para que no entre por la regla vieja de "misma área".
        area_rrhh = AreaEmpresa.objects.create(codigo='RH', nombre='Talento Humano')
        c_rrhh = Cargo.objects.create(codigo='RRH', nombre='Analista', area=area_rrhh, nivel_jerarquico=5)
        u_rrhh, _ = self.crear('rrhh.prueba', '7', c_rrhh, staff=True)
        self.client.force_login(u_rrhh)
        self.assertEqual(self.client.get(self.url(self.oper_b)).status_code, 200)

    def test_un_ciclo_en_los_datos_no_cuelga_la_comprobacion(self):
        """Una asignación mal hecha (A jefe de B y B jefe de A) no debe
        dejar la vista en un bucle infinito."""
        HistorialCargo.objects.filter(empleado=self.coord_b).update(jefe_directo=self.oper_b)
        self.assertFalse(_es_superior_en_cadena(self.director, self.oper_b))
