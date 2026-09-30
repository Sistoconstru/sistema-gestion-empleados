"""Beneficios de retención en la fuente (Art. 383, 387, 388 ET).

Flujo:
1. Empleado marca `Empleado.es_declarante = True` desde su perfil.
2. Empleado carga un `TramiteBeneficio` por concepto, con sus soportes.
3. RRHH revisa. Al validar, SIGHU envía el trámite a Odoo (endpoint
   `POST /sighu_sync/webhook/beneficio_retencion`) y notifica al empleado
   para que firme la carta juramentada. Al rechazar, queda en SIGHU con
   observación y una notificación al empleado.

El identificador `tramite_uuid` viaja a Odoo como llave de idempotencia.

Ver docs/INTEGRACION_ODOO_BENEFICIOS_RETENCION.md para el contrato del
endpoint de Odoo.
"""
import uuid

from django.conf import settings
from django.db import models

from custom_storage.media import MediaStorage


def _soporte_upload_path(instance, filename):
    """Ruta S3 para el archivo del soporte principal."""
    tramite_id = instance.tramite_id
    return f'beneficios_retencion/{tramite_id}/{filename}'


def _soporte_dependiente_upload_path(instance, filename):
    """Ruta S3 para el archivo del soporte de un dependiente."""
    tramite_id = instance.dependiente.tramite_id
    dep_id = instance.dependiente_id
    return f'beneficios_retencion/{tramite_id}/dep/{dep_id}/{filename}'


class TramiteBeneficio(models.Model):
    """Un trámite = un beneficio de retención para un empleado en un año.

    Puede tener múltiples soportes y (para dependientes) múltiples
    dependientes. El `tramite_uuid` es la llave que se envía a Odoo.
    """

    TIPO_CHOICES = [
        ('intereses_vivienda', 'Intereses de vivienda'),
        ('medicina_prepagada', 'Medicina prepagada'),
        ('dependientes', 'Dependientes'),
        ('aportes_voluntarios_pension', 'Aportes voluntarios a pensión'),
        ('afc', 'AFC (Ahorro para el Fomento a la Construcción)'),
    ]

    PERIODICIDAD_CHOICES = [
        ('anual', 'Anual'),
        ('mensual', 'Mensual'),
    ]

    ESTADO_CHOICES = [
        ('pendiente_rrhh', 'Pendiente de revisión de RRHH'),
        ('validado', 'Validado por RRHH'),
        ('rechazado', 'Rechazado'),
        ('revocado', 'Revocado'),
        ('error_envio_odoo', 'Error al enviar a Odoo (reintentar)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey(
        'employees.Empleado',
        on_delete=models.CASCADE,
        related_name='tramites_beneficio_retencion',
    )
    tipo = models.CharField(max_length=40, choices=TIPO_CHOICES)
    anio_aplicacion = models.PositiveIntegerField(
        help_text="Año de nómina en el que aplica el beneficio.",
    )
    periodo_certificado = models.PositiveIntegerField(
        help_text=(
            "Año que reporta el documento. Vivienda/medicina = anio_aplicacion - 1. "
            "Dependientes = mismo anio_aplicacion."
        ),
    )
    valor = models.DecimalField(
        max_digits=14, decimal_places=2,
        null=True, blank=True,
        help_text="En pesos, tal como está en el soporte. Sin topes. Opcional en dependientes.",
    )
    periodicidad = models.CharField(
        max_length=10, choices=PERIODICIDAD_CHOICES,
        blank=True,
        help_text="Cómo leer `valor`. Vacío en dependientes.",
    )
    observacion_empleado = models.TextField(
        blank=True,
        help_text="Texto libre que el empleado agrega al cargar el trámite.",
    )

    estado = models.CharField(
        max_length=30, choices=ESTADO_CHOICES, default='pendiente_rrhh',
    )
    observacion_rrhh = models.TextField(
        blank=True,
        help_text="Motivo del rechazo o comentario de validación de RRHH.",
    )
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='beneficios_validados',
        help_text="Usuario RRHH que validó o rechazó el trámite.",
    )
    validado_el = models.DateField(
        null=True, blank=True,
        help_text="Fecha en que RRHH validó o rechazó el trámite.",
    )

    # Integración Odoo
    odoo_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="ID que devuelve Odoo tras registrar el trámite.",
    )
    aplica_desde = models.DateField(
        null=True, blank=True,
        help_text="Primera nómina afectada (según Odoo).",
    )
    vence_el = models.DateField(
        null=True, blank=True,
        help_text="Último día de vigencia (según Odoo, típicamente 30/04/N+1).",
    )
    respuesta_odoo = models.JSONField(
        null=True, blank=True,
        help_text="Última respuesta cruda de Odoo, para auditoría.",
    )
    ultimo_error_odoo = models.TextField(
        blank=True,
        help_text="Detalle del último error al llamar a Odoo, si hubo.",
    )
    enviado_a_odoo_el = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha/hora del último envío exitoso a Odoo.",
    )

    # Carta juramentada
    carta_generada_el = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha/hora en que se generó la carta juramentada por primera vez.",
    )
    carta_firmada = models.BooleanField(
        default=False,
        help_text="RRHH marca esto cuando el empleado firmó físicamente la carta.",
    )
    carta_firmada_el = models.DateTimeField(null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'beneficios_retencion_tramite'
        verbose_name = 'Trámite de beneficio de retención'
        verbose_name_plural = 'Trámites de beneficios de retención'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['empleado', 'anio_aplicacion']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} {self.anio_aplicacion} — {self.empleado}'


