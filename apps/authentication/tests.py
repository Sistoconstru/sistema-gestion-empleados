from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class ForzarCambioPasswordTests(TestCase):
    """Cubre el bloqueo del ForzarCambioPasswordMiddleware y su única salida."""

    def setUp(self):
        self.password = 'Temporal-9f3kd0'
        self.usuario = User.objects.create_user(
            username='prueba.flag',
            password=self.password,
            debe_cambiar_password=True,
        )
        self.url_cambio = reverse('authentication:password_change')

    def test_redirige_al_cambio_desde_cualquier_pagina(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get('/empleados/')
        self.assertRedirects(respuesta, self.url_cambio, fetch_redirect_response=False)

    def test_la_pagina_de_cambio_es_accesible(self):
        """Si el middleware también la redirigiera, el usuario quedaría en bucle."""
        self.client.force_login(self.usuario)
        respuesta = self.client.get(self.url_cambio)
        self.assertEqual(respuesta.status_code, 200)

    def test_logout_accesible_con_el_flag_activo(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse('authentication:logout'))
        self.assertIn(respuesta.status_code, (200, 302))

    def test_cambiar_la_password_apaga_el_flag_y_libera_la_navegacion(self):
        self.client.force_login(self.usuario)
        nueva = 'Otra-Clave-2026-xyz'
        respuesta = self.client.post(self.url_cambio, {
            'old_password': self.password,
            'new_password1': nueva,
            'new_password2': nueva,
        })
        self.assertRedirects(
            respuesta,
            reverse('authentication:password_change_done'),
            fetch_redirect_response=False,
        )

        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.debe_cambiar_password)
        self.assertTrue(self.usuario.check_password(nueva))

        # Ya no debe redirigir al cambio de contraseña.
        respuesta = self.client.get('/empleados/')
        self.assertNotIn(self.url_cambio, respuesta.get('Location', ''))

    def test_usuario_sin_el_flag_navega_normal(self):
        otro = User.objects.create_user(username='sin.flag', password='x-9slek31')
        self.client.force_login(otro)
        respuesta = self.client.get('/empleados/')
        self.assertNotIn(self.url_cambio, respuesta.get('Location', ''))


class ProxyPdfTests(TestCase):
    """El proxy de PDF no puede entregar nada fuera de MEDIA_ROOT ni sin sesión."""

    def setUp(self):
        self.url = reverse('documents:proxy_pdf')

    def test_exige_sesion(self):
        respuesta = self.client.get(self.url, {'file': '/media/x.pdf'})
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login', respuesta['Location'])

    def test_bloquea_el_escape_de_media_root(self):
        usuario = User.objects.create_user(username='lector', password='x-9slek31')
        self.client.force_login(usuario)
        for intento in ('/media/../secreto.pdf', '/media/../../secreto.pdf',
                        '/media/sub/../../../secreto.pdf'):
            with self.subTest(intento=intento):
                respuesta = self.client.get(self.url, {'file': intento})
                self.assertIn(respuesta.status_code, (400, 403, 404))

    def test_rechaza_origenes_externos_que_no_son_el_bucket(self):
        usuario = User.objects.create_user(username='lector2', password='x-9slek31')
        self.client.force_login(usuario)
        for intento in ('https://example.com/amazonaws.com',
                        'https://b.s3.sa-east-1.amazonaws.com.evil.com/a.pdf'):
            with self.subTest(intento=intento):
                respuesta = self.client.get(self.url, {'file': intento})
                self.assertEqual(respuesta.status_code, 403)


class EmpleadoExportTests(TestCase):
    """La exportación masiva de la nómina es solo para staff."""

    def setUp(self):
        self.url = reverse('employees:empleado_export')

    def test_anonimo_no_puede_exportar(self):
        respuesta = self.client.get(self.url, {'export': 'csv'})
        self.assertEqual(respuesta.status_code, 302)

    def test_empleado_sin_privilegios_no_puede_exportar(self):
        usuario = User.objects.create_user(username='raso', password='x-9slek31')
        self.client.force_login(usuario)
        respuesta = self.client.get(self.url, {'export': 'csv'})
        self.assertEqual(respuesta.status_code, 302)
        self.assertNotEqual(respuesta.get('Content-Type', ''), 'text/csv; charset=utf-8')
