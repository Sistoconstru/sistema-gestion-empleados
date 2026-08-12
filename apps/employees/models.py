from django.db import models

# =============================================================================
# apps/employees/models.py
# =============================================================================

import uuid
from django.db import models
from apps.core.models import BaseModel as CoreBaseModel
from custom_storage.media import MediaStorage

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
    centro_costo = models.ForeignKey(
        'organizational.CentroCosto',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='empleados',
        help_text="Centro de costo al que pertenece el empleado"
    )
    estado = models.ForeignKey(EstadoEmpleado, on_delete=models.CASCADE)  # Estado actual
    fecha_nacimiento = models.DateField(null=True, blank=True)  # Fecha de nacimiento
    ciudad_nacimiento = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, blank=True)  # Ciudad de nacimiento
    escolaridad = models.ForeignKey(Escolaridad, on_delete=models.SET_NULL, null=True, blank=True)  # Escolaridad
    contacto_emergencia_nombre = models.CharField(max_length=100, blank=True)  # Nombre contacto emergencia
    contacto_emergencia_telefono = models.CharField(max_length=15, blank=False)  # Teléfono contacto emergencia
    correo_electronico = models.EmailField(blank=True)  # Email
    direccion = models.CharField(max_length=200, blank=False, help_text="Dirección de residencia (debe iniciar con el tipo de vía completo)")  # Dirección de residencia

    ESTADO_CIVIL_CHOICES = [
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('union_libre', 'Unión Libre'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a'),
    ]
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True)

    SEXO_BIOLOGICO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    sexo_biologico = models.CharField(
        max_length=1, choices=SEXO_BIOLOGICO_CHOICES, blank=True,
        verbose_name='Sexo biológico',
        help_text='Sirve para reportes legales (PILA/DIAN) y segmentación (madres/padres).',
    )

    # Polla Mundial 2026 - Aceptación de términos
    acepto_terminos_polla_mundial = models.BooleanField(default=False, help_text="¿Aceptó términos y condiciones de la Polla Mundial?")
    fecha_aceptacion_terminos_polla = models.DateTimeField(null=True, blank=True, help_text="Fecha de aceptación de términos de Polla Mundial")

    # Encargado de asistencia: subalterno directo que puede registrar la
    # asistencia del equipo del jefe cuando el jefe esté ausente ese día.
    # Se activa automáticamente al detectar registro de ausencia del jefe hoy.
    encargado_asistencia = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reemplaza_a',
        help_text="Subalterno directo autorizado para registrar el equipo cuando este jefe esté ausente",
    )

    # Saldo de vacaciones (calculado y devuelto por Odoo, consultado bajo demanda).
    # SIGHU NO calcula saldo — solo muestra el valor autoritativo de Odoo.
    # El saldo es al ÚLTIMO CORTE MENSUAL (fin de mes anterior), no en vivo.
    saldo_vacaciones_dias = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text="Días de vacaciones disponibles al último corte según Odoo.",
    )
    saldo_vacaciones_fecha_corte = models.DateField(
        null=True, blank=True,
        help_text="Fecha del corte al que corresponde el saldo (típicamente último día del mes anterior).",
    )
    saldo_vacaciones_actualizado = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha/hora en que SIGHU consultó el saldo por última vez.",
    )

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
            historial = self.historialcargo_set.filter(activo=True).select_related('cargo', 'cargo__area').first()
            if historial and historial.cargo:
                return historial.cargo.area if hasattr(historial.cargo, 'area') else None
            return None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error obteniendo área actual para empleado {self.id}: {e}")
            return None

    @property
    def es_padre(self):
        """True si el empleado tiene al menos un hijo registrado (sin importar el flag activo).

        Se ignora `activo` a propósito: ser padre es un hecho de la persona, no de
        la vigencia del registro (los hijos pueden ser adultos, vivir fuera, etc.).
        """
        return self.familiares.filter(tipo='hijo').exists()


