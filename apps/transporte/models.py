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
from django.utils import timezone

from custom_storage.media import MediaStorage


def _documento_upload_path(instance, filename):
    """media/vehiculos/<placa>/<tipo>/<año>/<archivo>"""
    placa = (instance.vehiculo.placa or 'sin-placa').replace(' ', '').replace('/', '')
    anio = instance.fecha_expedicion.year if instance.fecha_expedicion else 'sin-fecha'
    return f'vehiculos/{placa}/{instance.tipo}/{anio}/{filename}'


def _recibo_upload_path(instance, filename):
    """media/vehiculos/<placa>/gastos/<año>/<mes>/<archivo>"""
    placa = (instance.vehiculo.placa or 'sin-placa').replace(' ', '').replace('/', '')
    f = instance.fecha or date.today()
    return f'vehiculos/{placa}/gastos/{f.year}/{f.month:02d}/{filename}'


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

    # Cuando se cambia el conductor hay que avisarle a Odoo. Si ese aviso
    # falla —Odoo caído, red— el cambio no se pierde: queda marcado y la
    # sincronización lo reintenta. Sin esto, una caída de Odoo dejaría la
    # asignación solo en SIGHU y nadie se enteraría.
    asignacion_sincronizada = models.BooleanField(
        default=True,
        help_text='False cuando falta avisarle a Odoo del cambio de conductor.',
    )
    asignacion_desde = models.DateField(
        null=True, blank=True,
        help_text='Fecha desde la que rige la asignación actual.',
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


class GastoVehiculo(models.Model):
    """Gasto de un vehículo, registrado por el conductor con su recibo.

    El conductor lo captura desde el celular al momento de pagar, porque un
    recibo de combustible que se guarda en el bolsillo para digitarlo el
    viernes casi nunca llega. Por eso el recibo es obligatorio: sin soporte
    el gasto no se puede legalizar.

    Las multas son el caso aparte. Cuando la responsable es la empresa
    entran al costo del vehículo; cuando es del conductor no, porque no son
    un gasto de operación sino algo que él debe. Mezclarlas distorsiona el
    costo por kilómetro, que es justo lo que se quiere medir.
    """
    COMBUSTIBLE = 'combustible'
    PEAJE = 'peaje'
    MANTENIMIENTO = 'mantenimiento'
    REPARACION = 'reparacion'
    LLANTAS = 'llantas'
    LAVADO = 'lavado'
    PARQUEADERO = 'parqueadero'
    MULTA = 'multa'
    OTRO = 'otro'
    TIPOS = [
        (COMBUSTIBLE, 'Combustible'),
        (PEAJE, 'Peaje'),
        (MANTENIMIENTO, 'Mantenimiento'),
        (REPARACION, 'Reparación'),
        (LLANTAS, 'Llantas'),
        (LAVADO, 'Lavado'),
        (PARQUEADERO, 'Parqueadero'),
        (MULTA, 'Multa o comparendo'),
        (OTRO, 'Otro'),
    ]

    RESPONSABLE_EMPRESA = 'empresa'
    RESPONSABLE_CONDUCTOR = 'conductor'
    RESPONSABLES = [
        (RESPONSABLE_EMPRESA, 'La empresa'),
        (RESPONSABLE_CONDUCTOR, 'El conductor'),
    ]

    PENDIENTE = 'pendiente'
    APROBADO = 'aprobado'
    RECHAZADO = 'rechazado'
    ESTADOS = [
        (PENDIENTE, 'Pendiente de revisión'),
        (APROBADO, 'Aprobado'),
        (RECHAZADO, 'Rechazado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT, related_name='gastos')
    conductor = models.ForeignKey(
        'employees.Empleado', on_delete=models.PROTECT,
        related_name='gastos_vehiculo',
        help_text='Quien hizo el gasto.')

    tipo = models.CharField(max_length=20, choices=TIPOS)
    monto = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(1)],
        help_text='Valor pagado, en pesos.')
    fecha = models.DateField(default=date.today)
    descripcion = models.CharField(
        max_length=200, blank=True,
        help_text='Dónde fue, qué se hizo. Opcional salvo en "Otro".')

    # Solo aplica a multas: quién la asume.
    responsable = models.CharField(
        max_length=12, choices=RESPONSABLES, blank=True,
        help_text='Solo para multas: quién responde por ella.')

    recibo = models.FileField(
        upload_to=_recibo_upload_path,
        storage=MediaStorage(),
        help_text='Foto o PDF del recibo. Sin soporte el gasto no se legaliza.')

    kilometraje = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Kilometraje del vehículo al momento del gasto. Opcional.')

    estado = models.CharField(max_length=12, choices=ESTADOS, default=PENDIENTE)
    observaciones_revision = models.TextField(
        blank=True, help_text='Por qué se rechazó, o nota de quien revisó.')
    revisado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='gastos_vehiculo_revisados')
    fecha_revision = models.DateTimeField(null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transporte_gastos_vehiculo'
        verbose_name = 'Gasto de vehículo'
        verbose_name_plural = 'Gastos de vehículos'
        ordering = ['-fecha', '-fecha_creacion']
        indexes = [
            models.Index(fields=['vehiculo', '-fecha']),
            models.Index(fields=['conductor', '-fecha']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} {self.monto} — {self.vehiculo.placa} ({self.fecha})'

    def clean(self):
        errores = {}
        if self.tipo == self.MULTA and not self.responsable:
            errores['responsable'] = 'En una multa hay que decir quién responde.'
        if self.tipo != self.MULTA and self.responsable:
            errores['responsable'] = 'El responsable solo aplica a las multas.'
        if self.tipo == self.OTRO and not self.descripcion.strip():
            errores['descripcion'] = 'Si el tipo es "Otro", explica de qué se trata.'
        if self.fecha and self.fecha > date.today():
            errores['fecha'] = 'No se puede registrar un gasto con fecha futura.'
        if errores:
            raise ValidationError(errores)

    @property
    def cuenta_como_costo(self):
        """Si entra al costo de operación del vehículo.

        Las multas que asume el conductor quedan fuera: son una deuda suya,
        no un gasto de operar el vehículo.
        """
        if self.estado == self.RECHAZADO:
            return False
        return not (self.tipo == self.MULTA
                    and self.responsable == self.RESPONSABLE_CONDUCTOR)

    @property
    def editable_por_conductor(self):
        """Mientras nadie lo haya revisado, el conductor puede corregirlo."""
        return self.estado == self.PENDIENTE


class ServicioIniciado(models.Model):
    """El momento en que el conductor sale a hacer un servicio de Odoo.

    El servicio es de Odoo: allá se crea, se le asigna el vehículo y se
    cobra. Lo único que SIGHU agrega es el instante en que el vehículo
    arrancó, que es lo que nadie más registra y que el conductor marca
    desde el celular al salir.

    Queda guardado aquí y no solo se le manda a Odoo porque la salida no
    puede depender de que Odoo conteste: el camión ya salió, y si el aviso
    falla ese dato se pierde para siempre. Lo que falle se reintenta.

    El servicio se identifica por `(odoo_modelo, odoo_id)` y no por `ref`:
    la referencia es para leerla, y dos modelos distintos de Odoo podrían
    repetirla. Se guarda además un resumen de a dónde iba, porque cuando
    Odoo cierra el documento el servicio desaparece de la consulta y sin
    ese texto el historial quedaría en un número.
    """

    # Margen para deshacer un inicio marcado por error. Corto a propósito:
    # es para el dedo que se resbaló al arrancar, no para reescribir a qué
    # hora salió el camión.
    MINUTOS_PARA_DESHACER = 15

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    odoo_modelo = models.CharField(
        max_length=80,
        help_text='Modelo del documento en Odoo (p. ej. stock.picking).')
    odoo_id = models.PositiveIntegerField(
        help_text='Id del documento en Odoo.')
    ref = models.CharField(
        max_length=60, blank=True,
        help_text='Referencia legible del servicio, como la muestra Odoo.')
    tipo = models.CharField(
        max_length=40, blank=True,
        help_text='Tipo de servicio según Odoo: traslado, entrega, recepción.')
    resumen = models.CharField(
        max_length=200, blank=True,
        help_text='A dónde iba, para que el historial se entienda después.')

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT, related_name='servicios_iniciados')
    conductor = models.ForeignKey(
        'employees.Empleado', on_delete=models.PROTECT,
        related_name='servicios_iniciados',
        help_text='Quien salió a hacerlo.')

    iniciado_en = models.DateTimeField(
        default=timezone.now,
        help_text='Momento en que el conductor marcó la salida.')
    kilometraje = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Kilometraje al salir. Opcional.')

    # La entrega cierra el viaje del lado del conductor. El documento de
    # Odoo lo cierra Odoo; esto es lo que el conductor sabe y nadie más:
    # que ya descargó.
    entregado_en = models.DateTimeField(
        null=True, blank=True,
        help_text='Momento en que el conductor marcó la entrega.')
    kilometraje_llegada = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Kilometraje al llegar. Opcional.')

    # Anular en vez de borrar: un inicio equivocado se corrige, pero quién
    # lo marcó y a qué hora sigue siendo parte del historial.
    anulado_en = models.DateTimeField(null=True, blank=True)
    anulado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='servicios_inicio_anulados')

    sincronizado = models.BooleanField(
        default=False,
        help_text='True cuando Odoo ya recibió el aviso de la salida.')
    fecha_sincronizacion = models.DateTimeField(null=True, blank=True)
    ultimo_error = models.CharField(
        max_length=300, blank=True,
        help_text='Por qué falló el último intento de avisarle a Odoo.')

    # La entrega lleva su propio estado de aviso: salida y entrega son dos
    # hechos distintos y uno puede llegar a Odoo sin el otro.
    entrega_sincronizada = models.BooleanField(
        default=False,
        help_text='True cuando Odoo ya recibió el aviso de la entrega.')
    fecha_sincronizacion_entrega = models.DateTimeField(null=True, blank=True)
    ultimo_error_entrega = models.CharField(max_length=300, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transporte_servicios_iniciados'
        verbose_name = 'Servicio iniciado'
        verbose_name_plural = 'Servicios iniciados'
        ordering = ['-iniciado_en']
        constraints = [
            # Un servicio no se puede iniciar dos veces. La restricción
            # excluye los anulados para que, tras deshacer, se pueda volver
            # a marcar la salida.
            models.UniqueConstraint(
                fields=['odoo_modelo', 'odoo_id'],
                condition=models.Q(anulado_en__isnull=True),
                name='servicio_iniciado_una_sola_vez',
            ),
        ]
        indexes = [
            models.Index(fields=['odoo_id']),
            models.Index(fields=['vehiculo', '-iniciado_en']),
            models.Index(fields=['conductor', '-iniciado_en']),
            models.Index(fields=['sincronizado']),
        ]

    def __str__(self):
        return f'{self.ref or self.odoo_id} — {self.vehiculo.placa} ({self.iniciado_en:%d/%m/%Y %H:%M})'

    def clean(self):
        if self.entregado_en and self.entregado_en < self.iniciado_en:
            raise ValidationError({
                'entregado_en': 'La entrega no puede ser anterior a la salida.'
            })

    @property
    def esta_activo(self):
        return self.anulado_en is None

    @property
    def esta_entregado(self):
        return self.entregado_en is not None

    @property
    def puede_entregarse(self):
        """Se entrega lo que salió y todavía no se ha entregado."""
        return self.esta_activo and not self.esta_entregado

    @property
    def puede_deshacerse(self):
        """Solo el rato justo después de marcarlo, y si Odoo no lo recibió.

        Si Odoo ya lo registró, deshacerlo aquí dejaría los dos sistemas
        diciendo cosas distintas; eso lo arregla el jefe, no el conductor.
        Un servicio ya entregado tampoco se des-inicia: primero se deshace
        la entrega.
        """
        if not self.esta_activo or self.sincronizado or self.esta_entregado:
            return False
        limite = self.fecha_creacion + timedelta(minutes=self.MINUTOS_PARA_DESHACER)
        return timezone.now() <= limite

    @property
    def puede_deshacer_entrega(self):
        """Mismo margen que la salida, por la misma razón: el dedo."""
        if not self.esta_activo or not self.esta_entregado:
            return False
        if self.entrega_sincronizada:
            return False
        limite = self.entregado_en + timedelta(minutes=self.MINUTOS_PARA_DESHACER)
        return timezone.now() <= limite

    @property
    def duracion_texto(self):
        """Cuánto duró el viaje, en palabras. Vacío si no ha entregado."""
        if not self.esta_entregado:
            return ''
        minutos = int((self.entregado_en - self.iniciado_en).total_seconds() // 60)
        if minutos < 0:
            return ''
        horas, resto = divmod(minutos, 60)
        if horas and resto:
            return f'{horas} h {resto} min'
        if horas:
            return f'{horas} h'
        return f'{resto} min'
