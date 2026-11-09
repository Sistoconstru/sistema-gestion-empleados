"""Desactiva suscripciones push repetidas del mismo dispositivo.

Cada vez que el navegador vuelve a suscribirse emite un endpoint nuevo, y el
anterior queda activo en la base aunque ya no lo use nadie. Pasa al
reinstalar la app, al limpiar datos del sitio o al cambiar de permisos. El
resultado es que un mismo teléfono figura varias veces y recibe el mismo
aviso repetido.

Se conserva la más reciente de cada usuario+dispositivo y se desactivan las
anteriores. No se borran: si una de ellas sigue viva, el envío fallará y el
sistema ya lleva la cuenta de fallos; dejar el registro permite revisarlo.
"""
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import PushSubscription

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ('Desactiva las suscripciones push repetidas del mismo usuario y '
            'dispositivo, conservando la más reciente.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se desactivaría sin guardar nada',
        )

    def handle(self, **options):
        dry_run = options['dry_run']

        activas = PushSubscription.objects.filter(activa=True).select_related(
            'usuario').order_by('usuario_id', '-fecha_creacion')

        total = activas.count()
        self.stdout.write(f'Suscripciones activas: {total}\n')

        # El user_agent es lo más cercano a "el mismo dispositivo" que hay
        # guardado. Dos navegadores distintos del mismo usuario (celular y
        # computador) deben conservarse por separado.
        grupos = defaultdict(list)
        for s in activas:
            grupos[(s.usuario_id, s.user_agent)].append(s)

        a_desactivar = []
        for (usuario_id, _ua), subs in grupos.items():
            if len(subs) > 1:
                # Vienen ordenadas de más nueva a más vieja.
                a_desactivar.extend(subs[1:])

        if not a_desactivar:
            self.stdout.write(self.style.SUCCESS(
                'No hay suscripciones repetidas.'))
            return

        usuarios = sorted({s.usuario.username for s in a_desactivar})
        self.stdout.write(
            f'Suscripciones a desactivar: {len(a_desactivar)} '
            f'de {len(usuarios)} usuarios\n')
        for u in usuarios:
            suyas = [s for s in a_desactivar if s.usuario.username == u]
            quedan = PushSubscription.objects.filter(
                usuario__username=u, activa=True).count() - len(suyas)
            self.stdout.write(
                f'   {u:22} se desactivan {len(suyas)}, le quedan {quedan}')

        if dry_run:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.WARNING(
                f'DRY RUN: se desactivarían {len(a_desactivar)}. '
                f'No se guardó nada.'
            ))
            return

        ahora = timezone.now()
        with transaction.atomic():
            n = PushSubscription.objects.filter(
                id__in=[s.id for s in a_desactivar]
            ).update(activa=False, fecha_ultimo_uso=ahora)

        logger.info('Desactivadas %s suscripciones push repetidas.', n)

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'Desactivadas {n} suscripciones repetidas.'))
        self.stdout.write(
            f'Quedan activas: '
            f'{PushSubscription.objects.filter(activa=True).count()}')
