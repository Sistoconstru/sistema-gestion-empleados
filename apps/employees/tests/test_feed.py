"""Tests del feed/cartelera: publicación rápida con imagen y reacciones."""
import io
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.employees.models import (
    Comentario, Empleado, EstadoEmpleado, Publicacion, Reaccion, TipoDocumento,
)
from apps.organizational.models import Sede

User = get_user_model()


def imagen_de_prueba(nombre='foto.jpg', tamano=(80, 60)):
    buffer = io.BytesIO()
    Image.new('RGB', tamano, (40, 120, 160)).save(buffer, format='JPEG')
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type='image/jpeg')


class FeedBaseTestCase(TestCase):
    """Fixtures compartidos: un empleado con usuario, que es lo mínimo
    que exige el feed (EmpleadoRequiredMixin)."""

    def crear_empleado(self, username, documento):
        user = User.objects.create_user(username=username, password='x-9slek31')
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
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user, self.empleado = self.crear_empleado('ana.prueba', '111')
        self.client.force_login(self.user)
        self.url_rapida = reverse('employees:crear_publicacion_rapida')


class PublicacionRapidaConImagenTests(FeedBaseTestCase):
    """Antes la publicación rápida era solo texto y para adjuntar una foto
    había que irse al editor completo."""

    def test_publicar_solo_texto(self):
        r = self.client.post(self.url_rapida, {'contenido': 'Hola equipo'},
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['success'])
        self.assertEqual(Publicacion.objects.count(), 1)

    def test_publicar_solo_imagen_sin_texto(self):
        """Una foto sin pie es una publicación válida."""
        r = self.client.post(
            self.url_rapida,
            {'contenido': '', 'imagen': imagen_de_prueba()},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['success'])
        publicacion = Publicacion.objects.get()
        self.assertTrue(publicacion.imagen)
        self.assertEqual(publicacion.contenido, '')

    def test_el_formulario_vacio_se_rechaza(self):
        r = self.client.post(self.url_rapida, {'contenido': '   '},
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.json()['success'])
        self.assertEqual(Publicacion.objects.count(), 0)

    def test_un_archivo_que_no_es_imagen_se_rechaza(self):
        archivo = SimpleUploadedFile('malo.pdf', b'%PDF-1.4 falso',
                                     content_type='application/pdf')
        r = self.client.post(self.url_rapida, {'contenido': 'con adjunto', 'imagen': archivo},
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Publicacion.objects.count(), 0)

    def test_devuelve_la_tarjeta_para_insertarla_sin_recargar(self):
        r = self.client.post(self.url_rapida, {'contenido': 'Sin recargar'},
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        html = r.json()['html']
        self.assertIn('publicacion-card', html)
        self.assertIn('Sin recargar', html)
        # La tarjeta recién creada no puede mostrar contadores vacíos ni romper.
        self.assertIn('btn-reaccion', html)

    def test_sin_javascript_sigue_redirigiendo(self):
        """Fallback para quien envíe el formulario sin AJAX."""
        r = self.client.post(self.url_rapida, {'contenido': 'Sin JS'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Publicacion.objects.count(), 1)


class ReaccionTests(FeedBaseTestCase):
    """El botón alterna: una sola reacción por persona y publicación."""

    def setUp(self):
        super().setUp()
        self.publicacion = Publicacion.objects.create(
            autor=self.empleado, titulo='', contenido='Publicación de prueba',
        )
        self.url = reverse('employees:alternar_reaccion', args=[self.publicacion.pk])

    def test_alternar_pone_y_quita(self):
        r1 = self.client.post(self.url).json()
        self.assertTrue(r1['reaccionado'])
        self.assertEqual(r1['total'], 1)

        r2 = self.client.post(self.url).json()
        self.assertFalse(r2['reaccionado'])
        self.assertEqual(r2['total'], 0)

    def test_no_se_acumulan_reacciones_de_la_misma_persona(self):
        for _ in range(5):
            self.client.post(self.url)
        # Número impar de clics: queda puesta, pero solo una fila.
        self.assertEqual(
            Reaccion.objects.filter(publicacion=self.publicacion).count(), 1,
        )

    def test_cada_empleado_cuenta_por_separado(self):
        otro_user, _ = self.crear_empleado('luis.prueba', '222')
        self.client.post(self.url)
        self.client.force_login(otro_user)
        r = self.client.post(self.url).json()
        self.assertEqual(r['total'], 2)

    def test_exige_sesion(self):
        self.client.logout()
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 302)


class ContadoresDelFeedTests(FeedBaseTestCase):
    """Unir comentarios y reacciones en la misma consulta multiplica filas:
    sin distinct=True los dos contadores salen inflados."""

    def test_los_contadores_no_se_inflan_entre_si(self):
        publicacion = Publicacion.objects.create(
            autor=self.empleado, titulo='', contenido='Con actividad',
        )
        for i in range(3):
            Comentario.objects.create(
                publicacion=publicacion, autor=self.empleado, contenido=f'C{i}',
            )
        otro_user, otro_emp = self.crear_empleado('eva.prueba', '333')
        Reaccion.objects.create(publicacion=publicacion, autor=self.empleado)
        Reaccion.objects.create(publicacion=publicacion, autor=otro_emp)

        r = self.client.get(reverse('employees:feed_list'))
        encontrada = next(p for p in r.context['publicaciones'] if p.pk == publicacion.pk)
        self.assertEqual(encontrada.num_comentarios, 3)
        self.assertEqual(encontrada.num_reacciones, 2)

    def test_el_feed_marca_si_el_usuario_ya_reacciono(self):
        publicacion = Publicacion.objects.create(
            autor=self.empleado, titulo='', contenido='Reaccionada',
        )
        r = self.client.get(reverse('employees:feed_list'))
        encontrada = next(p for p in r.context['publicaciones'] if p.pk == publicacion.pk)
        self.assertFalse(encontrada.reaccionado)

        Reaccion.objects.create(publicacion=publicacion, autor=self.empleado)
        r = self.client.get(reverse('employees:feed_list'))
        encontrada = next(p for p in r.context['publicaciones'] if p.pk == publicacion.pk)
        self.assertTrue(encontrada.reaccionado)


class VigenciaYEnlacesTests(FeedBaseTestCase):
    """Las publicaciones de empleados duran 30 días y sus URL son enlaces."""

    def publicar(self, texto):
        self.client.post(self.url_rapida, {'contenido': texto},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return Publicacion.objects.latest('fecha_creacion')

    def test_la_publicacion_vence_a_los_30_dias(self):
        """La señal post_save le ponía 15 días y pisaba lo que fijaba la vista."""
        from django.utils import timezone
        publicacion = self.publicar('Hola')
        dias = (publicacion.fecha_eliminacion_automatica - timezone.now()).days
        self.assertIn(dias, (29, 30))

    def test_el_feed_oculta_las_vencidas(self):
        from datetime import timedelta
        from django.utils import timezone
        vencida = self.publicar('vieja')
        Publicacion.objects.filter(pk=vencida.pk).update(
            fecha_eliminacion_automatica=timezone.now() - timedelta(minutes=1))
        vigente = self.publicar('nueva')
        ids = [p.pk for p in self.client.get(reverse('employees:feed_list')).context['publicaciones']]
        self.assertIn(vigente.pk, ids)
        self.assertNotIn(vencida.pk, ids)

    def test_las_url_se_vuelven_enlaces_que_abren_en_otra_pestana(self):
        self.publicar('Miren esto https://www.ejemplo.com/noticia?id=5 y www.otro.co')
        html = self.client.get(reverse('employees:feed_list')).content.decode()
        self.assertIn('<a href="https://www.ejemplo.com/noticia?id=5" target="_blank" '
                      'rel="nofollow noopener noreferrer">', html)
        self.assertIn('href="http://www.otro.co"', html)

    def test_el_texto_sigue_escapado(self):
        self.publicar('<script>alert(1)</script> https://ejemplo.com')
        html = self.client.get(reverse('employees:feed_list')).content.decode()
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_el_editor_completo_redirige_al_feed(self):
        r = self.client.get('/empleados/feed/publicacion/crear/')
        self.assertRedirects(r, reverse('employees:feed_list'), fetch_redirect_response=False)

    def test_el_comentario_de_plantilla_no_se_ve_en_la_pagina(self):
        html = self.client.get(reverse('employees:feed_list')).content.decode()
        self.assertNotIn('{#', html)
        self.assertNotIn('Editor Completo', html)
