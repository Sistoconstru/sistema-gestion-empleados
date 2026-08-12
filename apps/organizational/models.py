from django.db import models

# =============================================================================
# apps/organizational/models.py
# =============================================================================

from django.db import models

class Sede(models.Model):
    """Modelo para sedes de la empresa"""
    codigo = models.CharField(max_length=10, unique=True)  # Código único de la sede
    nombre = models.CharField(max_length=100)  # Nombre de la sede
    direccion = models.TextField()  # Dirección física
    ciudad = models.CharField(max_length=50)  # Ciudad donde está ubicada
    departamento = models.CharField(max_length=50)  # Departamento
    telefono = models.CharField(max_length=15)  # Teléfono de contacto
    activa = models.BooleanField(default=True)  # Estado activo/inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    
    class Meta:
        db_table = 'sedes'
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class AreaEmpresa(models.Model):
    """Modelo para áreas de la empresa"""
    codigo = models.CharField(max_length=20, unique=True)  # Código único del área
    nombre = models.CharField(max_length=100, unique=True)  # Nombre del área
    descripcion = models.TextField(blank=True)  # Descripción opcional
    area_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # Área superior (jerarquía)
    responsable = models.ForeignKey('employees.Empleado', on_delete=models.SET_NULL, null=True, blank=True)  # Empleado responsable
    activa = models.BooleanField(default=True)  # Estado activo/inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    
    class Meta:
        db_table = 'areas_empresa'
        verbose_name = 'Área de Empresa'
        verbose_name_plural = 'Áreas de Empresa'
    
    def __str__(self):
        return self.nombre

class Cargo(models.Model):
    """Modelo para cargos dentro de la empresa"""
    codigo = models.CharField(max_length=20, unique=True)  # Código único del cargo
    nombre = models.CharField(max_length=100)  # Nombre del cargo
    descripcion = models.TextField(blank=True)  # Descripción opcional
    area = models.ForeignKey(AreaEmpresa, on_delete=models.CASCADE)  # Área a la que pertenece el cargo
    cargo_jefe = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  # Cargo jefe (jerarquía)
    nivel_jerarquico = models.IntegerField(default=1)  # Nivel jerárquico
    salario_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Salario mínimo
    salario_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Salario máximo
    requiere_licencia_conducir = models.BooleanField(default=False)  # Si requiere licencia de conducir
    requiere_certificado_alturas = models.BooleanField(default=False)  # Si requiere certificado de alturas
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    
    # NUEVO CAMPO: Rol automático
    rol_automatico = models.ForeignKey(
        'authentication.Rol',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Rol del Sistema",
        help_text="Rol que se asigna automáticamente a empleados con este cargo"
    )

    crea_usuario_sistema = models.BooleanField(
        default=True,
        verbose_name="¿Crea usuario en el sistema?",
        help_text=(
            "Si está marcado, al asignar este cargo a un empleado nuevo se crea su usuario "
            "automáticamente. Desmarca para cargos sin acceso al sistema (ej: aprendiz en "
            "etapa lectiva). El usuario se creará cuando el empleado pase a un cargo que sí "
            "lo permita."
        ),
    )

    es_cargo_aprendiz = models.BooleanField(
        default=False,
        verbose_name="¿Es cargo de aprendiz SENA?",
        help_text=(
            "Marca este cargo si corresponde a un aprendiz del SENA (etapa lectiva o "
            "productiva). Los empleados con este cargo cuentan para la cuota de aprendices "
            "definida en la resolución vigente del SENA."
        ),
    )

    class Meta:
        db_table = 'cargos'
        unique_together = ['nombre', 'area']
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
    
    def __str__(self):
        rol_info = f" → {self.rol_automatico.nombre}" if self.rol_automatico else ""
        return f"{self.nombre} - {self.area.nombre}{rol_info}"


class CentroCosto(models.Model):
    """Centros de costo para asignación contable de empleados.

    La sede operativa de cada empleado se obtiene desde Empleado.sede; el centro
    de costo es un catálogo independiente, no se ata a una sede.
    """
    cuenta_analitica = models.CharField(max_length=100, unique=True, help_text="Etiqueta Odoo: [CODE] NOMBRE")
    referencia = models.CharField(max_length=30, blank=True, help_text="Código corto de referencia (ej: 1001)")
    nombre = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'centros_costo'
        verbose_name = 'Centro de Costo'
        verbose_name_plural = 'Centros de Costo'
        ordering = ['referencia']

    def __str__(self):
        return self.cuenta_analitica


