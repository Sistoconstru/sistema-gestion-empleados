"""Elimina notificaciones antiguas para evitar acumulación indefinida.

Reglas:
- Notificaciones LEÍDAS: se eliminan si `fecha_leida` es más antigua que
  --dias-leidas (default 30).
- Notificaciones NO leídas: se eliminan si `fecha_creacion` es más antigua
  que --dias-no-leidas (default 90).

Modo:
- Sin flags → dry-run.
- --apply → aplica.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.models import Notificacion


class Command(BaseCommand):
    help = 'Elimina notificaciones antiguas (leídas y no leídas más viejas que el umbral).'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true',
                            help='Aplica los borrados. Sin este flag es dry-run.')
        parser.add_argument('--dias-leidas', type=int, default=30,
                            help='Umbral para notificaciones leídas (default 30).')
        parser.add_argument('--dias-no-leidas', type=int, default=90,
                            help='Umbral para notificaciones no leídas (default 90).')

    def handle(self, *args, **options):
        apply = options['apply']
        dias_leidas = options['dias_leidas']
        dias_no_leidas = options['dias_no_leidas']

        ahora = timezone.now()
        corte_leidas = ahora - timedelta(days=dias_leidas)
        corte_no_leidas = ahora - timedelta(days=dias_no_leidas)

        qs_leidas = Notificacion.objects.filter(
            leida=True, fecha_leida__lt=corte_leidas,
        )
        qs_no_leidas = Notificacion.objects.filter(
            leida=False, fecha_creacion__lt=corte_no_leidas,
        )

        n_leidas = qs_leidas.count()
        n_no_leidas = qs_no_leidas.count()
        total = n_leidas + n_no_leidas

        self.stdout.write(f'Leídas con fecha_leida < {corte_leidas:%Y-%m-%d %H:%M}: {n_leidas}')
        self.stdout.write(f'No leídas con fecha_creacion < {corte_no_leidas:%Y-%m-%d %H:%M}: {n_no_leidas}')
        self.stdout.write(f'Total a eliminar: {total}')

        if not apply:
            self.stdout.write(self.style.WARNING(
                '\n*** DRY-RUN — no se eliminó nada. Corre con --apply. ***'
            ))
            return

        borradas_leidas, _ = qs_leidas.delete()
        borradas_no_leidas, _ = qs_no_leidas.delete()
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Eliminadas: {borradas_leidas} leídas + {borradas_no_leidas} no leídas '
            f'= {borradas_leidas + borradas_no_leidas} totales.'
        ))
