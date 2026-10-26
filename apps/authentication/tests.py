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

    def test_el_cambio_no_queda_registrado_en_claro_en_la_auditoria(self):
        """El POST del cambio de contraseña pasa por AuditLogMiddleware."""
        from apps.core.models import LogActividad

        self.client.force_login(self.usuario)
        nueva = 'Clave-Auditada-2026'
        self.client.post(self.url_cambio, {
            'old_password': self.password,
            'new_password1': nueva,
            'new_password2': nueva,
        })

        # Si no se registrara nada, la comprobación de abajo pasaría sola.
        self.assertTrue(
            LogActividad.objects.exists(),
            'La auditoría no registró el POST: el test no estaría probando nada.',
        )
        registrado = ' '.join(
            str(log.cambios_realizados)
            for log in LogActividad.objects.all()
        )
        self.assertNotIn(nueva, registrado)
        self.assertNotIn(self.password, registrado)


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


class AccesoRasoTests(TestCase):
    """Las vistas administrativas no pueden abrirse con solo tener sesión.

    LoginRequiredMixin autentica pero no autoriza, y los `{% if perms %}` de los
    templates solo esconden botones: antes un empleado sin ningún permiso llegaba
    a la nómina completa y a los reportes de RRHH escribiendo la URL.
    """

    # Rutas administrativas: un empleado raso no debe pasar.
    RESTRINGIDAS = [
        '/empleados/',
        '/empleados/periodo-prueba/',
        '/capacitaciones/admin/',
        '/reportes/',
        '/reportes/asistencia/',
        '/reportes/evaluations/',
        '/reportes/novedades/',
        '/reportes/aprendices-sena/',
    ]

    def setUp(self):
        self.raso = User.objects.create_user(username='raso.sinpermisos', password='x-9slek31')
        self.staff = User.objects.create_user(
            username='admin.rrhh', password='x-9slek31', is_staff=True,
        )

    def test_el_empleado_raso_no_entra(self):
        self.client.force_login(self.raso)
        self.assertEqual(self.raso.get_all_permissions(), set())
        for url in self.RESTRINGIDAS:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertIn(
                    r.status_code, (302, 403),
                    f'{url} se abrió con status {r.status_code} para una cuenta sin permisos',
                )

    def test_el_staff_si_entra(self):
        """Contrapeso: si esto falla, la restricción rompió a RRHH.

        No se exige 200 porque algunas de estas vistas redirigen según los datos
        (periodo-prueba vuelve al listado si falta el EstadoEmpleado 'p-prue', y
        en la base de test no hay ninguno). Lo que se comprueba es que a staff no
        se le niegue el paso: ni 403 ni rebote al login.
        """
        self.client.force_login(self.staff)
        for url in self.RESTRINGIDAS:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertNotEqual(r.status_code, 403, f'{url} dio 403 a staff')
                destino = r.get('Location', '')
                self.assertNotIn('login', destino, f'{url} mandó a staff al login ({destino})')

    def test_el_anonimo_va_al_login_no_a_un_403(self):
        r = self.client.get('/empleados/')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/auth/login/', r['Location'])

    def test_el_empleado_conserva_sus_propias_secciones(self):
        self.client.force_login(self.raso)
        for url in ('/encuestas/', '/sorteos/', '/capacitaciones/catalogo/'):
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertNotEqual(
                    r.status_code, 403,
                    f'{url} dejó de ser accesible para un empleado normal',
                )


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


class DashboardAdministrativoTests(TestCase):
    """El dashboard administrativo no se alcanza sin privilegios."""

    def test_usuario_sin_ficha_ni_privilegios_no_llega_al_dashboard(self):
        """El `except Empleado.DoesNotExist: pass` lo dejaba caer al de admin."""
        huerfano = User.objects.create_user(username='sin.ficha', password='x-9slek31')
        self.client.force_login(huerfano)
        r = self.client.get('/dashboard/')
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('dashboard', r['Location'])

    def test_staff_si_llega_al_dashboard(self):
        admin = User.objects.create_user(
            username='admin.dash', password='x-9slek31', is_staff=True,
        )
        self.client.force_login(admin)
        r = self.client.get('/dashboard/')
        self.assertEqual(r.status_code, 200)


