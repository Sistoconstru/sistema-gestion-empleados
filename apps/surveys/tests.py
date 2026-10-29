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