class Familiar(BaseModel):
    """Datos de familiares del empleado (pareja, hijos, otros).

    Un solo modelo polimórfico vía `tipo` para que sea extensible. Validación:
    solo puede haber una pareja activa por empleado a la vez.
    """
    TIPO_CHOICES = [
        ('pareja', 'Pareja'),
        ('hijo', 'Hijo/a'),
        ('padre', 'Padre/Madre'),
        ('hermano', 'Hermano/a'),
        ('otro', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='familiares')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.SET_NULL, null=True, blank=True)
    numero_documento = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    parentesco = models.CharField(max_length=50, blank=True, help_text="Detalle del parentesco si tipo='otro'")

    # Aplican principalmente a pareja, opcionales para el resto
    convive = models.BooleanField(default=False, help_text="Convive con el empleado")
    dependiente_economico = models.BooleanField(default=False, help_text="Dependiente económico del empleado")
    eps = models.CharField(max_length=100, blank=True, help_text="EPS a la que está afiliado")

    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True, help_text="Si el registro está vigente")

    class Meta:
        db_table = 'familiares'
        verbose_name = 'Familiar'
        verbose_name_plural = 'Familiares'
        ordering = ['tipo', 'fecha_nacimiento']
        indexes = [
            models.Index(fields=['empleado', 'tipo']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nombre_completo} (de {self.empleado.nombre_completo})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        from datetime import date
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def clean(self):
        """Solo puede existir una pareja activa por empleado."""
        from django.core.exceptions import ValidationError
        if not self.empleado_id:
            # ModelForm._post_clean dispara este clean() antes de que la vista
            # asigne empleado. Difiere la validación: se re-ejecutará en full_clean()
            # justo antes de save().
            return
        if self.tipo == 'pareja' and self.activo:
            qs = Familiar.objects.filter(
                empleado_id=self.empleado_id, tipo='pareja', activo=True
            ).exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    "Este empleado ya tiene una pareja registrada como activa. "
                    "Desactiva la actual antes de registrar otra."
                )


def _documento_familiar_upload_path(instance, filename):
    """Ruta de almacenamiento siguiendo el patrón del proyecto.

    Estructura: familiares/<numero_documento_empleado>/<tipo>_<nombre_slug_familiar>/<filename_safe>

    Misma convención que DocumentoEmpleado (documentos/<numero_doc>/<tipo>/...)
    y certificados de capacitación (capacitaciones/certificados/<numero_doc>/...).
    Permite ubicar fácilmente todos los archivos de un empleado en S3 por su
    cédula.

    El filename se slugifica y se acota a 80 chars + extensión (hasta 10),
    para evitar errores 400 por nombres largos o caracteres especiales.
    """
    import os
    from django.utils.text import slugify

    empleado_doc = instance.familiar.empleado.numero_documento
    tipo_familiar = instance.familiar.tipo  # 'pareja', 'hijo', 'padre', etc.
    nombre_familiar_slug = slugify(instance.familiar.nombre_completo)[:50] or 'sin-nombre'
    subcarpeta_familiar = f"{tipo_familiar}_{nombre_familiar_slug}"

    base, ext = os.path.splitext(filename or '')
    ext = (ext or '').lower()[:10]
    base_safe = slugify(base)[:80] or 'documento'

    return f"familiares/{empleado_doc}/{subcarpeta_familiar}/{base_safe}{ext}"


