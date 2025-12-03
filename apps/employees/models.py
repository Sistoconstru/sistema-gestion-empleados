from django.db import models

# =============================================================================
# apps/employees/models.py
# =============================================================================

import uuid
from django.db import models
from apps.core.models import BaseModel as CoreBaseModel

# ===================== MODELO BASE PARA AUDITORÍA =====================

class BaseModel(models.Model):
    """Modelo base con campos de auditoría estándar"""
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora de creación del registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, help_text="Fecha y hora de última actualización")
    creado_por = models.ForeignKey(
        'authentication.Usuario', 
        on_delete=models.CASCADE, 
        related_name='%(class)s_creados',
        help_text="Usuario que creó el registro"
    )
    
    class Meta:
        abstract = True

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

class Empleado(BaseModel):
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
    fecha_nacimiento = models.DateField(null=True, blank=True)  # Fecha de nacimiento
    ciudad_nacimiento = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, blank=True)  # Ciudad de nacimiento
    escolaridad = models.ForeignKey(Escolaridad, on_delete=models.SET_NULL, null=True, blank=True)  # Escolaridad
    contacto_emergencia_nombre = models.CharField(max_length=100, blank=True)  # Nombre contacto emergencia
    contacto_emergencia_telefono = models.CharField(max_length=15, blank=False)  # Teléfono contacto emergencia
    correo_electronico = models.EmailField(blank=True)  # Email
    direccion = models.CharField(max_length=200, blank=False, help_text="Dirección de residencia (debe iniciar con el tipo de vía completo)")  # Dirección de residencia
    # Campos de auditoría heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        indexes = [
            # Removemos numero_documento porque ya tiene unique=True (índice automático)
            models.Index(fields=['estado']),
            models.Index(fields=['sede']),
            models.Index(fields=['fecha_ingreso']),  # Índice útil para consultas de antigüedad
            models.Index(fields=['estado', 'sede']),  # Índice compuesto para filtros combinados
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
            return self.historialcargo_set.filter(activo=True).first()
        except (AttributeError, TypeError, ValueError) as e:
            # Log específico del error para debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error obteniendo cargo actual para empleado {self.id}: {e}")
            return None
    
    @property
    def nombre_cargo_actual(self):
        """Retorna el nombre del cargo actual del empleado"""
        try:
            historial = self.historialcargo_set.filter(activo=True).first()
            if historial:
                return historial.cargo.nombre
            return None
        except (AttributeError, TypeError, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error obteniendo nombre cargo actual para empleado {self.id}: {e}")
            return None
    
    @property
    def area_actual(self):
        """Retorna el área actual del empleado basada en su cargo"""
        try:
            historial = self.historialcargo_set.filter(activo=True).first()
            if historial:
                return historial.cargo.area
            return None
        except (AttributeError, TypeError, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error obteniendo área actual para empleado {self.id}: {e}")
            return None

class HistorialCargo(BaseModel):
    """Historial de cargos de empleados"""
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)  # Empleado asociado
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)  # Cargo asociado
    fecha_inicio = models.DateField()  # Fecha de inicio en el cargo
    fecha_fin = models.DateField(null=True, blank=True)  # Fecha de fin en el cargo
    salario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Salario en el cargo
    # activo heredado de BaseModel: Si el cargo está activo
    activo = models.BooleanField(default=True)  # Si el cargo está activo - agregado explícitamente
    motivo_cambio = models.CharField(max_length=200, blank=True)  # Motivo del cambio de cargo
    observaciones = models.TextField(blank=True)  # Observaciones adicionales
    # Jefe directo: empleado que ocupa el cargo_jefe del cargo asignado
    jefe_directo = models.ForeignKey(
        'employees.Empleado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinados',
        help_text="Jefe directo del empleado (empleado que ocupa el cargo jefe)"
    )
    # Campos de auditoría heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por
    
    class Meta:
        db_table = 'historial_cargos'
        verbose_name = 'Historial de Cargo'
        verbose_name_plural = 'Historiales de Cargo'
    
    def clean(self):
        """Validación personalizada para asegurar un solo cargo activo por empleado"""
        from django.core.exceptions import ValidationError
        
        if self.activo:
            # Buscar otros cargos activos para el mismo empleado
            historial_activo = HistorialCargo.objects.filter(
                empleado=self.empleado, 
                activo=True
            ).exclude(pk=self.pk if self.pk else None)
            
            if historial_activo.exists():
                raise ValidationError('El empleado ya tiene un cargo activo. Desactive el cargo actual antes de asignar uno nuevo.')
    
    def save(self, *args, **kwargs):
        """Override save para manejar transiciones de cargo automáticamente"""
        if self.activo:
            # Desactivar otros cargos activos del mismo empleado
            HistorialCargo.objects.filter(
                empleado=self.empleado, 
                activo=True
            ).exclude(pk=self.pk if self.pk else None).update(
                activo=False,
                fecha_fin=self.fecha_inicio
            )
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.empleado.nombre_completo} - {self.cargo} ({estado})"