class ResolucionSena(models.Model):
    """Resolución del SENA que fija la cuota de aprendices para la empresa.

    Ley 789 de 2002 (Colombia): las empresas con >=15 trabajadores tienen cuota
    obligatoria de aprendices SENA. La cuota efectiva la define la resolución
    que emite la Regional del SENA (típicamente 1 por cada 20 trabajadores),
    no el conteo automático. Este modelo guarda esa resolución como fuente
    autoritativa. Múltiples resoluciones se archivan; la que cubre "hoy" con
    su ventana de vigencia es la que rige.
    """
    numero = models.CharField(
        max_length=60,
        help_text="Número de resolución (ej: 1-0001-2026-0007890)",
    )
    fecha_expedicion = models.DateField(
        help_text="Fecha en que el SENA expidió la resolución.",
    )
    fecha_vigencia_inicio = models.DateField(
        help_text="Inicio de vigencia de esta cuota.",
    )
    fecha_vigencia_fin = models.DateField(
        null=True, blank=True,
        help_text="Fin de vigencia. Dejar vacío si aún no se conoce (se aplica hasta que llegue una nueva).",
    )
    cuota_aprendices = models.PositiveIntegerField(
        help_text="Cantidad total de aprendices que la empresa debe mantener según la resolución.",
    )
    total_trabajadores_base = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Total de trabajadores que consideró el SENA al calcular la cuota (informativo).",
    )
    archivo_pdf = models.FileField(
        upload_to='resoluciones_sena/',
        null=True, blank=True,
        help_text="PDF oficial de la resolución (opcional pero recomendado).",
    )
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resoluciones_sena_creadas',
    )

    class Meta:
        db_table = 'resoluciones_sena'
        verbose_name = 'Resolución SENA'
        verbose_name_plural = 'Resoluciones SENA'
        ordering = ['-fecha_vigencia_inicio', '-fecha_expedicion']
        indexes = [
            models.Index(fields=['-fecha_vigencia_inicio']),
        ]

    def __str__(self):
        return f'Res. {self.numero} — cuota {self.cuota_aprendices} (desde {self.fecha_vigencia_inicio})'

    @classmethod
    def vigente(cls, fecha=None):
        """Retorna la resolución vigente en la fecha dada (por defecto: hoy).

        La vigente es la que tiene fecha_vigencia_inicio <= fecha y
        (fecha_vigencia_fin es null O fecha_vigencia_fin >= fecha). Si hay
        varias que cumplan (traslape mal registrado), gana la de inicio más
        reciente.
        """
        from datetime import date as _date
        from django.db.models import Q
        f = fecha or _date.today()
        return (
            cls.objects
            .filter(fecha_vigencia_inicio__lte=f)
            .filter(Q(fecha_vigencia_fin__isnull=True) | Q(fecha_vigencia_fin__gte=f))
            .order_by('-fecha_vigencia_inicio')
            .first()
        )


class SalarioMinimoAnual(models.Model):
    """Salario mínimo mensual legal vigente (SMMLV) por año en Colombia.

    Cada enero el gobierno emite un decreto con el nuevo SMMLV; RRHH lo
    registra aquí. La app lo consume para cualquier cálculo legal (sanción
    SENA, prestaciones, etc.) via `vigente()`.

    Si el año en curso no está registrado, `vigente()` devuelve el más
    reciente conocido — así el sistema no se queda sin valor mientras
    RRHH actualiza. Un cron avisa cuando llega enero sin actualización.
    """
    year = models.PositiveSmallIntegerField(
        unique=True,
        help_text='Año al que aplica este SMMLV (ej: 2026).',
    )
    valor = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text='Valor mensual del SMMLV en pesos (ej: 1423500.00 para 2026).',
    )
    decreto = models.CharField(
        max_length=60, blank=True,
        help_text='Número de decreto/norma que lo fija (ej: Decreto 1435 de 2025).',
    )
    fecha_expedicion = models.DateField(
        null=True, blank=True,
        help_text='Fecha del decreto (opcional).',
    )
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='smmlv_actualizados',
    )

    class Meta:
        db_table = 'salario_minimo_anual'
        verbose_name = 'Salario mínimo anual (SMMLV)'
        verbose_name_plural = 'Salarios mínimos anuales (SMMLV)'
        ordering = ['-year']

    def __str__(self):
        return f'SMMLV {self.year}: ${self.valor:,.0f}'

    @classmethod
    def valor_vigente(cls, year=None):
        """Retorna el valor SMMLV para el año dado (por defecto: actual).

        Si el año exacto no está en la BD, devuelve el más reciente registrado.
        Si no hay ninguno, devuelve None — el llamador decide qué hacer.
        """
        from datetime import date as _date
        target = year or _date.today().year
        row = cls.objects.filter(year=target).first()
        if row is None:
            row = cls.objects.order_by('-year').first()
        return row.valor if row else None

    @classmethod
    def esta_actualizado(cls):
        """True si el SMMLV del año actual está registrado en la BD."""
        from datetime import date as _date
        return cls.objects.filter(year=_date.today().year).exists()


class SeguimientoReemplazosSena(models.Model):
    """Estado momentáneo del proceso de conseguir aprendices para reemplazar
    a los que están próximos a terminar (contratos con ≤30 días restantes).

    Diseño singleton: mantiene UN solo registro global. RRHH actualiza el
    contador `conseguidos` a medida que va identificando candidatos; el
    resto (cantidad requerida, faltantes) se calcula dinámicamente
    comparando contra los aprendices reales próximos a vencer.
    """
    conseguidos = models.PositiveIntegerField(
        default=0,
        help_text='Cantidad de aprendices candidatos ya identificados/en proceso de contratación.',
    )
    notas = models.TextField(
        blank=True,
        help_text='Notas internas (nombres candidatos, estatus con SENA, etc.).',
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reemplazos_sena_actualizados',
    )

    class Meta:
        db_table = 'seguimiento_reemplazos_sena'
        verbose_name = 'Seguimiento reemplazos SENA'
        verbose_name_plural = 'Seguimientos reemplazos SENA'

    def __str__(self):
        return f'Conseguidos {self.conseguidos} (actualizado {self.fecha_actualizacion:%d/%m/%Y})'

    @classmethod
    def instancia(cls):
        """Devuelve el registro único, creándolo si no existe."""
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'conseguidos': 0})
        return obj