class DocumentoFamiliar(models.Model):
    """Documentos adjuntos por familiar (registro civil, TI, certificados, etc.)."""

    TIPO_CHOICES = [
        ('registro_civil', 'Registro Civil'),
        ('tarjeta_identidad', 'Tarjeta de Identidad'),
        ('cedula', 'Cédula de Ciudadanía'),
        ('certificado_estudio', 'Certificado de Estudio'),
        ('certificado_eps', 'Certificado EPS'),
        ('otro', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    familiar = models.ForeignKey(Familiar, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Clase de documento')
    descripcion = models.CharField(max_length=200, blank=True)
    # storage=MediaStorage() explícito porque DEFAULT_FILE_STORAGE en Django 5
    # con STORAGES nuevo puede no resolver al backend S3 esperado. Mismo patrón
    # que DocumentoEmpleado.archivo en apps/documents/models.py.
    archivo = models.FileField(
        upload_to=_documento_familiar_upload_path,
        max_length=500,
        storage=MediaStorage(),
    )
    fecha_vencimiento = models.DateField(null=True, blank=True, help_text="Si aplica (ej: certificado de estudio)")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documentos_familiar'
        verbose_name = 'Documento de Familiar'
        verbose_name_plural = 'Documentos de Familiares'
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.familiar.nombre_completo}"

    @property
    def filename(self):
        """Nombre del archivo (sin path) para mostrar y para el atributo download."""
        if not self.archivo:
            return ''
        import os
        return os.path.basename(self.archivo.name)


class SolicitudVacacion(BaseModel):
    """Solicitud de vacaciones aprobada por el jefe directo y enviada a Odoo.

    SIGHU NO valida saldo ni calcula días hábiles — eso lo hace Odoo. SIGHU solo
    registra la solicitud, dispara el webhook y guarda el `leave_id_odoo` que
    devuelve Odoo para trazabilidad. Ver docs/INTEGRACION_ODOO_VACACIONES.md.
    """
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('enviada_pendiente_rrhh', 'Enviada — Pendiente RRHH'),
        ('rechazada_odoo', 'Rechazada por Odoo (saldo/reglas)'),
        ('error_envio', 'Error de envío'),
        # Callbacks de Odoo cuando RRHH actúa sobre la solicitud
        ('aprobada_rrhh', 'Aprobada por RRHH'),
        ('rechazada_rrhh', 'Rechazada por RRHH'),
        ('cancelada_rrhh', 'Cancelada por RRHH'),
    ]

    TIPO_CHOICES = [
        ('tiempo', 'Tiempo (días libres)'),
        ('pago_dinero', 'Pagada en dinero'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey(
        Empleado, on_delete=models.CASCADE, related_name='solicitudes_vacacion',
        help_text="Empleado a quien le aplica la vacación",
    )
    jefe_solicitante = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vacaciones_solicitadas',
        help_text="Jefe (o staff/RRHH) que solicitó la vacación",
    )
    # Fechas nullables: las compensaciones en dinero no tienen rango de ausencia.
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default='tiempo',
        help_text="Tipo de vacación: tiempo (días libres) o pago en dinero",
    )
    estado_local = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='borrador')
    leave_id_odoo = models.IntegerField(
        null=True, blank=True,
        help_text="ID de hr.leave devuelto por Odoo (solo aplica cuando tipo=tiempo)",
    )
    compensacion_id_odoo = models.IntegerField(
        null=True, blank=True, unique=True,
        help_text="ID de la compensación en Odoo (solo aplica cuando tipo=pago_dinero). "
                  "Clave de upsert para compensaciones — no colisiona con leave_id.",
    )
    valor_compensacion = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Valor pagado al empleado en pesos (solo tipo=pago_dinero).",
    )
    fecha_lote_nomina = models.DateField(
        null=True, blank=True,
        help_text="Fecha del lote de nómina en que se aplicó la compensación (solo tipo=pago_dinero).",
    )
    dias_compensados = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text="Días compensados en dinero (informativo, solo tipo=pago_dinero). "
                  "Puede tener decimales (ej: 7.5).",
    )
    motivo_rechazo = models.TextField(blank=True)
    fecha_envio_odoo = models.DateTimeField(null=True, blank=True)
    respuesta_odoo = models.JSONField(null=True, blank=True, help_text="Respuesta cruda de Odoo (auditoría)")

    # Constancia de descarga de la carta (declaración del empleado de estar al
    # tanto de sus vacaciones aprobadas). Se registra la primera descarga con
    # su hash de confirmación; descargas posteriores no sobreescriben.
    carta_descargada_fecha = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha/hora en que el empleado descargó la carta con consentimiento.",
    )
    carta_confirmada_hash = models.CharField(
        max_length=64, blank=True,
        help_text="Hash SHA-256 del consentimiento (empleado_id + solicitud_id + fecha).",
    )

    class Meta:
        db_table = 'solicitudes_vacacion'
        verbose_name = 'Solicitud de Vacación'
        verbose_name_plural = 'Solicitudes de Vacación'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['empleado', '-fecha_creacion']),
            models.Index(fields=['estado_local']),
        ]

    def __str__(self):
        return f"Vacación {self.empleado.nombre_completo} {self.fecha_inicio} a {self.fecha_fin} ({self.get_estado_local_display()})"

    @property
    def dias_calendario(self):
        """Días calendario incluyendo extremos.

        Para tipo=tiempo, se calcula del rango de fechas.
        Para tipo=pago_dinero (compensaciones), retorna dias_compensados que envía Odoo.
        """
        if self.tipo == 'pago_dinero':
            return self.dias_compensados
        if not self.fecha_inicio or not self.fecha_fin:
            return None
        return (self.fecha_fin - self.fecha_inicio).days + 1

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha final no puede ser anterior a la inicial.")
        # tipo=tiempo requiere ambas fechas; tipo=pago_dinero no las requiere.
        if self.tipo == 'tiempo' and (not self.fecha_inicio or not self.fecha_fin):
            raise ValidationError("Las vacaciones en tiempo requieren fecha_inicio y fecha_fin.")


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
    # Fin de contrato de aprendizaje: solo aplica cuando el cargo es aprendiz
    # SENA. Si se deja vacío, el reporte SENA calcula 6 meses desde fecha_inicio
    # (contrato productivo típico). Se usa manual para aprendices profesionales
    # con contratos más cortos u otros casos particulares.
    fecha_fin_contrato_aprendizaje = models.DateField(
        null=True, blank=True,
        help_text="Solo para cargos de aprendiz SENA. Deja vacío para usar el default de 6 meses desde fecha_inicio.",
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

            # Asignar jefe_directo automáticamente si no está asignado manualmente
            # Solo si el cargo tiene un cargo_jefe definido
            if not self.jefe_directo and self.cargo.cargo_jefe:
                # Buscar empleados activos en el cargo_jefe
                empleados_en_cargo_jefe = HistorialCargo.objects.filter(
                    cargo=self.cargo.cargo_jefe,
                    activo=True
                ).select_related('empleado')

                # Si hay exactamente UN empleado en el cargo jefe, asignarlo
                if empleados_en_cargo_jefe.count() == 1:
                    self.jefe_directo = empleados_en_cargo_jefe.first().empleado
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(
                        f"Jefe directo asignado automáticamente: {self.empleado.nombre_completo} "
                        f"→ {self.jefe_directo.nombre_completo} "
                        f"(Cargo: {self.cargo.nombre} → {self.cargo.cargo_jefe.nombre})"
                    )
                elif empleados_en_cargo_jefe.count() > 1:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"No se asignó jefe directo automáticamente para {self.empleado.nombre_completo}: "
                        f"Hay {empleados_en_cargo_jefe.count()} empleados en el cargo jefe '{self.cargo.cargo_jefe.nombre}'"
                    )

        super().save(*args, **kwargs)
    
    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.empleado.nombre_completo} - {self.cargo} ({estado})"


