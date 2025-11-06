# =============================================================================
# apps/authentication/models.py
# =============================================================================

import uuid
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils import timezone

# Modelo de usuario personalizado que extiende AbstractUser
class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único
    telefono = models.CharField(max_length=15)  # Teléfono del usuario
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Fecha de última actualización
    ultimo_acceso = models.DateTimeField(null=True, blank=True)  # Último acceso al sistema
    
    class Meta:
        db_table = 'usuarios'  # Nombre de la tabla en la BD
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['email']),  # Índice para búsquedas por email
            models.Index(fields=['is_active']),  # Índice para búsquedas por estado activo
        ]


# Modelo para los roles del sistema
class Rol(models.Model):
    """Roles del sistema"""
    nombre = models.CharField(max_length=50, unique=True)  # Nombre del rol
    codigo = models.CharField(max_length=20, unique=True)  # Código único del rol
    descripcion = models.TextField(blank=True)  # Descripción opcional
    nivel_jerarquico = models.IntegerField(default=1)  # Nivel jerárquico del rol
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre  # Representación en texto


# Modelo para los módulos del sistema
class ModuloSistema(models.Model):
    """Módulos del sistema"""
    nombre = models.CharField(max_length=100, unique=True)  # Nombre del módulo
    codigo = models.CharField(max_length=30, unique=True)  # Código único del módulo
    descripcion = models.TextField(blank=True)  # Descripción opcional
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    
    class Meta:
        db_table = 'modulos_sistema'
        verbose_name = 'Módulo del Sistema'
        verbose_name_plural = 'Módulos del Sistema'
    
    def __str__(self):
        return self.nombre


# Modelo para los permisos del sistema
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
    
    nombre = models.CharField(max_length=100)  # Nombre del permiso
    codigo = models.CharField(max_length=50, unique=True)  # Código único del permiso
    descripcion = models.TextField(blank=True)  # Descripción opcional
    modulo = models.ForeignKey(ModuloSistema, on_delete=models.CASCADE)  # Módulo asociado
    accion = models.CharField(max_length=20, choices=ACCIONES)  # Acción permitida
    
    class Meta:
        db_table = 'permisos'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
    
    def __str__(self):
        return f"{self.nombre} - {self.get_accion_display()}"  # Representación en texto


# Modelo para la relación muchos a muchos entre roles y permisos
class RolPermiso(models.Model):
    """Relación muchos a muchos entre roles y permisos"""
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)  # Rol asociado
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)  # Permiso asociado
    grupo = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Grupo de permisos")
    fecha_asignacion = models.DateTimeField(auto_now_add=True)  # Fecha de asignación
    asignado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que asigna el permiso
    
    class Meta:
        db_table = 'roles_permisos'
        unique_together = ['rol', 'permiso', 'grupo']  # Relación única por rol y permiso


# Modelo para la relación muchos a muchos entre usuarios y roles
class UsuarioRol(models.Model):
    """Relación muchos a muchos entre usuarios y roles"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario asociado
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)  # Rol asociado
    fecha_asignacion = models.DateTimeField(auto_now_add=True)  # Fecha de asignación
    fecha_expiracion = models.DateField(null=True, blank=True)  # Fecha de expiración opcional
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    asignado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='asignaciones_realizadas')  # Usuario que asigna el rol
    
    class Meta:
        db_table = 'usuarios_roles'
        unique_together = ['usuario', 'rol']  # Relación única por usuario y rol
