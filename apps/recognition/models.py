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
    
    def esta_disponible(self):
        """Verifica si el beneficio está disponible para canje"""
        from django.utils import timezone
        hoy = timezone.now().date()
        
        # Verificar disponibilidad general
        if not self.disponible:
            return False
        
        # Verificar vigencia
        if self.vigencia_inicio and hoy < self.vigencia_inicio:
            return False
        if self.vigencia_fin and hoy > self.vigencia_fin:
            return False
        
        # Verificar stock (si aplica)
        if self.stock_actual is not None and self.stock_actual <= 0:
            return False
        
        return True
    
    def tiene_stock_suficiente(self, cantidad=1):
        """Verifica si hay stock suficiente"""
        if self.stock_actual is None:
            return True  # Sin límite de stock
        return self.stock_actual >= cantidad


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
    fecha_reclamo_programada = models.DateField(null=True, blank=True)  # Fecha para reclamar
    fecha_entrega = models.DateTimeField(null=True, blank=True)  # Fecha real de entrega
    estado = models.CharField(max_length=20, choices=ESTADOS, default='solicitado')
    observaciones = models.TextField(blank=True)
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'canjeos_beneficio'
        verbose_name = 'Canjeo de Beneficio'
        verbose_name_plural = 'Canjeos de Beneficio'
    
    def get_estado_descripcion(self):
        """Descripción detallada del estado"""
        if self.estado == 'solicitado':
            return "Esperando aprobación del administrador"
        elif self.estado == 'aprobado':
            if self.fecha_reclamo_programada:
                return f"Aprobado - Puede reclamar a partir del {self.fecha_reclamo_programada.strftime('%d/%m/%Y')}"
            else:
                return "Aprobado - Puede reclamar cuando guste"
        elif self.estado == 'entregado':
            return f"Entregado el {self.fecha_entrega.strftime('%d/%m/%Y')}"
        elif self.estado == 'rechazado':
            return "Solicitud rechazada"
        return self.get_estado_display()
    
    def get_instrucciones_beneficio(self):
        """Instrucciones para el empleado según el estado"""
        if self.estado == 'aprobado':
            instrucciones = []
            if self.fecha_reclamo_programada:
                instrucciones.append(f"📅 Fecha disponible: {self.fecha_reclamo_programada.strftime('%d/%m/%Y')}")
            if self.observaciones:
                instrucciones.append(f"📝 Instrucciones: {self.observaciones}")
            instrucciones.append("🏢 Presenta tu código de canje en recursos humanos")
            return instrucciones
        return []
    
    def get_estado_color(self):
        """Color CSS para el estado"""
        colors = {
            'solicitado': 'warning',
            'aprobado': 'success', 
            'entregado': 'primary',
            'rechazado': 'danger'
        }
        return colors.get(self.estado, 'secondary')
    
    def save(self, *args, **kwargs):
        """Generar código de canje único"""
        if not self.codigo_canje:
            import random
            import string
            self.codigo_canje = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)
    
    def get_estado_color(self):
        """Color para badges según estado"""
        colores = {
            'solicitado': 'warning',
            'aprobado': 'success',
            'entregado': 'primary',
            'rechazado': 'danger',
        }
        return colores.get(self.estado, 'secondary')
    
    def get_estado_icono(self):
        """Icono para cada estado"""
        iconos = {
            'solicitado': 'fas fa-clock',
            'aprobado': 'fas fa-check',
            'entregado': 'fas fa-gift',
            'rechazado': 'fas fa-times',
        }
        return iconos.get(self.estado, 'fas fa-question')
    
    def get_estado_descripcion(self):
        """Descripción detallada del estado para el empleado"""
        descripciones = {
            'solicitado': 'Tu solicitud está siendo revisada por el administrador. Los puntos están reservados temporalmente.',
            'aprobado': 'Tu beneficio ha sido aprobado. Sigue las instrucciones para hacer efectivo tu beneficio.',
            'entregado': '¡Beneficio entregado! Esperamos que disfrutes tu recompensa.',
            'rechazado': 'Tu solicitud fue rechazada. Los puntos han sido devueltos a tu cuenta.',
        }
        return descripciones.get(self.estado, 'Estado desconocido')
    
    def get_instrucciones_beneficio(self):
        """Instrucciones específicas según el estado"""
        if self.estado == 'aprobado':
            if 'almuerzo' in self.tipo_beneficio.nombre.lower() or 'descuento' in self.tipo_beneficio.nombre.lower():
                return f"Presenta el código {self.codigo_canje} en el restaurante para aplicar tu descuento."
            elif 'día libre' in self.tipo_beneficio.nombre.lower():
                return f"Contacta a Recursos Humanos con el código {self.codigo_canje} para coordinar tu día libre."
            elif 'curso' in self.tipo_beneficio.nombre.lower():
                return f"Se te enviará un email con el enlace de acceso al curso. Código: {self.codigo_canje}"
            elif 'parking' in self.tipo_beneficio.nombre.lower():
                return f"Tu acceso VIP al parking ya está activado. Código: {self.codigo_canje}"
            else:
                return f"Contacta al administrador con el código {self.codigo_canje} para coordinar la entrega."
        elif self.estado == 'entregado':
            return "¡Beneficio entregado exitosamente!"
        elif self.estado == 'solicitado':
            return "Esperando aprobación del administrador."
        else:
            return ""