# ===================== ASISTENCIA DIARIA =====================

class AsistenciaDiaria(BaseModel):
    """Registro diario de asistencia del empleado, capturado por su jefe directo.

    Un registro por (empleado, fecha). El jefe abre el tablero, todos aparecen
    como 'presente' por defecto, y solo interactúa con las excepciones. Las
    ausencias por vacaciones/incapacidad se autodetectan del resto del sistema.

    Jornada estándar Construinmuniza: L-V, 7:00 AM a 4:24 PM con 1h de descanso
    (20+40 min). Los sábados/domingos/festivos NO se registran.
    """
    ESTADO_CHOICES = [
        ('presente', 'Presente'),
        ('retardo', 'Retardo'),
        ('ausente', 'Ausente sin justificar'),
        ('permiso', 'Permiso remunerado'),
        ('permiso_no_remunerado', 'Permiso no remunerado'),
        ('incapacidad', 'Incapacidad'),
        ('en_vacaciones', 'En vacaciones'),
    ]
    # Estados que NO son un "presente pleno" — para reportes de ausentismo.
    ESTADOS_AUSENCIA = {
        'ausente', 'permiso', 'permiso_no_remunerado',
        'incapacidad', 'en_vacaciones',
    }
    # Estados autodetectados por el sistema — el jefe no los edita a mano.
    ESTADOS_AUTOMATICOS = {'en_vacaciones', 'incapacidad'}

    empleado = models.ForeignKey(
        Empleado, on_delete=models.CASCADE, related_name='asistencias',
        help_text="Empleado al que corresponde el registro",
    )
    fecha = models.DateField(help_text="Fecha del registro (solo días L-V)")
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='presente')
    motivo = models.TextField(
        blank=True,
        help_text="Motivo de la ausencia/permiso (obligatorio si estado != presente)",
    )
    registrado_por = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='asistencias_registradas',
        help_text="Jefe que registró la asistencia",
    )

    class Meta:
        db_table = 'asistencia_diaria'
        verbose_name = 'Registro de asistencia'
        verbose_name_plural = 'Registros de asistencia'
        constraints = [
            models.UniqueConstraint(
                fields=['empleado', 'fecha'],
                name='unique_asistencia_empleado_fecha',
            ),
        ]
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['empleado', '-fecha']),
            models.Index(fields=['estado']),
        ]
        ordering = ['-fecha', 'empleado__apellidos']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha} ({self.get_estado_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Solo días laborales L-V (lunes=0 ... viernes=4)
        if self.fecha and self.fecha.weekday() >= 5:
            raise ValidationError({'fecha': 'Solo se registran días de lunes a viernes.'})
        # Motivo obligatorio para ausencias
        if self.estado != 'presente' and not (self.motivo or '').strip():
            if self.estado not in self.ESTADOS_AUTOMATICOS:
                raise ValidationError({
                    'motivo': f'El motivo es obligatorio cuando el estado es {self.get_estado_display()}.',
                })

    @property
    def es_ausencia(self):
        return self.estado in self.ESTADOS_AUSENCIA


# ===================== NOVEDADES DE NÓMINA =====================

class NovedadNomina(BaseModel):
    """Novedades operativas del empleado (horas extras, recargos) que impactan
    la nómina.

    Reemplaza el formato manual 'FORMATO DE HORAS EXTRAS Y RECARGOS'. El jefe
    directo registra las novedades por empleado y por día desde una vista
    semanal (L-D). RRHH aprueba antes de que cuenten para nómina.
    """
    TIPO_CHOICES = [
        ('hora_extra_diurna', 'Hora extra diurna'),
        ('hora_extra_nocturna', 'Hora extra nocturna'),
        ('hora_extra_dominical', 'Hora extra dominical/festivo'),
        ('recargo_nocturno', 'Recargo nocturno'),
        ('recargo_dominical', 'Recargo dominical/festivo'),
        ('vigilancia', 'Vigilancia'),
    ]

    ESTADO_APROBACION_CHOICES = [
        ('pendiente', 'Pendiente de aprobación'),
        ('aprobada', 'Aprobada por RRHH'),
        ('rechazada', 'Rechazada por RRHH'),
    ]

    empleado = models.ForeignKey(
        Empleado, on_delete=models.CASCADE, related_name='novedades_nomina',
        help_text="Empleado al que corresponde la novedad",
    )
    fecha = models.DateField(help_text="Fecha en que ocurrió la novedad")
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES)

    hora_inicio = models.TimeField(
        null=True, blank=True,
        help_text="Hora de inicio (opcional si solo se registra total)",
    )
    hora_fin = models.TimeField(
        null=True, blank=True,
        help_text="Hora de fin (opcional si solo se registra total)",
    )
    total_horas = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Horas totales de la novedad (ej: 2.50 = 2h 30m)",
    )

    motivo = models.TextField(help_text="Motivo de la novedad (obligatorio)")
    observaciones = models.TextField(blank=True)

    registrado_por = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='novedades_registradas',
        help_text="Jefe que registró la novedad",
    )

    # Aprobación por RRHH
    estado_aprobacion = models.CharField(
        max_length=15, choices=ESTADO_APROBACION_CHOICES, default='pendiente',
    )
    aprobado_por_rrhh = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='novedades_aprobadas',
        help_text="Usuario RRHH que aprobó/rechazó",
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(blank=True)

    class Meta:
        db_table = 'novedades_nomina'
        verbose_name = 'Novedad de nómina'
        verbose_name_plural = 'Novedades de nómina'
        indexes = [
            models.Index(fields=['empleado', '-fecha']),
            models.Index(fields=['fecha']),
            models.Index(fields=['estado_aprobacion']),
        ]
        ordering = ['-fecha', 'empleado__apellidos']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha} - {self.get_tipo_display()} ({self.total_horas}h)"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not (self.motivo or '').strip():
            raise ValidationError({'motivo': 'El motivo es obligatorio.'})
        if self.total_horas is None or self.total_horas <= 0:
            raise ValidationError({'total_horas': 'El total de horas debe ser mayor a cero.'})
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            # Puede cruzar medianoche — no forzar, solo advertir en validación fuerte.
            pass


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
        storage=MediaStorage(),
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
        """Obtiene la cantidad total de unidades reservadas (suma de cantidad_solicitada)"""
        from django.db.models import Sum
        resultado = self.reservas.filter(estado='activa').aggregate(total=Sum('cantidad_solicitada'))
        return resultado['total'] or 0

    def get_cantidad_regalos_solicitados(self):
        """Obtiene la cantidad de regalos solicitados (pendientes o aceptados)"""
        if self.tipo == 'regalo':
            return self.regalos.filter(estado__in=['pendiente', 'aceptado']).count()
        return 0

    def tiene_disponible(self, cantidad_requerida=1):
        """Verifica si hay cantidad disponible para reservar o regalar"""
        if self.cantidad_disponible is None:
            return True  # Sin límite

        # Sumar unidades ya reservadas/solicitadas
        cantidad_usada = self.get_cantidad_reservada() + self.get_cantidad_regalos_solicitados()
        return (cantidad_usada + cantidad_requerida) <= self.cantidad_disponible

    def get_disponible_texto(self):
        """Retorna texto de disponibilidad"""
        if self.cantidad_disponible is None:
            return "Ilimitado"

        # Para regalos, contar solo los regalos. Para otros, sumar unidades reservadas
        if self.tipo == 'regalo':
            regalos_solicitados = self.get_cantidad_regalos_solicitados()
            disponible = self.cantidad_disponible - regalos_solicitados
        else:
            reservadas = self.get_cantidad_reservada()
            disponible = self.cantidad_disponible - reservadas

        return f"{max(disponible, 0)} de {self.cantidad_disponible}"

    def get_calificacion_promedio(self):
        """Calcula el promedio de calificaciones que ha recibido este producto/vendedor"""
        from django.db.models import Avg
        resultado = self.ventas.filter(
            estado='completada',
            calificacion_comprador__isnull=False
        ).aggregate(promedio=Avg('calificacion_comprador'))
        return round(resultado['promedio'], 1) if resultado['promedio'] else None

    def get_total_calificaciones(self):
        """Cuenta cuántas calificaciones ha recibido este producto/vendedor"""
        return self.ventas.filter(
            estado='completada',
            calificacion_comprador__isnull=False
        ).count()

    def get_calificaciones_recientes(self, limit=5):
        """Obtiene las calificaciones más recientes con comentarios"""
        return self.ventas.filter(
            estado='completada',
            calificacion_comprador__isnull=False
        ).select_related('comprador').order_by('-fecha_completada')[:limit]


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
    cantidad_solicitada = models.PositiveIntegerField(
        default=1,
        help_text="Cantidad de unidades solicitadas por el comprador"
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
    confirmado_por_donante = models.BooleanField(
        default=False,
        help_text="Si el donante confirmó la entrega del regalo"
    )
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
        storage=MediaStorage(),
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
    es_rapida = models.BooleanField(
        default=False,
        help_text="¿Es una publicación rápida? (sin editor completo, dura 6 meses)"
    )

    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_eliminacion_automatica = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha cuando se eliminará automáticamente (15 días para publicaciones normales)"
    )

    # Fechas de publicación (solo para anuncios importantes o publicaciones programadas)
    fecha_inicio = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha de inicio de la publicación (si es nula, se publica inmediatamente)"
    )
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
        storage=MediaStorage(),
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
        """Verifica si la publicación está activa (dentro del rango de fechas)"""
        from django.utils import timezone
        ahora = timezone.now()

        # Si tiene fecha_inicio, debe estar después o igual a ahora
        if self.fecha_inicio and ahora < self.fecha_inicio:
            return False

        # Si tiene fecha_fin, debe estar antes de ahora
        if self.fecha_fin and ahora >= self.fecha_fin:
            return False

        return True

    @property
    def esta_publicada(self):
        """Verifica si la publicación ya ha sido publicada (pasó fecha_inicio)"""
        from django.utils import timezone
        if self.fecha_inicio and timezone.now() < self.fecha_inicio:
            return False
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


