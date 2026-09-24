"""Elimina novedades duplicadas por (empleado, fecha, tipo, hora_inicio, hora_fin, total_horas).

Los duplicados vienen de:
- Double-submit del modal (dos filas creadas con delta <1s).
- Re-carga humana días después (coordinador olvida que ya cargó el turno).
- Re-envío tras error de captura (mismo turno, motivo/observaciones distintos).

Estrategia:
- Agrupa por (empleado_id, fecha, tipo, hora_inicio, hora_fin, total_horas).
- Conserva la más antigua por `fecha_creacion` (o menor `pk` si empatan).
- Elimina el resto.
- Si observaciones/motivo difieren entre las duplicadas, muestra ambas para
  que el operador decida antes de correr --apply.

Modo:
- Sin flags → dry-run (default).
- --apply → aplica en una transacción atómica.
- --limit N → procesa solo los primeros N grupos (pruebas).
- --desde YYYY-MM-DD / --hasta YYYY-MM-DD → filtra rango.
"""
from collections import defaultdict
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.employees.models import NovedadNomina


class Command(BaseCommand):
    help = 'Elimina novedades de nómina duplicadas conservando la más antigua.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true',
                            help='Aplica las eliminaciones. Sin este flag es dry-run.')
        parser.add_argument('--limit', type=int, default=None,
                            help='Procesa solo los primeros N grupos duplicados.')
        parser.add_argument('--desde', type=str, default=None,
                            help='Fecha desde (YYYY-MM-DD).')
        parser.add_argument('--hasta', type=str, default=None,
                            help='Fecha hasta (YYYY-MM-DD).')

    def handle(self, *args, **options):
        apply = options['apply']
        limit = options['limit']
        desde = options.get('desde')
        hasta = options.get('hasta')

        qs = NovedadNomina.objects.all()
        if desde:
            qs = qs.filter(fecha__gte=date.fromisoformat(desde))
        if hasta:
            qs = qs.filter(fecha__lte=date.fromisoformat(hasta))
        qs = qs.select_related('empleado', 'creado_por').order_by('fecha', 'pk')

        # Agrupar por tupla identificadora
        grupos = defaultdict(list)
        for n in qs:
            k = (n.empleado_id, n.fecha, n.tipo,
                 n.hora_inicio, n.hora_fin, n.total_horas)
            grupos[k].append(n)

        dup_grupos = [(k, v) for k, v in grupos.items() if len(v) > 1]
        self.stdout.write(f'Grupos con duplicación: {len(dup_grupos)}')
        self.stdout.write(f'Total registros involucrados: '
                          f'{sum(len(v) for _, v in dup_grupos)}')
        self.stdout.write(f'Registros a eliminar: '
                          f'{sum(len(v) - 1 for _, v in dup_grupos)}')

        if limit:
            dup_grupos = dup_grupos[:limit]
            self.stdout.write(f'Procesando solo los primeros {limit} grupos.')

        eliminaciones = []  # [(pk_conservar, [pks_a_eliminar], grupo)]
        con_motivo_diferente = 0
        for k, novs in dup_grupos:
            # Ordenar: la más antigua primero (fecha_creacion, luego pk)
            novs_ord = sorted(novs, key=lambda n: (
                getattr(n, 'fecha_creacion', None) or n.pk, n.pk,
            ))

            motivos = {(n.motivo or '').strip() for n in novs_ord}
            if len(motivos) > 1:
                # Motivo distinto → conservar la MÁS RECIENTE (asumimos que
                # la segunda carga es una corrección con más detalle).
                con_motivo_diferente += 1
                conservar = novs_ord[-1]
                eliminar = novs_ord[:-1]
            else:
                # Motivos idénticos → conservar la más antigua.
                conservar = novs_ord[0]
                eliminar = novs_ord[1:]

            eliminaciones.append((conservar, eliminar, novs_ord))

        self.stdout.write(f'Grupos con motivos distintos entre duplicadas: '
                          f'{con_motivo_diferente} '
                          f'(revisar cuál conservar antes de --apply)')

        self.stdout.write('\n--- Detalle ---')
        for conservar, eliminar, novs_ord in eliminaciones:
            emp = conservar.empleado
            self.stdout.write(
                f'\n{emp.nombre_completo}  {conservar.fecha}  '
                f'{conservar.hora_inicio}-{conservar.hora_fin}  '
                f'{conservar.total_horas}h  [{conservar.tipo}]'
            )
            for i, n in enumerate(novs_ord):
                accion = 'CONSERVAR' if n.pk == conservar.pk else 'ELIMINAR'
                fc = getattr(n, 'fecha_creacion', None) or '?'
                self.stdout.write(
                    f'  [{accion}] pk={n.pk}  creado={fc}  '
                    f'motivo="{(n.motivo or "")[:40]}"  '
                    f'obs="{(n.observaciones or "")[:60]}"'
                )

        if not apply:
            self.stdout.write(self.style.WARNING(
                '\n*** DRY-RUN — no se modificó nada. Corre con --apply. ***'
            ))
            return

        self.stdout.write('\nAplicando eliminaciones...')
        eliminados = 0
        with transaction.atomic():
            for conservar, eliminar, _ in eliminaciones:
                for n in eliminar:
                    n.delete()
                    eliminados += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Aplicado. Registros eliminados: {eliminados}.'
        ))
