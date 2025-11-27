"""
Tests para vistas del marketplace
"""
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.employees.models import (
    Empleado, Producto, Categoria, EstadoEmpleado,
    TipoDocumento
)
from apps.organizational.models import Sede

User = get_user_model()


class ProductoListViewTest(TestCase):
    """Tests para ProductoListView"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.client = Client()
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
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
            nombre='Electrónica'
        )
        # Crear algunos productos
        for i in range(5):
            Producto.objects.create(
                titulo=f'Producto {i}',
                descripcion=f'Descripción {i}' * 5,
                tipo='venta',
                precio_inicial=100.00 * (i + 1),
                vendedor=self.empleado,
                categoria=self.categoria,
                creado_por=self.user
            )

    def test_view_accessible(self):
        """Test que la vista es accesible"""
        response = self.client.get(reverse('employees:producto_list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test que usa el template correcto"""
        response = self.client.get(reverse('employees:producto_list'))
        self.assertTemplateUsed(response, 'employees/marketplace/producto_list.html')

    def test_view_context_has_productos(self):
        """Test que el contexto tiene productos"""
        response = self.client.get(reverse('employees:producto_list'))
        self.assertIn('object_list', response.context)
        self.assertEqual(len(response.context['object_list']), 5)

    def test_view_pagination(self):
        """Test paginación"""
        response = self.client.get(reverse('employees:producto_list'))
        self.assertTrue('is_paginated' in response.context)


class ProductoDetailViewTest(TestCase):
    """Tests para ProductoDetailView"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.client = Client()
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
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
        self.producto = Producto.objects.create(
            titulo='Producto Detail',
            descripcion='Descripción' * 5,
            tipo='venta',
            precio_inicial=100.00,
            vendedor=self.empleado,
            categoria=self.categoria,
            creado_por=self.user
        )

    def test_view_accessible(self):
        """Test que la vista es accesible"""
        response = self.client.get(
            reverse('employees:producto_detail', args=[self.producto.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_view_context_has_producto(self):
        """Test que el contexto tiene el producto"""
        response = self.client.get(
            reverse('employees:producto_detail', args=[self.producto.id])
        )
        self.assertEqual(response.context['object'], self.producto)


class InboxViewTest(TestCase):
    """Tests para InboxView"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.client = Client()
        self.estado = EstadoEmpleado.objects.create(codigo='activo', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='SEDE001', nombre='Sede Principal')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
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

    def test_view_requires_login(self):
        """Test que requiere login"""
        response = self.client.get(reverse('employees:inbox'))
        self.assertEqual(response.status_code, 302)  # Redirect a login

    def test_view_accessible_with_login(self):
        """Test que la vista es accesible con login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('employees:inbox'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test que usa el template correcto"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('employees:inbox'))
        self.assertTemplateUsed(response, 'employees/messaging/inbox.html')