# ===================== POLLA MUNDIALISTA 2026 =====================

class PartidoMundial(models.Model):
    """Partidos del Mundial 2026 - Módulo temporal para polla mundialista"""

    FASES = [
        ('grupos', 'Fase de Grupos'),
        ('dieciseisavos', 'Dieciseisavos de Final'),
        ('octavos', 'Octavos de Final'),
        ('cuartos', 'Cuartos de Final'),
        ('semifinal', 'Semifinal'),
        ('tercer_lugar', 'Tercer Lugar'),
        ('final', 'Final'),
    ]

    MULTIPLICADORES_PUNTOS = {
        'grupos': 1,
        'dieciseisavos': 1,  # Mismo multiplicador que fase de grupos
        'octavos': 2,
        'cuartos': 3,
        'semifinal': 4,
        'tercer_lugar': 4,
        'final': 5,
    }

    # Información del partido
    equipo_local = models.CharField(max_length=50, help_text="Nombre del equipo local")
    equipo_visitante = models.CharField(max_length=50, help_text="Nombre del equipo visitante")
    bandera_local = models.CharField(max_length=10, blank=True, help_text="Emoji de bandera del equipo local")
    bandera_visitante = models.CharField(max_length=10, blank=True, help_text="Emoji de bandera del equipo visitante")

    # Fecha y fase
    fecha_hora = models.DateTimeField(help_text="Fecha y hora del partido")
    fase = models.CharField(max_length=20, choices=FASES, default='grupos', help_text="Fase del torneo")
    grupo = models.CharField(max_length=10, blank=True, help_text="Grupo (solo para fase de grupos, ej: A, B, C...)")
    estadio = models.CharField(max_length=100, blank=True, help_text="Nombre del estadio")
    ciudad = models.CharField(max_length=50, blank=True, help_text="Ciudad sede")

    # Resultado real (se llena después del partido)
    goles_local = models.IntegerField(null=True, blank=True, help_text="Goles del equipo local (resultado real)")
    goles_visitante = models.IntegerField(null=True, blank=True, help_text="Goles del equipo visitante (resultado real)")
    finalizado = models.BooleanField(default=False, help_text="¿Partido finalizado?")

    # ID externo de la API
    api_id = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text="ID del partido en TheSportsDB")

    # Control
    activo = models.BooleanField(default=True, help_text="¿Partido activo para predicciones?")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'polla_partidos'
        ordering = ['fecha_hora']
        indexes = [
            models.Index(fields=['fecha_hora']),
            models.Index(fields=['fase', 'fecha_hora']),
            models.Index(fields=['finalizado']),
        ]
        verbose_name = 'Partido Mundial'
        verbose_name_plural = 'Partidos Mundiales'

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.get_fase_display()}"

    @property
    def multiplicador_puntos(self):
        """Retorna el multiplicador de puntos según la fase"""
        return self.MULTIPLICADORES_PUNTOS.get(self.fase, 1)

    @property
    def acepta_predicciones(self):
        """Verifica si aún se aceptan predicciones (5 min antes del partido)"""
        from django.utils import timezone
        from datetime import timedelta

        if self.finalizado or not self.activo:
            return False

        # Cerrar predicciones 5 minutos antes del partido
        cierre = self.fecha_hora - timedelta(minutes=5)
        return timezone.now() < cierre

    @property
    def tiempo_restante(self):
        """Retorna el tiempo restante para hacer predicciones"""
        from django.utils import timezone
        from datetime import timedelta

        if not self.acepta_predicciones:
            return "Cerrado"

        cierre = self.fecha_hora - timedelta(minutes=5)
        diferencia = cierre - timezone.now()

        if diferencia.days > 0:
            return f"{diferencia.days}d {diferencia.seconds // 3600}h"
        elif diferencia.seconds > 3600:
            return f"{diferencia.seconds // 3600}h {(diferencia.seconds % 3600) // 60}m"
        else:
            return f"{diferencia.seconds // 60}m"


