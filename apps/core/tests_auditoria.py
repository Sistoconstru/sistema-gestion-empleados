"""Auditoría legible: la acción sale de la ruta, no de palabras en la URL.

Antes el 97% de los registros quedaba como "crear": aprobar un documento,
cerrar sesión o borrar un anexo se veían igual.
"""
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from apps.core.models import LogActividad
from apps.documents.models import AnexoDocumento
from apps.documents.tests import MEDIA_TMP, DocumentosBaseTestCase, pdf

User = get_user_model()


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class AuditoriaLegibleTests(DocumentosBaseTestCase):

    def ultimo(self):
        """El registro de la última petición. Se limpian los anteriores tras
        leerlo: ordenar por fecha empata cuando dos caen en el mismo instante."""
        log = LogActividad.objects.order_by('-fecha_accion').first()
        LogActividad.objects.all().delete()
        return log

    def test_login_exitoso(self):
        self.client.post(reverse('authentication:login'), {'username': 'ana.prueba', 'password': 'x-9slek31'})
        log = self.ultimo()
        self.assertEqual(log.accion, 'iniciar_sesion')
        self.assertEqual(log.usuario, self.user)
        self.assertEqual(log.descripcion, f'{self.user.get_full_name() or "ana.prueba"} inició sesión')

    def test_login_fallido_dice_con_que_usuario(self):
        self.client.post(reverse('authentication:login'), {'username': 'ana.prueba', 'password': 'mala'})
        log = self.ultimo()
        self.assertEqual(log.accion, 'login_fallido')
        self.assertIsNone(log.usuario)
        self.assertIn('«ana.prueba»', log.descripcion)

    def test_cerrar_sesion(self):
        self.client.force_login(self.user)
        self.client.post(reverse('authentication:logout'))
        self.assertEqual(self.ultimo().accion, 'cerrar_sesion')

    def test_aprobar_y_rechazar_nombran_el_documento(self):
        self.client.force_login(self.rrhh)
        url = reverse('documents:documento_approve', args=[self.contrato.pk])
        self.client.post(url, {'estado_aprobacion': 'rechazado', 'observaciones': 'Falta la firma'})
        log = self.ultimo()
        self.assertEqual(log.accion, 'rechazar')
        self.assertIn(f'rechazó el Contrato laboral de {self.empleado.nombre_completo}', log.descripcion)
        self.assertIn('Falta la firma', log.descripcion)

        self.client.post(url, {'estado_aprobacion': 'aprobado'})
        self.assertEqual(self.ultimo().accion, 'aprobar')

    def test_borrar_un_anexo_conserva_lo_que_se_borro(self):
        anexo = AnexoDocumento.objects.create(
            documento=self.contrato, tipo='prorroga', fecha_vigencia=self.contrato.fecha_carga.date(),
            archivo=pdf('p.pdf'), nombre_archivo='P.pdf', cargado_por=self.rrhh,
        )
        self.client.force_login(self.rrhh)
        self.client.post(reverse('documents:anexo_eliminar', args=[anexo.pk]))
        log = self.ultimo()
        self.assertEqual(log.accion, 'eliminar')
        self.assertIn(f'eliminó el anexo «Prórroga» del contrato laboral de {self.empleado.nombre_completo}', log.descripcion)

    def test_agregar_anexo(self):
        self.client.force_login(self.rrhh)
        self.client.post(reverse('documents:anexo_crear', args=[self.contrato.pk]), {
            'tipo': 'otrosi', 'fecha_vigencia': '2026-11-01', 'archivo': pdf('o.pdf'),
        })
        log = self.ultimo()
        self.assertEqual(log.accion, 'agregar_anexo')
        self.assertIn(f'agregó un Otrosí al Contrato laboral de {self.empleado.nombre_completo} (vigente desde 2026-11-01)', log.descripcion)

    def test_admin_borrado_masivo_sin_confirmar(self):
        self.client.force_login(User.objects.create_superuser('jefa', 'j@x.co', 'x-9slek31'))
        self.client.post(reverse('admin:documents_documentoempleado_changelist'), {
            'action': 'delete_selected', '_selected_action': [str(self.contrato.pk)],
        })
        log = self.ultimo()
        self.assertEqual(log.accion, 'eliminar_sin_confirmar')
        self.assertIn('aún sin confirmar', log.descripcion)
        self.assertIn(self.empleado.nombre_completo, log.descripcion)

    def test_ruta_sin_catalogo_ya_no_queda_como_crear(self):
        from apps.core.auditoria import interpretar
        accion, _, texto = interpretar({'vista': 'otra_app:algo_raro', 'kwargs': {}}, {}, 302)
        self.assertEqual(accion, 'otra')
        self.assertIn('algo raro', texto)
