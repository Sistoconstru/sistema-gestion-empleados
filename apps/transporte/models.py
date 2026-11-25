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
    """media/vehiculos/<placa>/gastos/<año>/<mes>/<archivo>

    Sin vehículo el recibo cuelga del conductor: hay gastos que no son de
    ningún carro y aun así hay que poder encontrarlos después.
    """
    f = instance.fecha or date.today()
    if instance.vehiculo_id and instance.vehiculo.placa:
        carpeta = instance.vehiculo.placa.replace(' ', '').replace('/', '')
        return f'vehiculos/{carpeta}/gastos/{f.year}/{f.month:02d}/{filename}'
    cedula = (getattr(instance.conductor, 'numero_documento', '')
              or 'sin-cedula')
    return f'gastos-conductor/{cedula}/{f.year}/{f.month:02d}/{filename}'


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
    POLIZA = 'poliza'
    IMPUESTO = 'impuesto'
    RODAMIENTO = 'rodamiento'
    TIPOS = [
        (SOAT, 'SOAT'),
        (TECNOMECANICA, 'Revisión tecnicomecánica'),
        (POLIZA, 'Póliza de responsabilidad civil'),
        (IMPUESTO, 'Impuesto vehicular'),
        (RODAMIENTO, 'Semaforización o derechos de tránsito'),
    ]

    # Los que vencen al año de expedidos, no en una fecha de calendario.
    ANUALES_DESDE_EXPEDICION = (SOAT, TECNOMECANICA, POLIZA)

    # Los que son un papel emitido por alguien: tienen número y entidad.
    # El impuesto y el rodamiento son un pago, no una póliza.
    CON_NUMERO_Y_ENTIDAD = (SOAT, TECNOMECANICA, POLIZA)

    # Tributos anuales: el plazo es una fecha del calendario, (mes, día).
    # El impuesto vehicular se paga hasta junio; la semaforización se puede
    # pagar en cualquier momento del año, así que su plazo es el 31 de
    # diciembre.
    LIMITES_ANUALES = {
        IMPUESTO: (6, 30),
        RODAMIENTO: (12, 31),
    }

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
        help_text='Desmarcar cuando el tributo no aplica a este vehículo (p. ej. semaforización en municipios que no la cobran).',
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

        SOAT, tecnomecánica y póliza vencen al año de expedidos.

        Los tributos anuales no: lo que vence no es el pago sino el plazo
        para hacer el siguiente, que cae en una fecha fija del calendario.
        Por eso un pago del año en curso queda vigente hasta el plazo del
        año que viene.

        Lo calculado es una propuesta: el campo queda editable porque una
        póliza puede venir a seis meses o a dos años según se contrate, y
        porque un tributo pagado tarde corresponde al año anterior y
        entonces la fecha hay que escribirla.
        """
        if self.tipo in self.ANUALES_DESDE_EXPEDICION:
            if not self.fecha_expedicion:
                return None
            try:
                return self.fecha_expedicion.replace(
                    year=self.fecha_expedicion.year + 1)
            except ValueError:
                # 29 de febrero: el año siguiente no lo tiene.
                return self.fecha_expedicion.replace(
                    year=self.fecha_expedicion.year + 1, day=28)

        limite = self.LIMITES_ANUALES.get(self.tipo)
        if not limite:
            return None

        # El pago cubre su propio año: lo que vence es el plazo del año
        # siguiente. Un impuesto de 2026 pagado en junio de 2026 deja al
        # vehículo al día hasta el 30 de junio de 2027, que es cuando toca
        # el de 2027. Calcularlo sobre el mismo año lo marcaba vencido a
        # los doce días de haberlo pagado.
        mes, dia = limite
        anio = (self.fecha_expedicion or date.today()).year
        return date(anio + 1, mes, dia)

    def save(self, *args, **kwargs):
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = self.calcular_vencimiento()
        super().save(*args, **kwargs)

    def clean(self):
        errores = {}
        if self.tipo in self.CON_NUMERO_Y_ENTIDAD:
            if not self.fecha_expedicion:
                errores['fecha_expedicion'] = (
                    'Obligatoria para SOAT, tecnomecánica y pólizas.')
            if not self.numero:
                errores['numero'] = 'Indica el número de póliza o certificado.'
            if not self.entidad:
                errores['entidad'] = (
                    'Indica el centro de diagnóstico.'
                    if self.tipo == self.TECNOMECANICA
                    else 'Indica la aseguradora.')
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

    # Puede ir vacío a propósito. No todo gasto de un conductor es de un
    # vehículo —un almuerzo en ruta, una herramienta— y forzarlo a colgar de
    # uno ensuciaría el costo del camión con cosas que no le corresponden.
    # Tampoco tiene que ser el vehículo que conduce: si tanquea el de un
    # compañero, el gasto es de ese carro.
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT, related_name='gastos',
        null=True, blank=True,
        help_text='Vehículo al que se le carga. Vacío si el gasto no es de ninguno.')

    conductor = models.ForeignKey(
        'employees.Empleado', on_delete=models.PROTECT,
        related_name='gastos_vehiculo',
        help_text='A quién se le atribuye el gasto.')

    # Quién digitó el registro, que no siempre es de quién es el gasto: un
    # coordinador puede registrarlo por el conductor. Sin esto los dos casos
    # se ven idénticos y no hay forma de saber quién respondió por el dato.
    registrado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='gastos_vehiculo_registrados',
        help_text='Usuario que creó el registro.')

    # El servicio que causó el gasto, cuando fue por uno en particular. Un
    # flete trae sus costos propios —peajes, combustible del viaje— y
    # poder separarlos de los del mes es lo que permite saber qué dejó.
    servicio = models.ForeignKey(
        'ServicioIniciado', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='gastos',
        help_text='Servicio que originó el gasto, si aplica.')

    # Dos llaves y no una: la cuenta del conductor y la del vehículo se
    # cierran por separado, así que el mismo gasto puede estar cerrado en
    # una y seguir abierto en la otra.
    cierre_conductor = models.ForeignKey(
        'CierreGastos', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='gastos_de_conductor',
        help_text='Cierre que selló este gasto en la cuenta del conductor.')
    cierre_vehiculo = models.ForeignKey(
        'CierreGastos', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='gastos_de_vehiculo',
        help_text='Cierre que selló este gasto en la cuenta del vehículo.')

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
            models.Index(fields=['servicio']),
        ]

    def __str__(self):
        donde = self.vehiculo.placa if self.vehiculo_id else 'sin vehículo'
        return f'{self.tipo_texto} {self.monto} — {donde} ({self.fecha})'

    @property
    def tipo_texto(self):
        """El nombre del gasto para mostrarlo.

        En "Otro" es lo que escribió quien lo registró: una lista llena de
        "Otro" no dice nada, y la descripción es justamente el tipo que no
        estaba en la lista. Odoo sigue recibiendo `tipo: "otro"` y la
        descripción aparte, que es lo acordado.
        """
        texto = (self.descripcion or '').strip()
        if self.tipo == self.OTRO and texto:
            return texto[:1].upper() + texto[1:]
        return self.get_tipo_display()

    def clean(self):
        errores = {}
        if self.tipo == self.MULTA and not self.responsable:
            errores['responsable'] = 'En una multa hay que decir quién responde.'
        if self.tipo != self.MULTA and self.responsable:
            errores['responsable'] = 'El responsable solo aplica a las multas.'
        if self.tipo == self.OTRO and not self.descripcion.strip():
            errores['descripcion'] = 'Si es "Otro", escribe en qué fue el gasto.'
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

    @classmethod
    def filtro_costo(cls):
        """`cuenta_como_costo` escrito como consulta.

        Los totales se suman en la base, no recorriendo los gastos en
        memoria, y la regla de qué entra al costo tiene que ser la misma en
        los dos sitios. Vive aquí para que no se separen.
        """
        return ~models.Q(estado=cls.RECHAZADO) & ~models.Q(
            tipo=cls.MULTA, responsable=cls.RESPONSABLE_CONDUCTOR)

    @classmethod
    def filtro_deuda_conductor(cls):
        """Lo que el conductor debe: multas a su cargo, no rechazadas."""
        return models.Q(tipo=cls.MULTA,
                        responsable=cls.RESPONSABLE_CONDUCTOR) & ~models.Q(
            estado=cls.RECHAZADO)

    @property
    def cerrado(self):
        """¿Quedó sellado por algún cierre de cuentas?

        Basta una de las dos cuentas: si el total del vehículo ya se firmó,
        cambiarle el monto al gasto dejaría ese cierre diciendo algo que no
        corresponde con sus propios renglones.
        """
        return bool(self.cierre_conductor_id or self.cierre_vehiculo_id)

    @property
    def editable_por_conductor(self):
        """Mientras nadie lo haya revisado ni cerrado, se puede corregir."""
        return self.estado == self.PENDIENTE and not self.cerrado

    @property
    def lo_registro_otro(self):
        """¿Lo digitó alguien distinto del conductor al que se le atribuye?

        Se compara contra el usuario del conductor y no contra el empleado,
        porque lo que se guarda es quién estaba en la sesión.
        """
        if not self.registrado_por_id:
            return False
        return self.registrado_por_id != getattr(
            self.conductor, 'usuario_id', None)


class CierreGastos(models.Model):
    """Corte de cuentas de un conductor o de un vehículo.

    Lo hace el jefe cuando quiere: no hay períodos automáticos ni cortes de
    fin de mes. Lo que queda es una foto —cuánto sumaban los gastos
    abiertos en ese momento, quién cerró y cuándo— y de ahí en adelante la
    cuenta arranca de cero.

    La pertenencia la marca la llave que queda en cada gasto, **no** el
    rango de fechas. Es la diferencia que importa: un gasto que se registra
    tarde, con fecha de un período ya cerrado, no se cuela en un total que
    alguien ya revisó y dio por bueno. Queda abierto y entra en el cierre
    siguiente. Las fechas que guarda el cierre son para leerlas, no para
    decidir qué entró.

    La del conductor y la del vehículo son cuentas independientes, porque
    responden preguntas distintas: cuánto le debo a Duvier, y cuánto cuesta
    operar el TIA 673. El mismo gasto entra en las dos y cada una se cierra
    por su lado.
    """
    CONDUCTOR = 'conductor'
    VEHICULO = 'vehiculo'
    AMBITOS = [
        (CONDUCTOR, 'Conductor'),
        (VEHICULO, 'Vehículo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ambito = models.CharField(max_length=12, choices=AMBITOS)

    conductor = models.ForeignKey(
        'employees.Empleado', on_delete=models.PROTECT,
        null=True, blank=True, related_name='cierres_gastos')
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT,
        null=True, blank=True, related_name='cierres_gastos')

    # Congelados al cerrar. No se recalculan: el valor de un cierre es
    # justamente que diga lo que decía el día que se firmó.
    total_costo = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deuda = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        help_text='Multas a cargo del conductor. No entran al costo.')
    cantidad = models.PositiveIntegerField(default=0)

    # Informativas: el primero y el último gasto que entraron.
    desde = models.DateField(null=True, blank=True)
    hasta = models.DateField(null=True, blank=True)

    cerrado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cierres_gastos_hechos')
    fecha_cierre = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    # Anular en vez de borrar: si el cierre se hizo mal, los gastos vuelven
    # a quedar abiertos pero queda constancia de que existió y de quién lo
    # deshizo.
    anulado_en = models.DateTimeField(null=True, blank=True)
    anulado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cierres_gastos_anulados')
    motivo_anulacion = models.CharField(max_length=300, blank=True)

    # --- Lo que sabe Odoo de este cierre --------------------------------
    #
    # La contabilidad de los vehículos vive en Odoo, así que el cierre es
    # el documento que viaja: un total sellado, con fecha, responsable y
    # renglones que ya no cambian. Se guarda aquí si llegó, porque el
    # cierre no puede depender de que Odoo conteste: se firma igual y el
    # envío se reintenta.
    sincronizado = models.BooleanField(
        default=False,
        help_text='True cuando Odoo ya recibió el cierre.')
    fecha_sincronizacion = models.DateTimeField(null=True, blank=True)
    odoo_ref = models.CharField(
        max_length=60, blank=True,
        help_text='Documento que Odoo creó con este cierre, para poder buscarlo allá.')
    ultimo_error = models.CharField(
        max_length=300, blank=True,
        help_text='Por qué falló el último intento de enviarlo.')
    conflicto_odoo = models.BooleanField(
        default=False,
        help_text='True si Odoo lo rechazó a propósito. El motivo va en ultimo_error.')

    # La anulación lleva su propio estado: si el cierre ya se contabilizó,
    # deshacerlo en SIGHU no deshace el asiento. Hay que decírselo, y ese
    # aviso puede fallar por su cuenta.
    anulacion_sincronizada = models.BooleanField(default=False)
    fecha_sincronizacion_anulacion = models.DateTimeField(null=True, blank=True)
    ultimo_error_anulacion = models.CharField(max_length=300, blank=True)
    conflicto_odoo_anulacion = models.BooleanField(default=False)

    class Meta:
        db_table = 'transporte_cierres_gastos'
        verbose_name = 'Cierre de gastos'
        verbose_name_plural = 'Cierres de gastos'
        ordering = ['-fecha_cierre']
        constraints = [
            # El ámbito y el sujeto tienen que concordar: un cierre de
            # conductor sin conductor, o con vehículo además, no significa
            # nada y ensuciaría los totales.
            models.CheckConstraint(
                condition=(
                    models.Q(ambito='conductor',
                             conductor__isnull=False, vehiculo__isnull=True)
                    | models.Q(ambito='vehiculo',
                               vehiculo__isnull=False, conductor__isnull=True)
                ),
                name='cierre_ambito_coherente',
            ),
        ]
        indexes = [
            models.Index(fields=['ambito', '-fecha_cierre']),
            models.Index(fields=['conductor', '-fecha_cierre']),
            models.Index(fields=['vehiculo', '-fecha_cierre']),
            models.Index(fields=['sincronizado']),
        ]

    def __str__(self):
        return f'Cierre {self.get_ambito_display().lower()} {self.sujeto} — {self.fecha_cierre:%d/%m/%Y}'

    @property
    def sujeto(self):
        """De quién o de qué es la cuenta, para mostrarlo."""
        if self.ambito == self.CONDUCTOR and self.conductor_id:
            return self.conductor.nombre_completo
        if self.ambito == self.VEHICULO and self.vehiculo_id:
            return self.vehiculo.placa
        return '—'

    @property
    def esta_activo(self):
        return self.anulado_en is None

    @property
    def estado_contabilidad(self):
        """Dónde va el cierre camino a la contabilidad de Odoo.

        Cuatro situaciones que se tratan distinto, y por eso no alcanza un
        booleano: lo que está en cola se arregla solo, lo rechazado hay que
        ir a resolverlo, y un cierre anulado que ya se había contabilizado
        tiene un asiento allá esperando que alguien lo reverse.
        """
        if not self.esta_activo:
            if not self.sincronizado:
                return 'anulado_sin_enviar'
            return ('anulado_avisado' if self.anulacion_sincronizada
                    else 'anulado_por_avisar')
        if self.conflicto_odoo:
            return 'rechazado'
        return 'enviado' if self.sincronizado else 'en_cola'

    @property
    def estado_contabilidad_texto(self):
        return {
            'enviado': 'En la contabilidad de Odoo',
            'en_cola': 'En cola para Odoo',
            'rechazado': 'Odoo lo rechazó',
            'anulado_sin_enviar': 'Anulado, nunca llegó a Odoo',
            'anulado_por_avisar': 'Anulado, falta avisarle a Odoo',
            'anulado_avisado': 'Anulado y avisado a Odoo',
        }[self.estado_contabilidad]

    @property
    def pendiente_para_odoo(self):
        """¿Hay algo que todavía haya que mandarle a Odoo de este cierre?"""
        if self.esta_activo:
            return not self.sincronizado and not self.conflicto_odoo
        # Anulado: solo se avisa si alcanzó a enviarse. Un cierre que
        # nunca llegó no tiene nada que deshacer del otro lado.
        return (self.sincronizado and not self.anulacion_sincronizada
                and not self.conflicto_odoo_anulacion)

    def gastos(self):
        """Los gastos que quedaron sellados por este cierre."""
        campo = ('cierre_conductor' if self.ambito == self.CONDUCTOR
                 else 'cierre_vehiculo')
        return GastoVehiculo.objects.filter(**{campo: self}).select_related(
            'vehiculo', 'conductor', 'servicio')


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

    SIN_NOVEDAD = 'sin_novedad'
    ENTREGA_PARCIAL = 'entrega_parcial'
    DEVOLUCION = 'devolucion'
    RECHAZO = 'rechazo'
    NOVEDADES = [
        (SIN_NOVEDAD, 'Sin novedad'),
        (ENTREGA_PARCIAL, 'Entrega parcial'),
        (DEVOLUCION, 'Devolución'),
        (RECHAZO, 'El cliente la rechazó'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    odoo_modelo = models.CharField(
        max_length=80,
        help_text='Modelo del documento en Odoo (construinmuniza.flete).')
    odoo_id = models.PositiveIntegerField(
        help_text='Id del documento en Odoo.')
    ref = models.CharField(
        max_length=60, blank=True,
        help_text='Referencia legible del servicio, como la muestra Odoo.')

    # El viaje con el que salió, si el servicio iba con otros en la misma
    # salida del camión. Cada parada sigue siendo su propio registro —se
    # entrega y se cierra por separado, porque una puede tener devolución y
    # otra no—, pero salieron juntas, y deshacer la salida es deshacerla
    # para todas.
    viaje_odoo_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Id del viaje en Odoo, si el servicio salió en un viaje.')
    viaje_ref = models.CharField(
        max_length=60, blank=True,
        help_text='Número del viaje (VJE/...), para leerlo.')
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

    # Lo que pasó en la entrega. Una entrega parcial o una devolución mueve
    # inventario y hay que ajustarla en Odoo, así que si el conductor no lo
    # reporta nadie se entera hasta que reclama el cliente.
    novedad = models.CharField(
        max_length=20, choices=NOVEDADES, default=SIN_NOVEDAD,
        help_text='Qué pasó en la entrega.')
    observacion = models.TextField(
        blank=True,
        help_text='Obligatoria cuando hubo novedad: qué pasó exactamente.')

    # Soporte, no base de cobro: el valor lo calcula Odoo con su documento
    # y usa esto para contrastar.
    toneladas_entregadas = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Lo que el conductor dice que entregó. Opcional.')

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
    # Odoo respondió 409: lo rechazó a propósito. No se reintenta, porque
    # del otro lado cambió algo y repetir el aviso da siempre lo mismo.
    conflicto_odoo = models.BooleanField(
        default=False,
        help_text='True si Odoo rechazó la salida. El motivo va en ultimo_error.')

    # La entrega lleva su propio estado de aviso: salida y entrega son dos
    # hechos distintos y uno puede llegar a Odoo sin el otro.
    entrega_sincronizada = models.BooleanField(
        default=False,
        help_text='True cuando Odoo ya recibió el aviso de la entrega.')
    fecha_sincronizacion_entrega = models.DateTimeField(null=True, blank=True)
    ultimo_error_entrega = models.CharField(max_length=300, blank=True)
    conflicto_odoo_entrega = models.BooleanField(
        default=False,
        help_text='True si Odoo rechazó la entrega. El motivo va en ultimo_error_entrega.')

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
            models.Index(fields=['viaje_odoo_id']),
            models.Index(fields=['vehiculo', '-iniciado_en']),
            models.Index(fields=['conductor', '-iniciado_en']),
            models.Index(fields=['sincronizado']),
        ]

    def __str__(self):
        return f'{self.ref or self.odoo_id} — {self.vehiculo.placa} ({self.iniciado_en:%d/%m/%Y %H:%M})'

    def clean(self):
        errores = {}
        if self.entregado_en and self.entregado_en < self.iniciado_en:
            errores['entregado_en'] = 'La entrega no puede ser anterior a la salida.'
        if (self.entregado_en and self.novedad != self.SIN_NOVEDAD
                and not (self.observacion or '').strip()):
            errores['observacion'] = (
                'Si hubo novedad hay que decir qué pasó: de ahí sale el '
                'ajuste en Odoo.')
        if errores:
            raise ValidationError(errores)

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

        La excepción es cuando Odoo rechazó la salida: ahí la salida sobra,
        y obligar al conductor a dejarla porque pasaron 15 minutos sería
        quedarse con un registro que el propio Odoo ya desconoció.
        """
        if not self.esta_activo or self.sincronizado or self.esta_entregado:
            return False
        if self.conflicto_odoo:
            return True
        limite = self.fecha_creacion + timedelta(minutes=self.MINUTOS_PARA_DESHACER)
        return timezone.now() <= limite

    @property
    def puede_deshacer_entrega(self):
        """Mismo margen que la salida, por la misma razón: el dedo."""
        if not self.esta_activo or not self.esta_entregado:
            return False
        if self.entrega_sincronizada:
            return False
        if self.conflicto_odoo_entrega:
            return True
        limite = self.entregado_en + timedelta(minutes=self.MINUTOS_PARA_DESHACER)
        return timezone.now() <= limite

    @property
    def tuvo_novedad(self):
        return self.esta_entregado and self.novedad != self.SIN_NOVEDAD

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


