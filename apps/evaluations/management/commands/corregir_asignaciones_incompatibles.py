"""
Corrige asignaciones de evaluación incompatibles con el estado del empleado.

Caso objetivo: empleados ACTUALMENTE en periodo de prueba (estado 'p-prue')
que tienen asignada una evaluación que NO es de tipo PERIODO_PRUEBA
(p. ej. evaluación de desempeño / anual).

Por defecto solo LISTA (dry-run). Borra únicamente con --apply, y solo las
asignaciones "vacías" (estado pendiente/en_progreso sin avance). Las que ya
tienen respuestas, resultado o plan de mejora se reportan para revisión manual
y nunca se borran automáticamente.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.evaluations.models import (
    AsignacionEvaluacion,
    RespuestaEvaluacion,
    ResultadoEvaluacion,
    PlanMejoraPredefinido,
)

ESTADO_PRUEBA = 'p-prue'
TIPO_PRUEBA = 'PERIODO_PRUEBA'
ESTADOS_VACIA = ('pendiente', 'en_progreso')


class Command(BaseCommand):
    help = (
        'Detecta y corrige asignaciones de evaluación de desempeño asignadas '
        'a empleados en periodo de prueba. Dry-run por defecto; usa --apply para borrar.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Borra realmente las asignaciones vacías. Sin esta bandera solo lista.',
        )

    def _tiene_avance(self, asig):
        """Una asignación tiene avance si no se puede considerar 'vacía'."""
        if asig.estado not in ESTADOS_VACIA:
            return True
        if asig.porcentaje_completado and asig.porcentaje_completado > 0:
            return True
        if RespuestaEvaluacion.objects.filter(asignacion=asig).exists():
            return True
        if ResultadoEvaluacion.objects.filter(asignacion=asig).exists():
            return True
        if PlanMejoraPredefinido.objects.filter(asignacion_evaluacion=asig).exists():
            return True
        return False

    def handle(self, *args, **options):
        aplicar = options['apply']

        incompatibles = AsignacionEvaluacion.objects.filter(
            empleado_evaluado__estado__codigo=ESTADO_PRUEBA
        ).exclude(
            evaluacion__tipo_evaluacion__codigo=TIPO_PRUEBA
        ).select_related(
            'empleado_evaluado',
            'empleado_evaluado__estado',
            'evaluacion',
            'evaluacion__tipo_evaluacion',
        ).order_by('empleado_evaluado__apellidos', 'empleado_evaluado__nombres')

        modo = 'APLICAR (se borrarán las vacías)' if aplicar else 'DRY-RUN (solo lista)'
        self.stdout.write('=' * 90)
        self.stdout.write(self.style.WARNING(
            f'CORRECCIÓN DE ASIGNACIONES INCOMPATIBLES — empleados en prueba con eval. de desempeño'
        ))
        self.stdout.write(f'Modo: {modo}')
        self.stdout.write('=' * 90)

        if not incompatibles.exists():
            self.stdout.write(self.style.SUCCESS('\nNo se encontraron asignaciones incompatibles. Nada que corregir.'))
            return

        vacias = []
        con_avance = []
        for asig in incompatibles:
            (con_avance if self._tiene_avance(asig) else vacias).append(asig)

        # --- Vacías (candidatas a borrado) ---
        self.stdout.write(self.style.WARNING(
            f'\n[VACÍAS] {len(vacias)} asignación(es) sin avance (pendiente/en_progreso) — candidatas a borrado:'
        ))
        for asig in vacias:
            self.stdout.write(
                f'  - {asig.empleado_evaluado.nombre_completo} | '
                f'{asig.evaluacion.nombre} ({asig.evaluacion.tipo_evaluacion.codigo}) | '
                f'estado={asig.estado} | periodo={asig.periodo_evaluacion} | id={asig.id}'
            )

        # --- Con avance (revisión manual) ---
        self.stdout.write(self.style.ERROR(
            f'\n[CON AVANCE] {len(con_avance)} asignación(es) con respuestas/resultado/plan — '
            f'NO se borran, requieren revisión manual:'
        ))
        for asig in con_avance:
            self.stdout.write(
                f'  - {asig.empleado_evaluado.nombre_completo} | '
                f'{asig.evaluacion.nombre} ({asig.evaluacion.tipo_evaluacion.codigo}) | '
                f'estado={asig.estado} | %={asig.porcentaje_completado} | id={asig.id}'
            )

        self.stdout.write('\n' + '-' * 90)
        self.stdout.write(
            f'Resumen: {len(vacias)} vacías | {len(con_avance)} con avance | '
            f'{incompatibles.count()} incompatibles en total'
        )

        if not aplicar:
            self.stdout.write(self.style.WARNING(
                '\nDRY-RUN: no se borró nada. Vuelve a ejecutar con --apply para borrar las vacías.'
            ))
            return

        if not vacias:
            self.stdout.write(self.style.SUCCESS('\nNo hay asignaciones vacías para borrar.'))
            return

        ids_vacias = [a.id for a in vacias]
        with transaction.atomic():
            borradas, _ = AsignacionEvaluacion.objects.filter(id__in=ids_vacias).delete()
        self.stdout.write(self.style.SUCCESS(
            f'\n[OK] APLICADO: {len(ids_vacias)} asignación(es) vacía(s) borrada(s) '
            f'({borradas} objeto(s) afectado(s) en cascada).'
        ))
        if con_avance:
            self.stdout.write(self.style.WARNING(
                f'  Quedan {len(con_avance)} con avance para revisar manualmente (ver lista arriba).'
            ))
