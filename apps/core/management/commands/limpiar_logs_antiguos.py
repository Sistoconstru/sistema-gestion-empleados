# =============================================================================
# apps/core/management/commands/limpiar_logs_antiguos.py
# Command para limpiar logs de auditoría mayores a 2 años
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.core.models import LogActividad
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Elimina logs de auditoría mayores a 2 años automáticamente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=730,  # 2 años por defecto
            help='Número de días de retención (default: 730 = 2 años)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la eliminación sin borrar realmente',
        )

    def handle(self, *args, **options):
        dias_retencion = options['dias']
        dry_run = options['dry_run']

        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS('LIMPIEZA DE LOGS DE AUDITORÍA'))
        self.stdout.write('='*70)

        # Calcular fecha límite
        fecha_limite = timezone.now() - timedelta(days=dias_retencion)

        self.stdout.write(f'\nParámetros:')
        self.stdout.write(f'  - Días de retención: {dias_retencion} días ({dias_retencion/365:.1f} años)')
        self.stdout.write(f'  - Fecha límite: {fecha_limite.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'  - Modo: {"SIMULACIÓN (dry-run)" if dry_run else "ELIMINACIÓN REAL"}')

        # Contar logs a eliminar
        logs_antiguos = LogActividad.objects.filter(fecha_accion__lt=fecha_limite)
        total_a_eliminar = logs_antiguos.count()

        # Contar total de logs
        total_logs = LogActividad.objects.count()

        self.stdout.write(f'\nEstadísticas:')
        self.stdout.write(f'  - Total de logs en BD: {total_logs:,}')
        self.stdout.write(f'  - Logs a eliminar: {total_a_eliminar:,}')
        self.stdout.write(f'  - Logs que permanecerán: {total_logs - total_a_eliminar:,}')

        if total_a_eliminar == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ No hay logs antiguos para eliminar'))
            self.stdout.write('='*70)
            return

        # Mostrar desglose por modelo
        self.stdout.write(f'\nDesglose por modelo:')
        modelos_stats = logs_antiguos.values('modelo').annotate(
            total=__import__('django.db.models', fromlist=['Count']).Count('id')
        ).order_by('-total')

        for stat in modelos_stats[:10]:  # Mostrar top 10
            modelo = stat['modelo'] or 'Sin modelo'
            total = stat['total']
            self.stdout.write(f'  - {modelo}: {total:,} logs')

        if modelos_stats.count() > 10:
            self.stdout.write(f'  ... y {modelos_stats.count() - 10} modelos más')

        # Confirmación si no es dry-run
        if not dry_run:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Se eliminarán {total_a_eliminar:,} logs'))

            # Eliminar logs antiguos
            try:
                self.stdout.write('\nEliminando logs antiguos...')
                eliminados, _ = logs_antiguos.delete()

                self.stdout.write(self.style.SUCCESS(f'\n✓ Eliminados {eliminados:,} logs correctamente'))
                logger.info(f'Limpieza de logs: {eliminados} logs eliminados (mayores a {dias_retencion} días)')

                # Estadísticas finales
                total_restante = LogActividad.objects.count()
                self.stdout.write(f'\nEstadísticas finales:')
                self.stdout.write(f'  - Logs eliminados: {eliminados:,}')
                self.stdout.write(f'  - Logs restantes: {total_restante:,}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n✗ Error al eliminar logs: {e}'))
                logger.error(f'Error en limpieza de logs: {e}', exc_info=True)
                return

        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  SIMULACIÓN: Se eliminarían {total_a_eliminar:,} logs'))
            self.stdout.write('\nPara eliminar realmente, ejecuta el comando sin --dry-run')

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✓ Proceso completado'))
        self.stdout.write('='*70)
