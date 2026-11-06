"""Cierra sin calificar los seguimientos bimensuales demasiado vencidos.

Un plan de mejora pierde sentido si nadie lo siguió a tiempo: pedirle al
supervisor que registre hoy el avance de un bimestre que vencía hace nueve
meses no produce un dato real, solo uno inventado. A partir del umbral el
sistema lo cierra sin calificación y deja constancia de que lo cerró él,
para que el plan pueda avanzar hasta su evaluación final con los bimestres
que sí se alcanzaron a diligenciar.
"""
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.evaluations.models import SeguimientoBimensual

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ('Cierra sin calificación los seguimientos bimensuales que llevan '
            'más de N meses vencidos (por defecto 6).')

    def add_arguments(self, parser):
        parser.add_argument(
            '--meses',
            type=int,
            default=6,
            help='Meses de vencimiento a partir de los cuales se cierra (por defecto 6)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se cerraría sin guardar nada',
        )

    def handle(self, **options):
        meses = options['meses']
        dry_run = options['dry_run']

        hoy = timezone.now().date()
        corte = hoy - relativedelta(months=meses)

        candidatos = SeguimientoBimensual.objects.filter(
            estado__in=['pendiente', 'atrasado'],
            fecha_limite__lt=corte,
        ).select_related(
            'plan_mejora__asignacion_evaluacion__empleado_evaluado',
            'plan_mejora__asignacion_evaluacion__evaluador',
        ).order_by('fecha_limite')

        total = candidatos.count()
        self.stdout.write(
            f'Fecha de corte: {corte} (más de {meses} meses vencidos)'
        )
        self.stdout.write(f'Seguimientos a cerrar: {total}\n')

        if not total:
            self.stdout.write(self.style.SUCCESS('No hay nada que cerrar.'))
            return

        planes_afectados = set()
        for s in candidatos:
            asignacion = s.plan_mejora.asignacion_evaluacion
            empleado = asignacion.empleado_evaluado
            evaluador = asignacion.evaluador
            dias = (hoy - s.fecha_limite).days
            planes_afectados.add(s.plan_mejora_id)

            self.stdout.write(
                f'  bim {s.numero_bimestre}  {empleado.nombre_completo[:30]:32} '
                f'evaluador={(evaluador.nombre_completo[:22] if evaluador else "NINGUNO"):24} '
                f'vencio={s.fecha_limite} ({dias} días)'
            )

        if dry_run:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.WARNING(
                f'DRY RUN: se cerrarían {total} seguimientos de '
                f'{len(planes_afectados)} planes. No se guardó nada.'
            ))
            return

        ahora = timezone.now()
        with transaction.atomic():
            cerrados = 0
            for s in candidatos:
                dias = (hoy - s.fecha_limite).days
                s.estado = 'cerrado_sistema'
                # Sin calificación: no es ni satisfactorio ni insatisfactorio,
                # simplemente no se midió a tiempo.
                s.avance_satisfactorio = None
                s.fecha_completado = ahora
                s.completado_por = None
                s.observaciones = (
                    f'Cerrado automáticamente por el sistema el '
                    f'{hoy:%d/%m/%Y}: el seguimiento llevaba {dias} días '
                    f'vencido (más de {meses} meses). Se cierra sin '
                    f'calificación y no se tiene en cuenta para la '
                    f'evaluación final.'
                )
                s.save(update_fields=[
                    'estado', 'avance_satisfactorio', 'fecha_completado',
                    'completado_por', 'observaciones',
                ])
                cerrados += 1

        logger.info(
            'Cerrados %s seguimientos bimensuales con más de %s meses de '
            'vencimiento, en %s planes de mejora.',
            cerrados, meses, len(planes_afectados)
        )

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'Cerrados {cerrados} seguimientos de {len(planes_afectados)} planes.'
        ))
        self.stdout.write(
            'Los bimestres que aún no llegan al umbral siguen pendientes y '
            'ya no quedan bloqueados por los cerrados.'
        )
