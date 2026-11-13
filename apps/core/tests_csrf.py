"""CSRF_FAILURE_VIEW: en vez del "Prohibido (403)" en blanco.

Logs de producción (11-13 nov): 6 rechazos en el login por token viejo y 2 en
el formulario del marketplace por envío cortado.
"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class CsrfFalloTests(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_login_con_token_viejo_recarga_el_login(self):
        r = self.client.post('/auth/login/', {'username': 'x', 'password': 'y'})
        self.assertRedirects(r, '/auth/login/', fetch_redirect_response=False)
        r = self.client.get('/auth/login/')
        self.assertContains(r, 'había caducado')

    def test_doble_envio_del_login_con_sesion_ya_iniciada_sigue_adelante(self):
        user = User.objects.create_user(username='ana', password='x-9slek31')
        self.client.force_login(user)
        r = self.client.post('/auth/login/', {'username': 'ana', 'password': 'x-9slek31'})
        self.assertRedirects(r, '/empleados/feed/', fetch_redirect_response=False)

    def test_otro_formulario_explica_y_ofrece_reintentar(self):
        user = User.objects.create_user(username='ana', password='x-9slek31')
        self.client.force_login(user)
        r = self.client.post('/empleados/marketplace/productos/crear/', {})
        self.assertEqual(r.status_code, 403)
        self.assertContains(r, 'No pudimos recibir el formulario', status_code=403)