class AvisoServicioAsignado(models.Model):
    """Constancia de que a un conductor ya se le avisó de un servicio.

    Los servicios se asignan en Odoo y Odoo no le avisa a SIGHU; SIGHU
    consulta cada pocos minutos y compara contra esta tabla. La llave es el
    servicio y la cédula del conductor que tiene en Odoo: si el coordinador
    se lo pasa a otro conductor, el nuevo recibe su aviso.

    También queda el renglón cuando no se avisó (`avisado=False`): el
    conductor no tiene usuario en SIGHU, o el servicio ya era viejo cuando
    se vio por primera vez. Así no se reintenta cada pocos minutos lo que
    no tiene a quién llegar.
    """
    odoo_id = models.PositiveIntegerField(
        help_text='Id del servicio (construinmuniza.flete) en Odoo.')
    cedula = models.CharField(
        max_length=20, help_text='Cédula del conductor asignado en Odoo.')
    empleado = models.ForeignKey(
        'employees.Empleado', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='avisos_servicio')
    viaje_odoo_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Id del viaje en Odoo, si el servicio va en uno.')
    ref = models.CharField(max_length=60, blank=True)
    avisado = models.BooleanField(
        default=True,
        help_text='False si se registró sin avisar (sin usuario, o ya era viejo).')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transporte_avisos_servicio_asignado'
        verbose_name = 'Aviso de servicio asignado'
        verbose_name_plural = 'Avisos de servicios asignados'
        ordering = ['-fecha_creacion']
        constraints = [
            models.UniqueConstraint(fields=['odoo_id', 'cedula'],
                                    name='aviso_servicio_una_vez_por_conductor'),
        ]
        indexes = [models.Index(fields=['viaje_odoo_id', 'cedula'])]

    def __str__(self):
        return f'{self.ref or self.odoo_id} → {self.cedula}'
