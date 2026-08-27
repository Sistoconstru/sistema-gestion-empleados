"""Modelos del módulo de sorteos.

Un Sorteo agrupa N premios idénticos (ej: "5 celulares usados"). Los
empleados se autoinscriben (nunca por terceros) y reciben un número
correlativo empezando en 1. El admin, al momento del sorteo, ingresa
el número ganador extraído por tómbola externa; el sistema resuelve la
persona y registra el GanadorSorteo. Se puede repetir hasta agotar los
premios (`cantidad_premios`).
"""
import uuid
from django.db import models
from django.conf import settings


class Sorteo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=30, unique=True,
        help_text='Identificador corto, p. ej. SORTEO-CEL-2026.')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='sorteos/', null=True, blank=True,
        help_text='Foto del/los premios (celulares, computadores…).')
    cantidad_premios = models.PositiveIntegerField(default=1,
        help_text='Cuántas veces se puede sortear (nº de premios idénticos).')
    encuesta_requisito = models.ForeignKey(
        'surveys.Encuesta', on_delete=models.PROTECT,
        related_name='sorteos_que_la_requieren',
        help_text='El empleado debe haber COMPLETADO esta encuesta para inscribirse.',
    )
    require_pwa = models.BooleanField(default=True,
        help_text='Exige tener SIGHU instalada como PWA (o suscripción push activa).')
    fecha_inicio_inscripcion = models.DateField()
    fecha_fin_inscripcion = models.DateField()
    fecha_sorteo = models.DateField()
    activo = models.BooleanField(default=True,
        help_text='Los sorteos ya realizados se apagan aquí para archivarlos.')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sorteos_creados',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sorteos'
        verbose_name = 'Sorteo'
        verbose_name_plural = 'Sorteos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.codigo} · {self.nombre}'

    @property
    def total_inscritos(self):
        return self.inscripciones.count()

    @property
    def total_ganadores(self):
        return self.ganadores.count()

    @property
    def premios_restantes(self):
        return max(0, self.cantidad_premios - self.total_ganadores)

    @property
    def sorteo_completado(self):
        return self.total_ganadores >= self.cantidad_premios

    def inscripciones_abiertas(self, hoy):
        return (self.activo
                and self.fecha_inicio_inscripcion <= hoy <= self.fecha_fin_inscripcion
                and not self.sorteo_completado)


class InscripcionSorteo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sorteo = models.ForeignKey(Sorteo, on_delete=models.CASCADE, related_name='inscripciones')
    empleado = models.ForeignKey(
        'employees.Empleado', on_delete=models.CASCADE, related_name='inscripciones_sorteo',
    )
    numero = models.PositiveIntegerField(
        help_text='Número correlativo dentro del sorteo, empieza en 1.')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sorteos_inscripcion'
        verbose_name = 'Inscripción de sorteo'
        verbose_name_plural = 'Inscripciones de sorteo'
        unique_together = [('sorteo', 'empleado'), ('sorteo', 'numero')]
        ordering = ['sorteo', 'numero']

    def __str__(self):
        return f'#{self.numero} — {self.empleado} en {self.sorteo.codigo}'


class GanadorSorteo(models.Model):
    """Registro de un premio entregado a una inscripción del sorteo."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sorteo = models.ForeignKey(Sorteo, on_delete=models.CASCADE, related_name='ganadores')
    inscripcion = models.OneToOneField(
        InscripcionSorteo, on_delete=models.CASCADE, related_name='ganador',
    )
    orden_premio = models.PositiveIntegerField(
        help_text='1er premio extraído, 2do, ...')
    fecha_seleccion = models.DateTimeField(auto_now_add=True)
    seleccionado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='premios_sorteo_seleccionados',
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = 'sorteos_ganador'
        verbose_name = 'Ganador de sorteo'
        verbose_name_plural = 'Ganadores de sorteo'
        unique_together = [('sorteo', 'orden_premio')]
        ordering = ['sorteo', 'orden_premio']

    def __str__(self):
        return f'{self.sorteo.codigo} · Premio {self.orden_premio} → #{self.inscripcion.numero}'
