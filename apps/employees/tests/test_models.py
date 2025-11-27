"""
Tests para modelos del marketplace
"""
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.employees.models import (
    Empleado, Producto, Venta, Subasta, PujaSubasta,
    Regalo, Conversacion, Mensaje, Categoria, EstadoEmpleado,
    TipoDocumento
)
from apps.organizational.models import Sede

User = get_user_model()


class ProductoModelTest(TestCase):
    """Tests para el modelo Producto"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.empleado = Empleado.objects.create(
            usuario=self.user,
            tipo_documento=self.tipo_doc,
            nombres='Test',
            apellidos='User',
            numero_documento='12345678',
            telefono_contacto='3101234567',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3109876543',
            direccion='Calle Principal 123',
            creado_por=self.user
        )
        self.categoria = Categoria.objects.create(
            nombre='Electrónica',
            descripcion='Productos electrónicos'
        )

    def test_crear_producto_venta(self):
        """Test crear producto de venta"""
        producto = Producto.objects.create(
            titulo='Laptop',
            descripcion='Laptop de prueba' * 5,
            tipo='venta',
            precio_inicial=1500.00,
            vendedor=self.empleado,
            categoria=self.categoria,
            creado_por=self.user
        )
        self.assertEqual(producto.titulo, 'Laptop')
        self.assertEqual(producto.tipo, 'venta')
        self.assertEqual(producto.estado, 'activo')
        self.assertEqual(producto.vendedor, self.empleado)

    def test_crear_producto_regalo(self):
        """Test crear producto de regalo sin precio"""
        producto = Producto.objects.create(
            titulo='Libro',
            descripcion='Libro de prueba' * 5,
            tipo='regalo',
            vendedor=self.empleado,
            categoria=self.categoria,
            creado_por=self.user
        )
        self.assertEqual(producto.tipo, 'regalo')
        self.assertIsNone(producto.precio_inicial)

    def test_crear_producto_subasta(self):
        """Test crear producto para subasta"""
        producto = Producto.objects.create(
            titulo='Reloj',
            descripcion='Reloj de prueba' * 5,
            tipo='subasta',
            precio_inicial=200.00,
            vendedor=self.empleado,
            categoria=self.categoria,
            creado_por=self.user
        )
        self.assertEqual(producto.tipo, 'subasta')
        self.assertEqual(producto.precio_inicial, 200.00)

    def test_producto_uuid_generated(self):
        """Test que se genera UUID automáticamente"""
        producto = Producto.objects.create(
            titulo='Producto UUID',
            descripcion='Prueba UUID' * 5,
            tipo='venta',
            precio_inicial=100.00,
            vendedor=self.empleado,
            categoria=self.categoria,
            creado_por=self.user
        )
        self.assertIsNotNone(producto.id)
        self.assertTrue(len(str(producto.id)) > 0)


class VentaModelTest(TestCase):
    """Tests para el modelo Venta"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user_vendedor = User.objects.create_user(
            username='vendedor',
            email='vendedor@test.com',
            password='testpass123'
        )
        self.user_comprador = User.objects.create_user(
            username='comprador',
            email='comprador@test.com',
            password='testpass123'
        )
        self.vendedor = Empleado.objects.create(
            usuario=self.user_vendedor,
            tipo_documento=self.tipo_doc,
            nombres='Juan',
            apellidos='Vendedor',
            numero_documento='111',
            telefono_contacto='3101234567',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3109876543',
            direccion='Calle Principal 123',
            creado_por=self.user_vendedor
        )
        self.comprador = Empleado.objects.create(
            usuario=self.user_comprador,
            tipo_documento=self.tipo_doc,
            nombres='Carlos',
            apellidos='Comprador',
            numero_documento='222',
            telefono_contacto='3105551234',
            fecha_ingreso=date.today(),
            sede=self.sede,
            estado=self.estado,
            contacto_emergencia_telefono='3105559876',
            direccion='Calle Secundaria 456',
            creado_por=self.user_comprador
        )
        self.categoria = Categoria.objects.create(
            nombre='Test'
        )
        self.producto = Producto.objects.create(
            titulo='Test Producto',
            descripcion='Descripción' * 5,
            tipo='venta',
            precio_inicial=100.00,
            vendedor=self.vendedor,
            categoria=self.categoria,
            creado_por=self.user_vendedor
        )

    def test_crear_venta(self):
        """Test crear venta"""
        venta = Venta.objects.create(
            producto=self.producto,
            vendedor=self.vendedor,
            comprador=self.comprador,
            precio_final=100.00,
            creado_por=self.user_comprador
        )
        self.assertEqual(venta.producto, self.producto)
        self.assertEqual(venta.precio_final, 100.00)
        self.assertEqual(venta.estado, 'pendiente_vendedor')

    def test_venta_cambiar_estado(self):
        """Test cambiar estado de venta"""
        venta = Venta.objects.create(
            producto=self.producto,
            vendedor=self.vendedor,
            comprador=self.comprador,
            precio_final=100.00,
            creado_por=self.user_comprador
        )
        venta.estado = 'completada'
        venta.save()
        venta.refresh_from_db()
        self.assertEqual(venta.estado, 'completada')


class RegaloModelTest(TestCase):
    """Tests para el modelo Regalo"""

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
        self.categoria = Categoria.objects.create(nombre='Test')
        self.producto = Producto.objects.create(
            titulo='Producto Regalo',
            descripcion='Test' * 5,
            tipo='regalo',
            vendedor=self.empleado1,
            categoria=self.categoria,
            creado_por=self.user1
        )

    def test_crear_regalo(self):
        """Test crear regalo"""
        regalo = Regalo.objects.create(
            producto=self.producto,
            donante=self.empleado1,
            receptor=self.empleado2,
            mensaje='Felicidades!',
            creado_por=self.user1
        )
        self.assertEqual(regalo.donante, self.empleado1)
        self.assertEqual(regalo.receptor, self.empleado2)
        self.assertEqual(regalo.estado, 'pendiente')

    def test_regalo_aceptar(self):
        """Test aceptar regalo"""
        regalo = Regalo.objects.create(
            producto=self.producto,
            donante=self.empleado1,
            receptor=self.empleado2,
            creado_por=self.user1
        )
        regalo.estado = 'aceptado'
        regalo.save()
        regalo.refresh_from_db()
        self.assertEqual(regalo.estado, 'aceptado')


class ConversacionModelTest(TestCase):
    """Tests para el modelo Conversacion"""

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

    def test_crear_conversacion(self):
        """Test crear conversación"""
        conversacion = Conversacion.objects.create(
            titulo='Test Chat',
            contexto='general',
            creado_por=self.user1
        )
        conversacion.participantes.add(self.empleado1, self.empleado2)

        self.assertEqual(conversacion.titulo, 'Test Chat')
        self.assertEqual(conversacion.contexto, 'general')
        self.assertEqual(conversacion.participantes.count(), 2)

    def test_crear_mensaje(self):
        """Test crear mensaje en conversación"""
        conversacion = Conversacion.objects.create(
            contexto='general',
            creado_por=self.user1
        )
        conversacion.participantes.add(self.empleado1, self.empleado2)

        mensaje = Mensaje.objects.create(
            conversacion=conversacion,
            remitente=self.empleado1,
            contenido='Hola, cómo estás?',
            creado_por=self.user1
        )

        self.assertEqual(mensaje.contenido, 'Hola, cómo estás?')
        self.assertEqual(mensaje.remitente, self.empleado1)
