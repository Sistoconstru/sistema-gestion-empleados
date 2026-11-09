"""Borra las copias que dejó el doble scheduler.

Durante meses hubo dos planificadores corriendo a la vez (uno en start.sh y
otro dentro de Gunicorn), así que cada aviso automático se creaba dos veces.
La causa está corregida; esto limpia lo que quedó.

Se conserva siempre la primera de cada grupo: la que el usuario vio y pudo
haber marcado como leída. Dos notificaciones cuentan como la misma si
coinciden usuario, tipo, título y mensaje, y se crearon con pocos segundos
de diferencia — el margen evita borrar un aviso legítimo que se repita
semanas después, como el recordatorio mensual de la cuota SENA.
"""
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.notifications.models import Notificacion

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ('Elimina notificaciones duplicadas creadas por el doble '
            'scheduler, conservando la primera de cada grupo.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--segundos',
            type=int,
            default=120,
            help=('Margen para considerar dos avisos la misma entrega '
                  '(por defecto 120 segundos)'),
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se borraría sin borrar nada',
        )

    def handle(self, **options):
        margen = options['segundos']
        dry_run = options['dry_run']

        total = Notificacion.objects.count()
        self.stdout.write(f'Notificaciones en la base: {total}')
        self.stdout.write(f'Margen de agrupación: {margen} segundos\n')

        # Se recorre ordenado por clave y fecha para detectar las ráfagas sin
        # cargar comparaciones cruzadas: dentro de cada clave, una copia es la
        # que llega a menos de `margen` de la anterior conservada.
        campos = ('id', 'usuario_id', 'tipo_notificacion_id', 'titulo',
                  'mensaje', 'fecha_creacion', 'leida')
        filas = (Notificacion.objects.order_by(
            'usuario_id', 'tipo_notificacion_id', 'titulo', 'mensaje',
            'fecha_creacion').values(*campos))

        a_borrar = []
        por_tipo = defaultdict(int)
        leidas_borradas = 0
        clave_anterior = None
        referencia = None

        for f in filas.iterator(chunk_size=2000):
            clave = (f['usuario_id'], f['tipo_notificacion_id'],
                     f['titulo'], f['mensaje'])
            if clave != clave_anterior:
                clave_anterior = clave
                referencia = f['fecha_creacion']
                continue

            if (f['fecha_creacion'] - referencia).total_seconds() <= margen:
                a_borrar.append(f['id'])
                por_tipo[f['tipo_notificacion_id']] += 1
                if f['leida']:
                    leidas_borradas += 1
            else:
                # Entrega legítima posterior: pasa a ser la nueva referencia.
                referencia = f['fecha_creacion']

        self.stdout.write(f'Copias a eliminar: {len(a_borrar)}')
        if not a_borrar:
            self.stdout.write(self.style.SUCCESS('No hay duplicados.'))
            return

        self.stdout.write(f'   de ellas ya leídas: {leidas_borradas}')
        self.stdout.write(f'   quedarían: {total - len(a_borrar)}\n')

        from apps.notifications.models import TipoNotificacion
        nombres = dict(TipoNotificacion.objects.values_list('id', 'codigo'))
        self.stdout.write('Por tipo de notificación:')
        for tipo_id, n in sorted(por_tipo.items(), key=lambda x: -x[1]):
            self.stdout.write(f'   {str(nombres.get(tipo_id, tipo_id)):28} {n:>5}')

        if dry_run:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.WARNING(
                f'DRY RUN: se eliminarían {len(a_borrar)} notificaciones. '
                f'No se borró nada.'
            ))
            return

        borradas = 0
        with transaction.atomic():
            # En lotes: un IN con miles de UUID es pesado para el planificador.
            for i in range(0, len(a_borrar), 500):
                lote = a_borrar[i:i + 500]
                n, _ = Notificacion.objects.filter(id__in=lote).delete()
                borradas += n

        logger.info('Eliminadas %s notificaciones duplicadas (margen %ss).',
                    borradas, margen)

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'Eliminadas {borradas} notificaciones duplicadas.'
        ))
        self.stdout.write(f'Quedan {Notificacion.objects.count()}.')
