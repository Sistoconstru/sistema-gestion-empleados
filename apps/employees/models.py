from django.db import models

# Create your models here.
# =============================================================================
# apps/employees/models.py
# =============================================================================

import uuid
from django.db import models
from django.contrib.auth.models import Group



class TipoDocumento(models.Model):
    """Tipos de documento de identificación"""
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    requiere_numero = models.BooleanField(default=True)
    longitud_minima = models.IntegerField(default=8)
    longitud_maxima = models.IntegerField(default=15)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_documento'
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
    
    def __str__(self):
        return self.nombre


class Escolaridad(models.Model):
    """Niveles de escolaridad"""
    codigo = models.CharField(max_length=10, unique=True)
    nivel = models.CharField(max_length=50, unique=True)
    orden = models.IntegerField(unique=True)
    
    class Meta:
        db_table = 'escolaridad'
        ordering = ['orden']
        verbose_name = 'Escolaridad'
        verbose_name_plural = 'Escolaridades'
    
    def __str__(self):
        return self.nivel


class EstadoEmpleado(models.Model):
    """Estados de empleados"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.TextField(blank=True)
    permite_acceso_sistema = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'estados_empleado'
        verbose_name = 'Estado de Empleado'
        verbose_name_plural = 'Estados de Empleado'
    
    def __str__(self):
        return self.nombre



# ===================== NUEVOS MODELOS =====================
class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='ciudades')

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['nombre']
        unique_together = ('nombre', 'departamento')

    def __str__(self):
        return f"{self.nombre} ({self.departamento.nombre})"

# ===================== MODELO EMPLEADO =====================
class Empleado(models.Model):
    """Modelo principal de empleados"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        'authentication.Usuario', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Usuario del sistema (se crea automáticamente)"
    )
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    numero_documento = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono_contacto = models.CharField(max_length=15)
    fecha_ingreso = models.DateField()
    sede = models.ForeignKey('organizational.Sede', on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoEmpleado, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField(null=True, blank=False)
    ciudad_nacimiento = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, blank=True)  # Nuevo campo FK
    escolaridad = models.ForeignKey(Escolaridad, on_delete=models.SET_NULL, null=True, blank=True)
    contacto_emergencia_nombre = models.CharField(max_length=100, blank=True)
    contacto_emergencia_telefono = models.CharField(max_length=15, blank=False)
    correo_electronico = models.EmailField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='empleados_creados')

    class Meta:
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['estado']),
            models.Index(fields=['sede']),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class HistorialCargo(models.Model):
    """Historial de cargos de empleados"""
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    salario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    activo = models.BooleanField(default=True)
    motivo_cambio = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'historial_cargos'
        unique_together = ['empleado', 'activo']
        verbose_name = 'Historial de Cargo'
        verbose_name_plural = 'Historiales de Cargo'