class PrediccionMundial(models.Model):
    """Predicciones de empleados para partidos del mundial"""

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='predicciones_mundial',
        help_text="Empleado que realiza la predicción"
    )
    partido = models.ForeignKey(
        PartidoMundial,
        on_delete=models.CASCADE,
        related_name='predicciones',
        help_text="Partido para el cual se hace la predicción"
    )

    # Predicción del empleado
    goles_local_prediccion = models.IntegerField(help_text="Predicción de goles del equipo local")
    goles_visitante_prediccion = models.IntegerField(help_text="Predicción de goles del equipo visitante")

    # Puntos obtenidos (calculado automáticamente cuando finaliza el partido)
    puntos_ganados = models.IntegerField(default=0, help_text="Puntos obtenidos por esta predicción")

    # Timestamps
    fecha_prediccion = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora de la predicción")
    fecha_actualizacion = models.DateTimeField(auto_now=True, help_text="Última actualización de la predicción")

    class Meta:
        db_table = 'polla_predicciones'
        unique_together = ['empleado', 'partido']
        ordering = ['-fecha_prediccion']
        indexes = [
            models.Index(fields=['empleado', '-puntos_ganados']),
            models.Index(fields=['partido', '-puntos_ganados']),
        ]
        verbose_name = 'Predicción Mundial'
        verbose_name_plural = 'Predicciones Mundiales'

    def __str__(self):
        return f"{self.empleado.nombre_completo}: {self.goles_local_prediccion}-{self.goles_visitante_prediccion} ({self.partido})"

    def calcular_puntos(self):
        """
        Calcula los puntos obtenidos por esta predicción según el resultado real

        Sistema de puntos:
        - Resultado exacto (marcador + ganador): 5 puntos
        - Ganador correcto: 3 puntos
        - Empate acertado: 3 puntos
        - Acertar goles de un equipo: +1 punto

        Los puntos se multiplican por el multiplicador de la fase
        """
        partido = self.partido

        # Si el partido no ha finalizado, no se calculan puntos
        if not partido.finalizado or partido.goles_local is None or partido.goles_visitante is None:
            self.puntos_ganados = 0
            return 0

        puntos = 0

        # 1. Verificar resultado exacto (5 puntos)
        if (self.goles_local_prediccion == partido.goles_local and
            self.goles_visitante_prediccion == partido.goles_visitante):
            puntos = 5

        # 2. Verificar ganador correcto o empate (3 puntos)
        elif self._mismo_resultado(partido):
            puntos = 3

            # 3. Bonus: Acertar goles de algún equipo (+1 punto)
            if self.goles_local_prediccion == partido.goles_local:
                puntos += 1
            elif self.goles_visitante_prediccion == partido.goles_visitante:
                puntos += 1

        # 4. Solo acertó goles de un equipo sin acertar ganador (1 punto)
        else:
            if self.goles_local_prediccion == partido.goles_local:
                puntos += 1
            if self.goles_visitante_prediccion == partido.goles_visitante:
                puntos += 1

        # Aplicar multiplicador de la fase
        puntos_finales = puntos * partido.multiplicador_puntos

        self.puntos_ganados = puntos_finales
        return puntos_finales

    def _mismo_resultado(self, partido):
        """Verifica si acertó el resultado (ganador o empate)"""
        # Resultado real
        if partido.goles_local > partido.goles_visitante:
            resultado_real = 'local'
        elif partido.goles_local < partido.goles_visitante:
            resultado_real = 'visitante'
        else:
            resultado_real = 'empate'

        # Predicción
        if self.goles_local_prediccion > self.goles_visitante_prediccion:
            prediccion = 'local'
        elif self.goles_local_prediccion < self.goles_visitante_prediccion:
            prediccion = 'visitante'
        else:
            prediccion = 'empate'

        return resultado_real == prediccion

    @property
    def puede_modificar(self):
        """Verifica si aún puede modificar la predicción"""
        return self.partido.acepta_predicciones