# ===================== MARKETPLACE - PRODUCTOS =====================

class Categoria(models.Model):
    """Categorías de productos del marketplace"""
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre de la categoría")
    descripcion = models.TextField(blank=True, help_text="Descripción detallada")
    icono = models.CharField(max_length=50, blank=True, help_text="Clase de icono (Font Awesome)")
    activa = models.BooleanField(default=True, help_text="Si la categoría está activa")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(BaseModel):
    """Productos disponibles en el marketplace"""
    TIPO_CHOICES = [
        ('venta', 'Venta Normal'),
        ('regalo', 'Regalo'),
        ('subasta', 'Subasta'),
    ]

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('vendido', 'Vendido'),
        ('cancelado', 'Cancelado'),
        ('archivado', 'Archivado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendedor = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='productos_creados',
        help_text="Empleado que ofrece el producto"
    )
    titulo = models.CharField(max_length=200, help_text="Título del producto")
    descripcion = models.TextField(help_text="Descripción detallada del producto")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Categoría del producto"
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='venta',
        help_text="Tipo de oferta"
    )
    precio_inicial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precio inicial para venta o valor base para subasta"
    )
    imagen = models.ImageField(
        upload_to='marketplace/productos/',
        null=True,
        blank=True,
        help_text="Imagen principal del producto"
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='activo',
        help_text="Estado actual del producto"
    )
    visible_para = models.ManyToManyField(
        Empleado,
        blank=True,
        related_name='productos_visibles',
        help_text="Empleados que pueden ver este producto (vacío = todos)"
    )
    cantidad_disponible = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Cantidad disponible del producto (NULL = sin límite)"
    )
    # Campos heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'marketplace_productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['vendedor', 'estado']),
            models.Index(fields=['categoria', 'estado']),
            models.Index(fields=['tipo', 'estado']),
            models.Index(fields=['fecha_creacion']),
        ]
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} (${self.precio_inicial})" if self.precio_inicial else self.titulo

    def get_cantidad_reservada(self):
        """Obtiene la cantidad de productos reservados"""
        return self.reservas.filter(estado='activa').count()

    def tiene_disponible(self):
        """Verifica si hay cantidad disponible para reservar"""
        if self.cantidad_disponible is None:
            return True  # Sin límite
        return self.get_cantidad_reservada() < self.cantidad_disponible

    def get_disponible_texto(self):
        """Retorna texto de disponibilidad"""
        if self.cantidad_disponible is None:
            return "Sin límite"
        reservadas = self.get_cantidad_reservada()
        disponible = self.cantidad_disponible - reservadas
        return f"{disponible} de {self.cantidad_disponible}"


class Reserva(BaseModel):
    """Reservas/separaciones de productos por comprador"""
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('confirmada', 'Confirmada (Venta)'),
        ('cancelada', 'Cancelada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='reservas',
        help_text="Producto reservado"
    )
    comprador = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='reservas_como_comprador',
        help_text="Empleado que hizo la reserva"
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='activa',
        help_text="Estado de la reserva"
    )
    venta_asociada = models.OneToOneField(
        'Venta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reserva_origen',
        help_text="Venta originada de esta reserva"
    )
    # Campos heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'marketplace_reservas'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        indexes = [
            models.Index(fields=['producto', 'estado']),
            models.Index(fields=['comprador', 'estado']),
            models.Index(fields=['fecha_creacion']),
        ]
        ordering = ['-fecha_creacion']
        unique_together = [['producto', 'comprador', 'estado']]  # Un usuario no puede tener 2 reservas activas del mismo producto

    def __str__(self):
        return f"Reserva: {self.producto.titulo} - {self.comprador}"