class LimiteIntentosLoginTests(TestCase):
    """django-axes: cinco fallos seguidos y la cuenta queda bloqueada."""

    PASSWORD = 'Correcta-9slek31'

    def setUp(self):
        from axes.utils import reset
        reset()  # el contador vive en BD y en caché; se limpia entre tests
        self.usuario = User.objects.create_user(username='victima', password=self.PASSWORD)

    def _fallar(self, veces):
        for _ in range(veces):
            self.client.post('/login/', {'username': 'victima', 'password': 'incorrecta'})

    def test_el_sexto_intento_queda_bloqueado(self):
        self._fallar(5)
        # Incluso con la contraseña correcta: el bloqueo es por cuenta, no por
        # acierto. Si esto devolviera 302 el límite no se estaría aplicando.
        r = self.client.post('/login/', {'username': 'victima', 'password': self.PASSWORD})
        self.assertEqual(r.status_code, 429, 'axes responde 429 Too Many Requests al bloquear')
        self.assertNotIn('_auth_user_id', self.client.session)
        # Y se muestra la plantilla propia, no el 429 pelado de axes.
        self.assertContains(r, 'Acceso bloqueado', status_code=429)
        self.assertContains(r, '30 minutos', status_code=429)

    def test_cuatro_fallos_no_bloquean(self):
        self._fallar(4)
        r = self.client.post('/login/', {'username': 'victima', 'password': self.PASSWORD})
        self.assertEqual(r.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_un_acierto_reinicia_el_contador(self):
        """AXES_RESET_ON_SUCCESS: cuenta intentos seguidos, no acumulados."""
        self._fallar(4)
        self.client.post('/login/', {'username': 'victima', 'password': self.PASSWORD})
        self.client.logout()
        self._fallar(4)
        r = self.client.post('/login/', {'username': 'victima', 'password': self.PASSWORD})
        self.assertEqual(r.status_code, 302, 'el contador no se reinició tras un login correcto')

    def test_el_bloqueo_no_alcanza_a_otra_cuenta(self):
        """Se bloquea la pareja (usuario, IP), no la IP entera."""
        User.objects.create_user(username='companero', password=self.PASSWORD)
        self._fallar(5)
        r = self.client.post('/login/', {'username': 'companero', 'password': self.PASSWORD})
        self.assertEqual(r.status_code, 302, 'bloquear a uno dejó fuera a un compañero')


class ConfiguracionCuentaTests(TestCase):
    """La página de Configuración del menú de usuario y el cambio voluntario."""

    def setUp(self):
        self.url = reverse('core:configuracion')
        self.usuario = User.objects.create_user(username='empleado.conf', password='Actual-9slek31')

    def test_exige_sesion(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 302)
        self.assertIn('login', r['Location'])

    def test_un_empleado_normal_puede_abrirla(self):
        """Es su propia configuración: no puede quedar restringida a staff."""
        self.client.force_login(self.usuario)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_ofrece_el_cambio_de_contrasena(self):
        self.client.force_login(self.usuario)
        r = self.client.get(self.url)
        self.assertContains(r, reverse('authentication:password_change'))

    def test_el_cambio_voluntario_funciona_sin_tener_el_flag(self):
        self.assertFalse(self.usuario.debe_cambiar_password)
        self.client.force_login(self.usuario)
        nueva = 'Elegida-Por-Mi-2026'
        r = self.client.post(reverse('authentication:password_change'), {
            'old_password': 'Actual-9slek31',
            'new_password1': nueva,
            'new_password2': nueva,
        })
        self.assertEqual(r.status_code, 302)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(nueva))

    def test_el_menu_enlaza_la_configuracion_y_no_un_ancla(self):
        """El item del menú existía apuntando a href="#" y no abría nada.

        Se comprueba sobre la propia página de configuración, que extiende
        base.html y por tanto renderiza el mismo menú de usuario.
        """
        self.client.force_login(self.usuario)
        r = self.client.get(self.url)
        self.assertContains(r, f'href="{self.url}"')
        self.assertContains(r, 'Configuración')
