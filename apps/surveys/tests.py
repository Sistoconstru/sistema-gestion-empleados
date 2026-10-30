"""Tests de encuestas: preguntas Sí/No.

En producción se creó una encuesta con una pregunta Sí/No sin opciones. El
formulario pintaba entonces dos radios con value="si"/"no", y al guardar se
buscaba la opción con pk="si": OpcionEncuesta.pk es UUID, la consulta lanzaba
ValidationError y la respuesta era un 500. Nadie podía enviar la encuesta.
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.employees.models import Empleado, EstadoEmpleado, TipoDocumento
from apps.evaluations.models import TipoPregunta
from apps.organizational.models import Sede
from apps.surveys.models import (
    Encuesta, OpcionEncuesta, ParticipacionEncuesta, PreguntaEncuesta,
    RespuestaEncuesta, TipoEncuesta,
)

User = get_user_model()


class EncuestaBaseTestCase(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username='rrhh.prueba', password='x-9slek31', is_staff=True)
        self.user = User.objects.create_user(username='ana.prueba', password='x-9slek31')
        self.empleado = Empleado.objects.create(
            usuario=self.user,
            tipo_documento=TipoDocumento.objects.create(codigo='CC', nombre='Cédula'),
            nombres='Ana', apellidos='Prueba', numero_documento='111',
            telefono_contacto='3101234567', fecha_ingreso=date.today(),
            sede=Sede.objects.create(codigo='S1', nombre='Sede'),
            estado=EstadoEmpleado.objects.create(codigo='999', nombre='Activo'),
            contacto_emergencia_telefono='3109876543', direccion='Calle 1',
            creado_por=self.user,
        )
        self.tipo_si_no = TipoPregunta.objects.create(codigo='SI_NO', nombre='Sí/No')
        self.encuesta = Encuesta.objects.create(
            codigo='FIESTA', nombre='Fiesta', descripcion='-',
            tipo_encuesta=TipoEncuesta.objects.create(codigo='GEN', nombre='General'),
            fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=10),
            creada_por=self.admin,
        )

    def crear_pregunta_por_el_editor(self):
        """Como lo hace RRHH: sin escribir opciones."""
        self.client.force_login(self.admin)
        self.client.post(reverse('surveys:editar_preguntas', kwargs={'pk': self.encuesta.pk}), {
            'pregunta': '¿Confirmas asistencia?',
            'tipo_pregunta': self.tipo_si_no.pk,
            'obligatoria': 'on',
        })
        self.client.logout()
        return PreguntaEncuesta.objects.get(encuesta=self.encuesta)


class PreguntaSiNoTests(EncuestaBaseTestCase):

    def test_al_crearla_sin_opciones_se_le_ponen_si_y_no(self):
        pregunta = self.crear_pregunta_por_el_editor()
        self.assertEqual(
            list(pregunta.opcionencuesta_set.order_by('orden').values_list('opcion', flat=True)),
            ['Sí', 'No'],
        )

    def test_el_empleado_puede_responder_y_finalizar(self):
        pregunta = self.crear_pregunta_por_el_editor()
        si = pregunta.opcionencuesta_set.get(opcion='Sí')
        url = reverse('surveys:responder_encuesta', kwargs={'pk': self.encuesta.pk})
        self.client.force_login(self.user)
        self.client.get(url)  # crea la participación
        r = self.client.post(url, {f'pregunta_{pregunta.id}': str(si.pk), 'finalizar_encuesta': 'true'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ParticipacionEncuesta.objects.get(empleado=self.empleado).completada)
        self.assertEqual(RespuestaEncuesta.objects.get().opcion_seleccionada, si)

    def test_un_valor_que_no_es_uuid_no_tumba_el_envio(self):
        """Pregunta sin opciones (como la de producción antes de la migración):
        el valor "si" se guarda como texto en lugar de dar un 500."""
        pregunta = PreguntaEncuesta.objects.create(
            encuesta=self.encuesta, tipo_pregunta=self.tipo_si_no,
            pregunta='¿Vienes?', orden=1,
        )
        url = reverse('surveys:responder_encuesta', kwargs={'pk': self.encuesta.pk})
        self.client.force_login(self.user)
        self.client.get(url)
        r = self.client.post(url, {f'pregunta_{pregunta.id}': 'si', 'finalizar_encuesta': 'true'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(RespuestaEncuesta.objects.get().respuesta_texto, 'si')

    def test_un_formulario_viejo_con_si_cuenta_como_la_opcion_si(self):
        """Quien abrió la encuesta antes del arreglo envía "si" en vez del id."""
        pregunta = self.crear_pregunta_por_el_editor()
        url = reverse('surveys:responder_encuesta', kwargs={'pk': self.encuesta.pk})
        self.client.force_login(self.user)
        self.client.get(url)
        self.client.post(url, {f'pregunta_{pregunta.id}': 'si', 'finalizar_encuesta': 'true'})
        self.assertEqual(RespuestaEncuesta.objects.get().opcion_seleccionada.opcion, 'Sí')

    def test_cambiar_el_tipo_a_si_no_tambien_crea_las_opciones(self):
        tipo_texto = TipoPregunta.objects.create(codigo='TEXTO_LIBRE', nombre='Texto')
        pregunta = PreguntaEncuesta.objects.create(
            encuesta=self.encuesta, tipo_pregunta=tipo_texto, pregunta='¿Vienes?', orden=1,
        )
        self.client.force_login(self.admin)
        self.client.post(
            reverse('surveys:editar_pregunta', kwargs={'pk': self.encuesta.pk, 'pregunta_id': pregunta.pk}),
            {'pregunta': '¿Vienes?', 'tipo_pregunta': self.tipo_si_no.pk, 'obligatoria': 'on'},
        )
        self.assertEqual(OpcionEncuesta.objects.filter(pregunta=pregunta).count(), 2)


# =============================================================================
# Publicación, avisos y difusión
# =============================================================================

from unittest import mock

from django.utils import timezone

from apps.employees.models import HistorialCargo
from apps.notifications.models import Notificacion
from apps.organizational.models import AreaEmpresa, Cargo
from apps.surveys import avisos


def _sincronico(funcion, *args):
    return funcion(*args)


@mock.patch('apps.surveys.avisos.en_segundo_plano', side_effect=_sincronico)
class PublicacionYAvisosTests(EncuestaBaseTestCase):
    """Los envíos en segundo plano se corren en línea para poder comprobarlos."""

    def setUp(self):
        super().setUp()
        area = AreaEmpresa.objects.create(codigo='PROD', nombre='Producción')
        cargo_jefe = Cargo.objects.create(codigo='JEF', nombre='Jefe', area=area, nivel_jerarquico=1)
        cargo_op = Cargo.objects.create(codigo='OPE', nombre='Operario', area=area, nivel_jerarquico=2)
        self.u_jefe = User.objects.create_user(username='jefe.prueba', password='x-9slek31')
        self.jefe = Empleado.objects.create(
            usuario=self.u_jefe, tipo_documento=self.empleado.tipo_documento,
            nombres='Jefe', apellidos='Prueba', numero_documento='222',
            telefono_contacto='3101234567', fecha_ingreso=date.today(),
            sede=self.empleado.sede, estado=self.empleado.estado,
            contacto_emergencia_telefono='3109876543', direccion='Calle 2',
            creado_por=self.u_jefe,
        )
        HistorialCargo.objects.create(empleado=self.jefe, cargo=cargo_jefe, fecha_inicio=date.today(),
                                      activo=True, creado_por=self.u_jefe)
        HistorialCargo.objects.create(empleado=self.empleado, cargo=cargo_op, fecha_inicio=date.today(),
                                      activo=True, jefe_directo=self.jefe, creado_por=self.user)
        # La encuesta base del setUp se crea ya activa: aquí se trabaja con borradores.
        Encuesta.objects.all().delete()
        Notificacion.objects.all().delete()

    def crear_borrador(self, inicio=None, fin=None):
        self.client.force_login(self.admin)
        inicio = inicio or date.today()
        fin = fin or date.today() + timedelta(days=8)
        r = self.client.post(reverse('surveys:crear_encuesta'), {
            'codigo': 'FIESTA2', 'nombre': 'Fiesta', 'descripcion': '-',
            'tipo_encuesta': TipoEncuesta.objects.first().pk,
            'fecha_inicio': inicio.isoformat(), 'fecha_fin': fin.isoformat(),
        })
        encuesta = Encuesta.objects.get(codigo='FIESTA2')
        return r, encuesta

    def agregar_pregunta(self, encuesta):
        return PreguntaEncuesta.objects.create(
            encuesta=encuesta, tipo_pregunta=self.tipo_si_no, pregunta='¿Vienes?', orden=1,
        )

    def publicar(self, encuesta):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(reverse('surveys:publicar_encuesta', kwargs={'pk': encuesta.pk}))

    def avisos_de(self, usuario, codigo):
        return Notificacion.objects.filter(usuario=usuario, tipo_notificacion__codigo=codigo)

    # --- Borrador y publicación -------------------------------------------

    def test_crear_deja_un_borrador_sin_avisar_y_sin_error(self, _):
        """Antes la fecha quedaba como texto, el aviso fallaba al formatearla y
        RRHH veía "Error al crear encuesta" aunque se hubiera creado."""
        r, encuesta = self.crear_borrador()
        self.assertTrue(encuesta.es_borrador)
        self.assertFalse(encuesta.activa)
        self.assertFalse(Notificacion.objects.exists())
        mensajes = [str(m) for m in r.wsgi_request._messages]
        self.assertFalse(any('Error' in m for m in mensajes), mensajes)

    def test_no_se_publica_sin_preguntas(self, _):
        _, encuesta = self.crear_borrador()
        self.publicar(encuesta)
        encuesta.refresh_from_db()
        self.assertTrue(encuesta.es_borrador)

    def test_publicar_avisa_a_los_empleados(self, _):
        _, encuesta = self.crear_borrador()
        self.agregar_pregunta(encuesta)
        self.publicar(encuesta)
        encuesta.refresh_from_db()
        self.assertTrue(encuesta.activa)
        self.assertFalse(encuesta.es_borrador)
        self.assertEqual(self.avisos_de(self.user, 'encuesta_publicada').count(), 1)

    def test_si_abre_despues_avisa_el_dia_de_inicio(self, _):
        inicio = date.today() + timedelta(days=2)
        _, encuesta = self.crear_borrador(inicio=inicio, fin=inicio + timedelta(days=5))
        self.agregar_pregunta(encuesta)
        self.publicar(encuesta)
        self.assertFalse(self.avisos_de(self.user, 'encuesta_publicada').exists())
        with mock.patch('apps.surveys.avisos.timezone.localdate', return_value=inicio):
            avisos.mantenimiento_diario(inicio)
        self.assertEqual(self.avisos_de(self.user, 'encuesta_publicada').count(), 1)

    def test_cambiar_fechas_no_publica_un_borrador(self, _):
        _, encuesta = self.crear_borrador()
        self.client.post(reverse('surveys:editar_encuesta', kwargs={'pk': encuesta.pk}), {
            'nombre': 'Fiesta', 'tipo_encuesta': encuesta.tipo_encuesta_id,
            'fecha_inicio': date.today().isoformat(),
            'fecha_fin': (date.today() + timedelta(days=3)).isoformat(),
        })
        encuesta.refresh_from_db()
        self.assertTrue(encuesta.es_borrador)
        self.assertFalse(encuesta.activa)

    # --- Recordatorios y jefes --------------------------------------------

    def encuesta_publicada(self):
        _, encuesta = self.crear_borrador()
        self.agregar_pregunta(encuesta)
        self.publicar(encuesta)
        return encuesta

    def test_avisar_a_pendientes_llega_al_empleado_y_a_su_jefe(self, _):
        encuesta = self.encuesta_publicada()
        self.client.post(reverse('surveys:difundir_encuesta', kwargs={'pk': encuesta.pk}))
        self.assertEqual(self.avisos_de(self.user, 'encuesta_recordatorio').count(), 1)
        aviso_jefe = self.avisos_de(self.u_jefe, 'encuesta_jefe').get()
        self.assertIn('1 persona de tu equipo', aviso_jefe.mensaje)

    def test_un_solo_recordatorio_por_dia(self, _):
        encuesta = self.encuesta_publicada()
        url = reverse('surveys:difundir_encuesta', kwargs={'pk': encuesta.pk})
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(self.avisos_de(self.user, 'encuesta_recordatorio').count(), 1)
        self.assertEqual(self.avisos_de(self.u_jefe, 'encuesta_jefe').count(), 1)

    def test_quien_ya_respondio_no_recibe_recordatorio(self, _):
        encuesta = self.encuesta_publicada()
        ParticipacionEncuesta.objects.create(empleado=self.empleado, encuesta=encuesta, completada=True)
        self.client.post(reverse('surveys:difundir_encuesta', kwargs={'pk': encuesta.pk}))
        self.assertFalse(self.avisos_de(self.user, 'encuesta_recordatorio').exists())
        self.assertFalse(self.avisos_de(self.u_jefe, 'encuesta_jefe').exists())

    def test_recordatorios_automaticos_a_mitad_y_la_vispera(self, _):
        encuesta = self.encuesta_publicada()  # dura 8 días: mitad = día 4
        mitad = encuesta.fecha_inicio + timedelta(days=4)
        vispera = encuesta.fecha_fin - timedelta(days=1)
        otro_dia = encuesta.fecha_inicio + timedelta(days=2)
        for dia in (otro_dia, mitad, vispera):
            with mock.patch('apps.surveys.avisos.timezone.localdate', return_value=dia):
                avisos.mantenimiento_diario(dia)
        motivos = sorted(
            n.datos_adicionales['motivo']
            for n in self.avisos_de(self.user, 'encuesta_recordatorio')
        )
        self.assertEqual(motivos, ['cierre', 'mitad'])

    # --- Pantallas ---------------------------------------------------------

    def test_el_jefe_ve_quien_de_su_equipo_falta(self, _):
        encuesta = self.encuesta_publicada()
        self.client.force_login(self.u_jefe)
        r = self.client.get(reverse('surveys:pendientes_equipo', kwargs={'pk': encuesta.pk}))
        self.assertContains(r, self.empleado.nombre_completo)
        self.assertContains(r, 'Pendiente')

    def test_un_empleado_sin_equipo_no_ve_a_nadie(self, _):
        encuesta = self.encuesta_publicada()
        self.client.force_login(self.user)
        r = self.client.get(reverse('surveys:pendientes_equipo', kwargs={'pk': encuesta.pk}))
        self.assertNotContains(r, self.jefe.nombre_completo)

    def test_difundir_muestra_qr_y_enlace_de_whatsapp(self, _):
        encuesta = self.encuesta_publicada()
        r = self.client.get(reverse('surveys:difundir_encuesta', kwargs={'pk': encuesta.pk}))
        self.assertContains(r, '<svg')
        self.assertContains(r, 'https://wa.me/?text=')
        self.assertContains(r, f'/encuestas/responder/{encuesta.pk}/')

    def test_un_empleado_no_entra_a_difundir(self, _):
        encuesta = self.encuesta_publicada()
        self.client.force_login(self.user)
        r = self.client.get(reverse('surveys:difundir_encuesta', kwargs={'pk': encuesta.pk}))
        self.assertEqual(r.status_code, 302)

    def test_ventana_de_pendientes_aunque_nunca_la_haya_abierto(self, _):
        """En una encuesta general la participación se crea al abrirla; antes
        el contador del menú no veía a quien nunca la había abierto."""
        encuesta = self.encuesta_publicada()
        self.assertFalse(ParticipacionEncuesta.objects.filter(empleado=self.empleado).exists())
        self.client.force_login(self.user)
        r = self.client.get(reverse('employees:feed_list'))
        self.assertEqual(r.context['encuestas_pendientes_nav'], 1)
        self.assertContains(r, 'modalEncuestasPendientes')

    def test_la_ventana_no_sale_dentro_de_encuestas(self, _):
        self.encuesta_publicada()
        self.client.force_login(self.user)
        r = self.client.get(reverse('surveys:index'))
        self.assertNotContains(r, 'modalEncuestasPendientes')

    def test_tras_un_recordatorio_manual_no_llega_ademas_el_de_publicacion(self, _):
        encuesta = self.encuesta_publicada()
        Notificacion.objects.all().delete()  # como la fiesta: publicada sin aviso
        self.client.post(reverse('surveys:difundir_encuesta', kwargs={'pk': encuesta.pk}))
        avisos.mantenimiento_diario(date.today())
        self.assertFalse(self.avisos_de(self.user, 'encuesta_publicada').exists())
        self.assertEqual(self.avisos_de(self.user, 'encuesta_recordatorio').count(), 1)