class Venta(BaseModel):
    """Transacciones de venta normal entre empleados"""
    ESTADO_CHOICES = [
        ('pendiente_vendedor', 'Pendiente aceptación vendedor'),
        ('pendiente_comprador', 'Pendiente confirmación comprador'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='ventas'
    )
    vendedor = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='ventas_como_vendedor'
    )
    comprador = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='compras'
    )
    precio_final = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Precio final acordado"
    )
    estado = models.CharField(
        max_length=25,
        choices=ESTADO_CHOICES,
        default='pendiente_vendedor'
    )
    observaciones = models.TextField(blank=True, help_text="Notas sobre la venta")
    calificacion_vendedor = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Calificación del vendedor (1-5 estrellas)"
    )
    calificacion_comprador = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Calificación del comprador (1-5 estrellas)"
    )
    comentario_vendedor = models.TextField(blank=True, help_text="Comentario sobre el comprador")
    comentario_comprador = models.TextField(blank=True, help_text="Comentario sobre el vendedor")
    fecha_venta = models.DateTimeField(auto_now_add=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    # Campos heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'marketplace_ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        indexes = [
            models.Index(fields=['vendedor', 'estado']),
            models.Index(fields=['comprador', 'estado']),
            models.Index(fields=['fecha_venta']),
        ]
        ordering = ['-fecha_venta']

    def __str__(self):
        return f"{self.producto.titulo} - {self.vendedor} → {self.comprador}"


class Subasta(BaseModel):
    """Subastas de productos entre empleados"""
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='subastas'
    )
    vendedor = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='subastas_creadas'
    )
    precio_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    precio_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Precio de la puja más alta"
    )
    pujador_actual = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subastas_pujadas'
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='activa'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(help_text="Fecha y hora de finalización de la subasta")
    incremento_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1000,
        help_text="Incremento mínimo para nueva puja"
    )
    ganador = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subastas_ganadas'
    )
    # Campos heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'marketplace_subastas'
        verbose_name = 'Subasta'
        verbose_name_plural = 'Subastas'
        indexes = [
            models.Index(fields=['vendedor', 'estado']),
            models.Index(fields=['estado', 'fecha_fin']),
            models.Index(fields=['pujador_actual']),
        ]
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Subasta: {self.producto.titulo} ({self.estado})"


class PujaSubasta(BaseModel):
    """Historial de pujas en subastas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subasta = models.ForeignKey(
        Subasta,
        on_delete=models.CASCADE,
        related_name='pujas'
    )
    pujador = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='mis_pujas'
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    es_puja_automatica = models.BooleanField(
        default=False,
        help_text="Si es una puja automática del sistema"
    )
    monto_maximo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monto máximo permitido para pujas automáticas"
    )
    # Campos heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'marketplace_pujas'
        verbose_name = 'Puja'
        verbose_name_plural = 'Pujas'
        indexes = [
            models.Index(fields=['subasta', 'fecha_creacion']),
            models.Index(fields=['pujador']),
        ]
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Puja de {self.pujador.nombre_completo}: ${self.monto}"


class Regalo(BaseModel):
    """Regalos entre empleados"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente aceptación'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='regalos'
    )
    donante = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='regalos_dados'
    )
    receptor = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='regalos_recibidos'
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    mensaje = models.TextField(blank=True, help_text="Mensaje del donante")
    fecha_ofrecimiento = models.DateTimeField(auto_now_add=True)
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)
    # Campos heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'marketplace_regalos'
        verbose_name = 'Regalo'
        verbose_name_plural = 'Regalos'
        indexes = [
            models.Index(fields=['receptor', 'estado']),
            models.Index(fields=['donante']),
        ]
        ordering = ['-fecha_ofrecimiento']

    def __str__(self):
        return f"{self.donante.nombre_completo} → {self.receptor.nombre_completo}: {self.producto.titulo}"


# ===================== MESSAGING - CONVERSACIONES =====================

