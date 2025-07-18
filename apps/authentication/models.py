# =============================================================================
# apps/authentication/models.py
# =============================================================================

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telefono = models.CharField(max_length=15)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]


class Rol(models.Model):
    """Roles del sistema"""
    nombre = models.CharField(max_length=50, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    nivel_jerarquico = models.IntegerField(default=1)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre


class ModuloSistema(models.Model):
    """Módulos del sistema"""
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=30, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'modulos_sistema'
        verbose_name = 'Módulo del Sistema'
        verbose_name_plural = 'Módulos del Sistema'
    
    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    """Permisos del sistema"""
    ACCIONES = [
        ('create', 'Crear'),
        ('read', 'Leer'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('approve', 'Aprobar'),
        ('assign', 'Asignar'),
    ]
    
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    modulo = models.ForeignKey(ModuloSistema, on_delete=models.CASCADE)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    
    class Meta:
        db_table = 'permisos'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
    
    def __str__(self):
        return f"{self.nombre} - {self.get_accion_display()}"


class RolPermiso(models.Model):
    """Relación muchos a muchos entre roles y permisos"""
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    asignado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'roles_permisos'
        unique_together = ['rol', 'permiso']


class UsuarioRol(models.Model):
    """Relación muchos a muchos entre usuarios y roles"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    asignado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='asignaciones_realizadas')
    
    class Meta:
        db_table = 'usuarios_roles'
        unique_together = ['usuario', 'rol']