class SoporteBeneficio(models.Model):
    """Archivo adjunto (PDF/imagen) del trámite principal."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tramite = models.ForeignKey(
        TramiteBeneficio, on_delete=models.CASCADE, related_name='soportes',
    )
    archivo = models.FileField(
        upload_to=_soporte_upload_path,
        max_length=500,
        storage=MediaStorage(),
    )
    nombre_original = models.CharField(max_length=255, blank=True)
    tipo_mime = models.CharField(max_length=100, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'beneficios_retencion_soporte'
        verbose_name = 'Soporte de beneficio'
        verbose_name_plural = 'Soportes de beneficios'

    def __str__(self):
        return self.nombre_original or self.archivo.name


class DependienteBeneficio(models.Model):
    """Dependiente asociado a un trámite tipo=dependientes.

    Un solo trámite puede tener múltiples dependientes; la deducción se
    aplica una sola vez, pero Odoo necesita el detalle de todos.
    """

    CAUSAL_CHOICES = [
        ('hijo_menor_18', 'Hijo menor de 18 años'),
        ('hijo_18_23_estudiando', 'Hijo 18-23 años estudiando'),
        ('hijo_mayor_23_dependiente', 'Hijo mayor de 23 dependiente'),
        ('conyuge_dependiente', 'Cónyuge/compañero dependiente'),
        ('familiar_dependiente', 'Padres o hermanos dependientes'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tramite = models.ForeignKey(
        TramiteBeneficio, on_delete=models.CASCADE, related_name='dependientes',
    )
    nombres = models.CharField(max_length=200)
    numero_documento = models.CharField(max_length=30, blank=True)
    parentesco = models.CharField(
        max_length=50, blank=True,
        help_text="Descripción libre e informativa (ej: 'hijo', 'esposa').",
    )
    causal = models.CharField(
        max_length=40, choices=CAUSAL_CHOICES,
        help_text="Define qué documento se exige.",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'beneficios_retencion_dependiente'
        verbose_name = 'Dependiente'
        verbose_name_plural = 'Dependientes'

    def __str__(self):
        return f'{self.nombres} ({self.get_causal_display()})'


class SoporteDependiente(models.Model):
    """Soporte específico de un dependiente (certificado de estudio,
    certificado médico, etc.)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dependiente = models.ForeignKey(
        DependienteBeneficio, on_delete=models.CASCADE, related_name='soportes',
    )
    archivo = models.FileField(
        upload_to=_soporte_dependiente_upload_path,
        max_length=500,
        storage=MediaStorage(),
    )
    nombre_original = models.CharField(max_length=255, blank=True)
    tipo_mime = models.CharField(max_length=100, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'beneficios_retencion_soporte_dependiente'
        verbose_name = 'Soporte de dependiente'
        verbose_name_plural = 'Soportes de dependientes'

    def __str__(self):
        return self.nombre_original or self.archivo.name