class Conversacion(BaseModel):
    """Conversaciones/chats entre empleados"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participantes = models.ManyToManyField(
        Empleado,
        related_name='conversaciones'
    )
    titulo = models.CharField(
        max_length=200,
        blank=True,
        help_text="Título opcional de la conversación"
    )
    contexto = models.CharField(
        max_length=20,
        choices=[
            ('venta', 'Venta'),
            ('subasta', 'Subasta'),
            ('regalo', 'Regalo'),
            ('general', 'General'),
        ],
        default='general',
        help_text="Contexto de la conversación"
    )
    producto_referencia = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversaciones'
    )
    archivada = models.BooleanField(default=False)
    fecha_ultima_actividad = models.DateTimeField(auto_now=True)
    # Campos heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'messaging_conversaciones'
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        indexes = [
            models.Index(fields=['fecha_ultima_actividad']),
        ]
        ordering = ['-fecha_ultima_actividad']

    def __str__(self):
        participantes_str = ', '.join([p.nombre_completo for p in self.participantes.all()[:2]])
        return f"Chat: {participantes_str}"


class Mensaje(BaseModel):
    """Mensajes individuales en conversaciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    remitente = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados'
    )
    contenido = models.TextField(help_text="Contenido del mensaje")
    archivos_adjuntos = models.FileField(
        upload_to='messaging/archivos/',
        null=True,
        blank=True,
        help_text="Archivo adjunto (opcional)"
    )
    leido = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    # Campos heredados de BaseModel: fecha_creacion, fecha_actualizacion, creado_por

    class Meta:
        db_table = 'messaging_mensajes'
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        indexes = [
            models.Index(fields=['conversacion', 'fecha_creacion']),
            models.Index(fields=['remitente']),
            models.Index(fields=['leido']),
        ]
        ordering = ['fecha_creacion']

    def __str__(self):
        preview = self.contenido[:50] + '...' if len(self.contenido) > 50 else self.contenido
        return f"{self.remitente.nombre_completo}: {preview}"


class LecturaConversacion(models.Model):
    """Rastreo del último mensaje leído por cada participante"""
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='lecturas'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='mis_lecturas'
    )
    ultimo_mensaje_leido = models.ForeignKey(
        Mensaje,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messaging_lecturas'
        unique_together = ['conversacion', 'empleado']
        verbose_name = 'Lectura de Conversación'
        verbose_name_plural = 'Lecturas de Conversaciones'

    def __str__(self):
        return f"{self.empleado.nombre_completo} en {self.conversacion}"


# ===================== FEED/PUBLICACIONES (MINIFACEBOOK) =====================

class Publicacion(models.Model):
    """Publicaciones en el feed del marketplace (minifacebook)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    autor = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='mis_publicaciones'
    )
    titulo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Título opcional de la publicación"
    )
    contenido = models.TextField(
        help_text="Contenido principal de la publicación"
    )
    imagen = models.ImageField(
        upload_to='publicaciones/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Imagen de fondo opcional (máx 5MB)"
    )

    # Flags de tipo de publicación
    es_anuncio = models.BooleanField(
        default=False,
        help_text="¿Es un anuncio (solo admins pueden crear)?"
    )
    es_importante = models.BooleanField(
        default=False,
        help_text="¿Es un anuncio importante? (solo si es_anuncio=True)"
    )

    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_eliminacion_automatica = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha cuando se eliminará automáticamente (15 días para publicaciones normales)"
    )

    # Solo para anuncios importantes
    fecha_fin = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha de finalización del anuncio importante"
    )

    # Estilos (JSON) - Nuevo formato mejorado
    estilos = models.JSONField(
        default=dict,
        blank=True,
        help_text="Estilos: font_family, font_size, text_color, stroke_width, stroke_color, "
                  "titulo_x, titulo_y, titulo_width, titulo_height, "
                  "contenido_x, contenido_y, contenido_width, contenido_height"
    )

    # Imagen renderizada (con texto superpuesto)
    imagen_renderizada = models.ImageField(
        upload_to='anuncios_renderizados/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Imagen final con texto renderizado"
    )

    class Meta:
        db_table = 'feed_publicaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['-fecha_creacion']),
            models.Index(fields=['es_anuncio', '-fecha_creacion']),
            models.Index(fields=['es_importante', '-fecha_creacion']),
            models.Index(fields=['fecha_fin']),
        ]
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'

    def __str__(self):
        titulo = self.titulo or self.contenido[:50]
        tipo = "Anuncio" if self.es_anuncio else "Publicación"
        return f"{tipo}: {titulo} - {self.autor.nombre_completo}"

    @property
    def esta_activa(self):
        """Verifica si la publicación está activa"""
        from django.utils import timezone
        if self.es_anuncio and self.es_importante and self.fecha_fin:
            return timezone.now() < self.fecha_fin
        return True

    @property
    def es_del_autor(self, user):
        """Verifica si el usuario es el autor"""
        return user.empleado == self.autor


class Comentario(models.Model):
    """Comentarios en las publicaciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    autor = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='mis_comentarios'
    )
    contenido = models.TextField(
        help_text="Contenido del comentario"
    )

    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feed_comentarios'
        ordering = ['fecha_creacion']
        indexes = [
            models.Index(fields=['publicacion', 'fecha_creacion']),
        ]
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f"Comentario de {self.autor.nombre_completo} en {self.publicacion}"

