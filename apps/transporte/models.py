# =============================================================================
# apps/transporte/models.py
# =============================================================================
"""Flota de vehículos: documentos legales y sus vencimientos.

El maestro de vehículos vive en Odoo, que es quien los da de alta, los asigna
y los cobra. Aquí se guarda un espejo identificado por el id de Odoo —no por
la placa, que viene escrita de formas distintas ("JYN 240", "NQR-ESQ762") y
cruzaría mal— y, sobre ese espejo, lo que Odoo no tiene: los documentos
legales del vehículo y el aviso de cuándo vencen.
"""

import uuid
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from custom_storage.media import MediaStorage


def _documento_upload_path(instance, filename):
    """media/vehiculos/<placa>/<tipo>/<año>/<archivo>"""
    placa = (instance.vehiculo.placa or 'sin-placa').replace(' ', '').replace('/', '')
    anio = instance.fecha_expedicion.year if instance.fecha_expedicion else 'sin-fecha'
    return f'vehiculos/{placa}/{instance.tipo}/{anio}/{filename}'


class Vehiculo(models.Model):
    """Espejo del vehículo que administra Odoo.

    Solo se sincroniza lo necesario para identificarlo y saber quién lo
    conduce. Marca, modelo o estado se refrescan desde Odoo; cambiarlos aquí
    no viaja de vuelta.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Clave real: el id que Odoo asigna. La placa es para que la lean las
    # personas, y puede cambiar de formato entre sistemas.
    odoo_id = models.PositiveIntegerField(
        unique=True,
        verbose_name='ID en Odoo',
        help_text='Identificador del vehículo en Odoo. Es la clave de cruce entre los dos sistemas.',
    )
    placa = models.CharField(max_length=20, verbose_name='Placa')
    marca = models.CharField(max_length=60, blank=True)
    modelo = models.CharField(max_length=60, blank=True)
    anio = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Año',
        validators=[MinValueValidator(1900)],
    )

    conductor = models.ForeignKey(
        'employees.Empleado',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='vehiculos_asignados',
        help_text='Conductor asignado actualmente. La asignación se avisa a Odoo.',
    )

    # Un vehículo que Odoo archiva deja de usarse, pero sus documentos y
    # gastos siguen siendo parte del historial y no se borran. Odoo no
    # reutiliza nunca el id, así que ese historial siempre cruza.
    activo = models.BooleanField(
        default=True,
        help_text='Se desmarca cuando Odoo lo reporta archivado. El historial se conserva.',
    )
    fecha_baja = models.DateField(
        null=True, blank=True,
        help_text='Fecha de baja según Odoo. Solo informativa.',
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_sincronizacion = models.DateTimeField(
        null=True, blank=True,
        help_text='Última vez que se refrescó desde Odoo.',
    )

    class Meta:
        db_table = 'transporte_vehiculos'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['placa']
        indexes = [
            models.Index(fields=['activo']),
            models.Index(fields=['conductor']),
        ]

    def __str__(self):
        return f'{self.placa} — {self.marca} {self.modelo}'.strip()

    def clean(self):
        # Odoo rechaza asignar conductor o flete a un vehículo archivado. Se
        # valida también aquí para que el error salga al guardar y no al
        # intentar sincronizar, cuando ya es tarde y confunde más.
        if self.conductor_id and not self.activo:
            raise ValidationError({
                'conductor': 'No se puede asignar conductor a un vehículo dado de baja.'
            })

    @property
    def placa_normalizada(self):
        """Placa sin espacios ni guiones, en mayúsculas, para comparar.

        Odoo y SIGHU no la escriben igual; esto permite buscarla sin que el
        formato estorbe. No reemplaza a `odoo_id` como clave.
        """
        return ''.join(c for c in (self.placa or '').upper() if c.isalnum())

    def documentos_vigentes(self):
        """El documento más reciente de cada tipo."""
        vigentes = []
        for tipo, _ in DocumentoVehiculo.TIPOS:
            doc = self.documentos.filter(tipo=tipo).order_by(
                '-fecha_vencimiento', '-fecha_expedicion').first()
            if doc:
                vigentes.append(doc)
        return vigentes

    def documentos_por_vencer(self, dias=None):
        """Documentos vigentes vencidos o próximos a vencer."""
        dias = DocumentoVehiculo.DIAS_AVISO if dias is None else dias
        limite = date.today() + timedelta(days=dias)
        return [d for d in self.documentos_vigentes()
                if d.fecha_vencimiento and d.fecha_vencimiento <= limite
                and d.aplica]


class DocumentoVehiculo(models.Model):
    """Documento legal de un vehículo, con historial.

    Se guarda cada renovación como un registro nuevo: el SOAT del año pasado
    sigue siendo la prueba de que el vehículo estuvo cubierto, y sobreescribirlo
    con el nuevo borraría esa constancia. El "vigente" de cada tipo es
    simplemente el de vencimiento más lejano.
    """
    SOAT = 'soat'
    TECNOMECANICA = 'tecnomecanica'
    IMPUESTO = 'impuesto'
    RODAMIENTO = 'rodamiento'
    TIPOS = [
        (SOAT, 'SOAT'),
        (TECNOMECANICA, 'Revisión tecnicomecánica'),
        (IMPUESTO, 'Impuesto vehicular'),
        (RODAMIENTO, 'Impuesto de rodamiento'),
    ]

    # Días antes del vencimiento en que se empieza a avisar. Un SOAT se
    # consigue en el día, pero la tecnomecánica puede necesitar cita y un
    # arreglo previo, así que un mes da margen para ambos.
    DIAS_AVISO = 30

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=20, choices=TIPOS)

    numero = models.CharField(
        max_length=60, blank=True,
        verbose_name='Número',
        help_text='Número de póliza (SOAT) o de certificado (tecnomecánica).',
    )
    entidad = models.CharField(
        max_length=120, blank=True,
        verbose_name='Entidad',
        help_text='Aseguradora del SOAT o centro de diagnóstico automotor.',
    )
    fecha_expedicion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(
        null=True, blank=True,
        help_text='Se calcula sola al guardar si se deja vacía.',
    )
    valor = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
    )

    # El impuesto de rodamiento no aplica en todos los municipios. Si no
    # aplica, el documento queda registrado como constancia pero no se avisa.
    aplica = models.BooleanField(
        default=True,
        help_text='Desmarcar cuando el tributo no aplica a este vehículo (p. ej. rodamiento en municipios que no lo cobran).',
    )

    archivo = models.FileField(
        upload_to=_documento_upload_path,
        storage=MediaStorage(),
        blank=True,
        help_text='PDF o foto del documento.',
    )
    observaciones = models.TextField(blank=True)

    registrado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documentos_vehiculo_registrados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transporte_documentos_vehiculo'
        verbose_name = 'Documento de vehículo'
        verbose_name_plural = 'Documentos de vehículos'
        ordering = ['vehiculo', 'tipo', '-fecha_vencimiento']
        indexes = [
            models.Index(fields=['vehiculo', 'tipo']),
            models.Index(fields=['fecha_vencimiento']),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.vehiculo.placa} ({self.fecha_vencimiento or "sin fecha"})'

    # --- Cálculo del vencimiento ----------------------------------------

    def calcular_vencimiento(self):
        """Fecha de vencimiento según el tipo, o None si no se puede.

        SOAT y tecnomecánica vencen al año de expedidos. El impuesto
        vehicular y el de rodamiento son anuales de calendario y vencen en
        una fecha fija, no a los 365 días del pago.
        """
        if self.tipo in (self.SOAT, self.TECNOMECANICA):
            if not self.fecha_expedicion:
                return None
            try:
                return self.fecha_expedicion.replace(
                    year=self.fecha_expedicion.year + 1)
            except ValueError:
                # 29 de febrero: el año siguiente no lo tiene.
                return self.fecha_expedicion.replace(
                    year=self.fecha_expedicion.year + 1, day=28)

        anio = (self.fecha_expedicion or date.today()).year
        if self.tipo == self.IMPUESTO:
            return date(anio, 6, 30)
        if self.tipo == self.RODAMIENTO:
            return date(anio, 12, 31)
        return None

    def save(self, *args, **kwargs):
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = self.calcular_vencimiento()
        super().save(*args, **kwargs)

    def clean(self):
        errores = {}
        if self.tipo in (self.SOAT, self.TECNOMECANICA):
            if not self.fecha_expedicion:
                errores['fecha_expedicion'] = 'Obligatoria para SOAT y tecnomecánica.'
            if not self.numero:
                errores['numero'] = 'Indica el número de póliza o certificado.'
            if not self.entidad:
                errores['entidad'] = (
                    'Indica la aseguradora.' if self.tipo == self.SOAT
                    else 'Indica el centro de diagnóstico.')
        if (self.fecha_expedicion and self.fecha_vencimiento
                and self.fecha_vencimiento < self.fecha_expedicion):
            errores['fecha_vencimiento'] = 'No puede ser anterior a la expedición.'
        if self.fecha_expedicion and self.fecha_expedicion > date.today():
            errores['fecha_expedicion'] = 'No puede ser una fecha futura.'
        if errores:
            raise ValidationError(errores)

    # --- Estado ----------------------------------------------------------

    @property
    def dias_para_vencer(self):
        if not self.fecha_vencimiento:
            return None
        return (self.fecha_vencimiento - date.today()).days

    @property
    def esta_vencido(self):
        d = self.dias_para_vencer
        return d is not None and d < 0

    @property
    def por_vencer(self):
        d = self.dias_para_vencer
        return d is not None and 0 <= d <= self.DIAS_AVISO

    @property
    def estado(self):
        if not self.aplica:
            return 'no_aplica'
        if self.fecha_vencimiento is None:
            return 'sin_fecha'
        if self.esta_vencido:
            return 'vencido'
        if self.por_vencer:
            return 'por_vencer'
        return 'vigente'

    @property
    def estado_display(self):
        return {
            'no_aplica': 'No aplica',
            'sin_fecha': 'Sin fecha',
            'vencido': 'Vencido',
            'por_vencer': 'Por vencer',
            'vigente': 'Vigente',
        }[self.estado]
