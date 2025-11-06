from django.db import models

# =============================================================================
# apps/employees/models.py
# =============================================================================

import uuid
from django.db import models
from django.contrib.auth.models import Group

# ===================== MODELOS BÁSICOS =====================

class TipoDocumento(models.Model):
    """Tipos de documento de identificación"""
    codigo = models.CharField(max_length=10, unique=True)  # Código único
    nombre = models.CharField(max_length=50)  # Nombre del documento
    descripcion = models.TextField(blank=True)  # Descripción opcional
    requiere_numero = models.BooleanField(default=True)  # Si requiere número
    longitud_minima = models.IntegerField(default=8)  # Longitud mínima
    longitud_maxima = models.IntegerField(default=15)  # Longitud máxima
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    
    class Meta:
        db_table = 'tipos_documento'
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
    
    def __str__(self):
        return self.nombre

class Escolaridad(models.Model):
    """Niveles de escolaridad"""
    codigo = models.CharField(max_length=10, unique=True)  # Código único
    nivel = models.CharField(max_length=50, unique=True)  # Nombre del nivel
    orden = models.IntegerField(unique=True)  # Orden para mostrar
    
    class Meta:
        db_table = 'escolaridad'
        ordering = ['orden']
        verbose_name = 'Escolaridad'
        verbose_name_plural = 'Escolaridades'
    
    def __str__(self):
        return self.nivel

class EstadoEmpleado(models.Model):
    """Estados de empleados"""
    codigo = models.CharField(max_length=20, unique=True)  # Código único
    nombre = models.CharField(max_length=30, unique=True)  # Nombre del estado
    descripcion = models.TextField(blank=True)  # Descripción opcional
    permite_acceso_sistema = models.BooleanField(default=True)  # Si permite acceso al sistema
    
    class Meta:
        db_table = 'estados_empleado'
        verbose_name = 'Estado de Empleado'
        verbose_name_plural = 'Estados de Empleado'
    
    def __str__(self):
        return self.nombre

# ===================== NUEVOS MODELOS =====================

class Departamento(models.Model):
    """Departamentos para ciudades"""
    nombre = models.CharField(max_length=100, unique=True)  # Nombre del departamento
    codigo = models.CharField(max_length=10, unique=True)  # Código único

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Ciudad(models.Model):
    """Ciudades asociadas a departamentos"""
    nombre = models.CharField(max_length=100)  # Nombre de la ciudad
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='ciudades')  # Departamento asociado

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único
    usuario = models.OneToOneField(
        'authentication.Usuario', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Usuario del sistema (se crea automáticamente)"
    )
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)  # Tipo de documento
    numero_documento = models.CharField(max_length=20, unique=True)  # Número de documento
    nombres = models.CharField(max_length=100)  # Nombres
    apellidos = models.CharField(max_length=100)  # Apellidos
    telefono_contacto = models.CharField(max_length=15)  # Teléfono de contacto
    fecha_ingreso = models.DateField()  # Fecha de ingreso
    sede = models.ForeignKey('organizational.Sede', on_delete=models.CASCADE)  # Sede asociada
    estado = models.ForeignKey(EstadoEmpleado, on_delete=models.CASCADE)  # Estado actual
    fecha_nacimiento = models.DateField(null=True, blank=False)  # Fecha de nacimiento
    ciudad_nacimiento = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, blank=True)  # Ciudad de nacimiento
    escolaridad = models.ForeignKey(Escolaridad, on_delete=models.SET_NULL, null=True, blank=True)  # Escolaridad
    contacto_emergencia_nombre = models.CharField(max_length=100, blank=True)  # Nombre contacto emergencia
    contacto_emergencia_telefono = models.CharField(max_length=15, blank=False)  # Teléfono contacto emergencia
    correo_electronico = models.EmailField(blank=True)  # Email
    direccion = models.CharField(max_length=200, blank=False, help_text="Dirección de residencia (debe iniciar con el tipo de vía completo)")  # Dirección de residencia
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Fecha de última actualización
    creado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='empleados_creados')  # Usuario que creó el registro

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
        """Retorna el nombre completo del empleado"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def cargo_actual(self):
        """Retorna el historial de cargo actual del empleado"""
        try:
            historial = self.historialcargo_set.filter(activo=True).first()
            return historial
        except:
            return None
    
    @property
    def nombre_cargo_actual(self):
        """Retorna el nombre del cargo actual del empleado"""
        try:
            historial = self.historialcargo_set.filter(activo=True).first()
            if historial:
                return historial.cargo.nombre
            return None
        except:
            return None
    
    @property
    def area_actual(self):
        """Retorna el área actual del empleado basada en su cargo"""
        try:
            historial = self.historialcargo_set.filter(activo=True).first()
            if historial:
                return historial.cargo.area
            return None
        except:
            return None

class HistorialCargo(models.Model):
    """Historial de cargos de empleados"""
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)  # Empleado asociado
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)  # Cargo asociado
    fecha_inicio = models.DateField()  # Fecha de inicio en el cargo
    fecha_fin = models.DateField(null=True, blank=True)  # Fecha de fin en el cargo
    salario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Salario en el cargo
    activo = models.BooleanField(default=True)  # Si el cargo está activo
    motivo_cambio = models.CharField(max_length=200, blank=True)  # Motivo del cambio de cargo
    observaciones = models.TextField(blank=True)  # Observaciones adicionales
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación del registro
    creado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)  # Usuario que creó el registro
    
    class Meta:
        db_table = 'historial_cargos'
        unique_together = ['empleado', 'activo']
        verbose_name = 'Historial de Cargo'
        verbose_name_plural = 'Historiales de Cargo'


