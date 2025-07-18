from django.db import models

# Create your models here.
# =============================================================================
# apps/recognition/models.py
# =============================================================================

import uuid
from django.db import models


class TipoActividad(models.Model):
    """Tipos de actividades que otorgan puntos"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    puntos_base = models.IntegerField()
    multiplicador_complejidad = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_actividad'
        verbose_name = 'Tipo de Actividad'
        verbose_name_plural = 'Tipos de Actividad'
    
    def __str__(self):
        return self.nombre


class HistorialPuntos(models.Model):
    """Historial de puntos ganados por empleados"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)
    tipo_actividad = models.ForeignKey(TipoActividad, on_delete=models.CASCADE)
    puntos = models.IntegerField()
    descripcion = models.CharField(max_length=200)
    objeto_relacionado_tipo = models.CharField(max_length=50, blank=True)
    objeto_relacionado_id = models.UUIDField(null=True, blank=True)
    fecha_obtencion = models.DateTimeField(auto_now_add=True)
    validado = models.BooleanField(default=True)
    validado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'historial_puntos'
        verbose_name = 'Historial de Puntos'
        verbose_name_plural = 'Historiales de Puntos'


class TipoReconocimiento(models.Model):
    """Tipos de reconocimientos"""
    PERIODICIDADES = [
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    criterios = models.TextField()
    periodicidad = models.CharField(max_length=20, choices=PERIODICIDADES)
    permite_repetir_empleado = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_reconocimiento'
        verbose_name = 'Tipo de Reconocimiento'
        verbose_name_plural = 'Tipos de Reconocimiento'
    
    def __str__(self):
        return self.nombre


class Reconocimiento(models.Model):
    """Reconocimientos otorgados a empleados"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)
    tipo_reconocimiento = models.ForeignKey(TipoReconocimiento, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=20)
    año = models.IntegerField()
    mes = models.IntegerField(null=True, blank=True)
    trimestre = models.IntegerField(null=True, blank=True)
    puntuacion_obtenida = models.DecimalField(max_digits=8, decimal_places=2)
    posicion = models.IntegerField(null=True, blank=True)
    justificacion = models.TextField()
    beneficio_otorgado = models.TextField(blank=True)
    fecha_otorgamiento = models.DateTimeField(auto_now_add=True)
    otorgado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'reconocimientos'
        unique_together = ['tipo_reconocimiento', 'periodo', 'empleado']
        verbose_name = 'Reconocimiento'
        verbose_name_plural = 'Reconocimientos'


class TipoInsignia(models.Model):
    """Tipos de insignias gamificadas"""
    NIVELES = [
        ('bronce', 'Bronce'),
        ('plata', 'Plata'),
        ('oro', 'Oro'),
        ('platino', 'Platino'),
        ('diamante', 'Diamante'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    criterios = models.TextField()
    icono = models.ImageField(upload_to='insignias/', blank=True)
    color_hex = models.CharField(max_length=7, default='#1f2937')
    nivel = models.CharField(max_length=20, choices=NIVELES, default='bronce')
    puntos_requeridos = models.IntegerField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_insignia'
        verbose_name = 'Tipo de Insignia'
        verbose_name_plural = 'Tipos de Insignia'
    
    def __str__(self):
        return self.nombre


class InsigniaEmpleado(models.Model):
    """Insignias obtenidas por empleados"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)
    tipo_insignia = models.ForeignKey(TipoInsignia, on_delete=models.CASCADE)
    fecha_otorgamiento = models.DateTimeField(auto_now_add=True)
    justificacion = models.TextField(blank=True)
    otorgado_automaticamente = models.BooleanField(default=True)
    otorgado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'insignias_empleado'
        unique_together = ['empleado', 'tipo_insignia']
        verbose_name = 'Insignia de Empleado'
        verbose_name_plural = 'Insignias de Empleado'


class TipoBeneficio(models.Model):
    """Tipos de beneficios canjeables"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50, blank=True)
    costo_puntos = models.IntegerField()
    stock_inicial = models.IntegerField(null=True, blank=True)
    stock_actual = models.IntegerField(null=True, blank=True)
    imagen = models.ImageField(upload_to='beneficios/', blank=True)
    terminos_condiciones = models.TextField(blank=True)
    vigencia_inicio = models.DateField(null=True, blank=True)
    vigencia_fin = models.DateField(null=True, blank=True)
    disponible = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_beneficio'
        verbose_name = 'Tipo de Beneficio'
        verbose_name_plural = 'Tipos de Beneficio'
    
    def __str__(self):
        return self.nombre


class CanjeoBeneficio(models.Model):
    """Canjes de beneficios por parte de empleados"""
    ESTADOS = [
        ('solicitado', 'Solicitado'),
        ('aprobado', 'Aprobado'),
        ('entregado', 'Entregado'),
        ('rechazado', 'Rechazado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)
    tipo_beneficio = models.ForeignKey(TipoBeneficio, on_delete=models.CASCADE)
    codigo_canje = models.CharField(max_length=20, unique=True)
    puntos_utilizados = models.IntegerField()
    fecha_canje = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='solicitado')
    observaciones = models.TextField(blank=True)
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'canjeos_beneficio'
        verbose_name = 'Canjeo de Beneficio'
        verbose_name_plural = 'Canjeos de Beneficio'