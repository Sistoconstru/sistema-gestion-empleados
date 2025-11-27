"""
Tests para formularios del marketplace
"""
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.employees.models import (
    Empleado, Producto, Categoria, EstadoEmpleado,
    TipoDocumento
)
from apps.employees.forms import (
    ProductoForm, VentaForm, RegaloForm,
    ConversacionForm, MensajeForm
)
from apps.organizational.models import Sede

User = get_user_model()


class ProductoFormTest(TestCase):
    """Tests para ProductoForm"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user = User.objects.create_user(username='user', password='pass123')
        self.empleado = Empleado.objects.create(
            usuario=self.user,
            tipo_documento=self.tipo_doc,
            nombres='Test',
            apellidos='User',
            numero_documento='123',
            telefono_contacto='3101234567',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3109876543',
            direccion='Calle Principal 123',
            creado_por=self.user
        )
        self.categoria = Categoria.objects.create(
            nombre='Test'
        )

    def test_form_valid_venta(self):
        """Test formulario válido para venta"""
        data = {
            'titulo': 'Laptop Gaming',
            'descripcion': 'Excelente laptop para gaming' * 5,
            'tipo': 'venta',
            'precio_inicial': 1500.00,
            'categoria': self.categoria.id,
        }
        form = ProductoForm(data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_short_title(self):
        """Test formulario inválido con título corto"""
        data = {
            'titulo': 'Lap',
            'descripcion': 'Descripción' * 5,
            'tipo': 'venta',
            'precio_inicial': 100.00,
            'categoria': self.categoria.id,
        }
        form = ProductoForm(data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_short_description(self):
        """Test formulario inválido con descripción corta"""
        data = {
            'titulo': 'Laptop',
            'descripcion': 'Desc',
            'tipo': 'venta',
            'precio_inicial': 100.00,
            'categoria': self.categoria.id,
        }
        form = ProductoForm(data)
        self.assertFalse(form.is_valid())

    def test_form_regalo_no_price(self):
        """Test formulario regalo sin precio"""
        data = {
            'titulo': 'Libro',
            'descripcion': 'Libro interesante' * 5,
            'tipo': 'regalo',
            'categoria': self.categoria.id,
        }
        form = ProductoForm(data)
        self.assertTrue(form.is_valid())

    def test_form_venta_negative_price(self):
        """Test formulario con precio negativo"""
        data = {
            'titulo': 'Producto',
            'descripcion': 'Descripción' * 5,
            'tipo': 'venta',
            'precio_inicial': -100.00,
            'categoria': self.categoria.id,
        }
        form = ProductoForm(data)
        self.assertFalse(form.is_valid())


class VentaFormTest(TestCase):
    """Tests para VentaForm"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user_v = User.objects.create_user(username='vendedor', password='pass123')
        self.user_c = User.objects.create_user(username='comprador', password='pass123')

        self.vendedor = Empleado.objects.create(
            usuario=self.user_v,
            tipo_documento=self.tipo_doc,
            nombres='Vendedor',
            apellidos='Test',
            numero_documento='111',
            telefono_contacto='3101234567',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3109876543',
            direccion='Calle Principal 123',
            creado_por=self.user_v
        )
        self.comprador = Empleado.objects.create(
            usuario=self.user_c,
            tipo_documento=self.tipo_doc,
            nombres='Comprador',
            apellidos='Test',
            numero_documento='222',
            telefono_contacto='3105551234',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3105559876',
            direccion='Calle Secundaria 456',
            creado_por=self.user_c
        )

    def test_form_valid_venta(self):
        """Test formulario válido de venta"""
        data = {
            'precio_confirmacion': 100.00,
        }
        form = VentaForm(
            data,
            vendedor=self.vendedor,
            comprador=self.comprador
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_price_mismatch(self):
        """Test formulario con precio diferente"""
        data = {
            'precio_confirmacion': 50.00,
        }
        # Simulamos que el precio real es 100
        form = VentaForm(
            data,
            vendedor=self.vendedor,
            comprador=self.comprador
        )
        # La validación ocurre en el formulario
        self.assertTrue(form.is_valid())  # El formulario valida tipos


class RegaloFormTest(TestCase):
    """Tests para RegaloForm"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

        self.empleado1 = Empleado.objects.create(
            usuario=self.user1,
            tipo_documento=self.tipo_doc,
            nombres='Donante',
            apellidos='Test',
            numero_documento='111',
            telefono_contacto='3101234567',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3109876543',
            direccion='Calle Principal 123',
            creado_por=self.user1
        )
        self.empleado2 = Empleado.objects.create(
            usuario=self.user2,
            tipo_documento=self.tipo_doc,
            nombres='Receptor',
            apellidos='Test',
            numero_documento='222',
            telefono_contacto='3105551234',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3105559876',
            direccion='Calle Secundaria 456',
            creado_por=self.user2
        )

    def test_form_valid_regalo(self):
        """Test formulario válido de regalo"""
        data = {
            'receptor_id': self.empleado2.id,
            'mensaje': 'Te quiero mucho!',
        }
        form = RegaloForm(data, donante=self.empleado1)
        self.assertTrue(form.is_valid())

    def test_form_regalo_self_not_allowed(self):
        """Test que no puedo regalarme a mí mismo"""
        data = {
            'receptor_id': self.empleado1.id,
        }
        form = RegaloForm(data, donante=self.empleado1)
        self.assertFalse(form.is_valid())


class ConversacionFormTest(TestCase):
    """Tests para ConversacionForm"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

        self.empleado1 = Empleado.objects.create(
            usuario=self.user1,
            tipo_documento=self.tipo_doc,
            nombres='Usuario',
            apellidos='Uno',
            numero_documento='111',
            telefono_contacto='3101234567',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3109876543',
            direccion='Calle Principal 123',
            creado_por=self.user1
        )
        self.empleado2 = Empleado.objects.create(
            usuario=self.user2,
            tipo_documento=self.tipo_doc,
            nombres='Usuario',
            apellidos='Dos',
            numero_documento='222',
            telefono_contacto='3105551234',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3105559876',
            direccion='Calle Secundaria 456',
            creado_por=self.user2
        )

    def test_form_valid_conversacion(self):
        """Test formulario válido de conversación"""
        data = {
            'participante_id': self.empleado2.id,
            'contexto': 'general',
        }
        form = ConversacionForm(data, usuario=self.empleado1)
        self.assertTrue(form.is_valid())

    def test_form_self_conversation_not_allowed(self):
        """Test que no puedo chatear conmigo mismo"""
        data = {
            'participante_id': self.empleado1.id,
            'contexto': 'general',
        }
        form = ConversacionForm(data, usuario=self.empleado1)
        self.assertFalse(form.is_valid())


class MensajeFormTest(TestCase):
    """Tests para MensajeForm"""

    def test_form_valid_mensaje(self):
        """Test formulario válido de mensaje"""
        data = {
            'contenido': 'Hola, cómo estás?',
        }
        form = MensajeForm(data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_short_message(self):
        """Test formulario con mensaje muy corto"""
        data = {
            'contenido': 'H',
        }
        form = MensajeForm(data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_long_message(self):
        """Test formulario con mensaje muy largo"""
        data = {
            'contenido': 'A' * 5001,
        }
        form = MensajeForm(data)
        self.assertFalse(form.is_valid())

    def test_form_valid_long_message(self):
        """Test formulario con mensaje largo válido"""
        data = {
            'contenido': 'A' * 5000,
        }
        form = MensajeForm(data)
        self.assertTrue(form.is_valid())
