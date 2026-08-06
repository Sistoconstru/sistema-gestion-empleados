"""Asegura que existan claves VAPID persistentes para Web Push.

Se llama desde start.sh al arrancar en Railway. La primera corrida genera un
par de claves nuevas y las guarda en la tabla ConfiguracionSistema (módulo
'pwa'); las siguientes corridas leen las mismas — CRÍTICO para que las
suscripciones push guardadas en el navegador de los empleados sigan siendo
válidas entre deploys.

Precedencia:
  1. Si VAPID_PUBLIC_KEY ya está en el entorno (setter manual en Railway) →
     no toca nada, sale silencioso.
  2. Si están en la DB → las imprime como `export VAR=valor` para que
     start.sh haga `eval` y las inyecte al proceso.
  3. Si no están en ninguna parte → genera, persiste en DB, imprime.

Uso desde start.sh:
    eval "$(python manage.py asegurar_vapid_keys)"
"""
import base64
import os
import sys

from django.core.management.base import BaseCommand
from django.db import transaction
from py_vapid import Vapid


PWA_MODULO = 'pwa'
CLAVE_PUB = 'vapid_public_key'
CLAVE_PRIV = 'vapid_private_key'
CLAVE_EMAIL = 'vapid_admin_email'


def _generar_par():
    """Genera un par VAPID y retorna (public_b64, private_b64)."""
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    v = Vapid()
    v.generate_keys()
    pub_der = v.public_key.public_bytes(
        encoding=Encoding.X962, format=PublicFormat.UncompressedPoint
    )
    pub_b64 = base64.urlsafe_b64encode(pub_der).rstrip(b'=').decode()
    priv_bytes = v.private_key.private_numbers().private_value.to_bytes(32, 'big')
    priv_b64 = base64.urlsafe_b64encode(priv_bytes).rstrip(b'=').decode()
    return pub_b64, priv_b64


def _get_settings_map():
    """Retorna dict {clave: valor} de las 3 claves PWA guardadas en DB."""
    from apps.core.models import ConfiguracionSistema
    filas = ConfiguracionSistema.objects.filter(
        modulo=PWA_MODULO,
        clave__in=(CLAVE_PUB, CLAVE_PRIV, CLAVE_EMAIL),
    )
    return {f.clave: f.valor for f in filas}


def _persistir(pub_b64, priv_b64, admin_email):
    """Guarda las 3 claves en ConfiguracionSistema. actualizado_por = primer
    superuser disponible (fallback: primer Usuario activo)."""
    from apps.core.models import ConfiguracionSistema
    from django.contrib.auth import get_user_model

    User = get_user_model()
    system_user = (
        User.objects.filter(is_superuser=True).order_by('id').first()
        or User.objects.filter(is_active=True).order_by('id').first()
    )
    if system_user is None:
        raise RuntimeError(
            'No hay ningún Usuario en la base — no se puede persistir la config VAPID.'
        )

    defaults = {
        'valor': '',  # se sobrescribe abajo por cada clave
        'tipo_dato': 'string',
        'editable_usuario': False,
        'actualizado_por': system_user,
    }
    with transaction.atomic():
        for clave, valor, descripcion in (
            (CLAVE_PUB, pub_b64, 'Clave pública VAPID para Web Push (formato base64url raw)'),
            (CLAVE_PRIV, priv_b64, 'Clave privada VAPID — NO COMPARTIR'),
            (CLAVE_EMAIL, admin_email, 'Contacto para el push service (VAPID sub claim)'),
        ):
            ConfiguracionSistema.objects.update_or_create(
                modulo=PWA_MODULO, clave=clave,
                defaults={**defaults, 'valor': valor, 'descripcion': descripcion},
            )


def _emitir_export(pub_b64, priv_b64, admin_email):
    """Imprime en stdout las tres líneas `export` que start.sh evalúa.

    Las stderrizamos con logs discretos para que `eval` no confunda comentarios
    con instrucciones."""
    sys.stdout.write(f'export VAPID_PUBLIC_KEY={pub_b64}\n')
    sys.stdout.write(f'export VAPID_PRIVATE_KEY={priv_b64}\n')
    sys.stdout.write(f'export VAPID_ADMIN_EMAIL={admin_email}\n')
    sys.stdout.flush()


class Command(BaseCommand):
    help = 'Asegura que existan claves VAPID persistentes para Web Push. Idempotente.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-regen',
            action='store_true',
            help='Regenera las claves aunque ya existan (invalida todas las suscripciones actuales).',
        )
        parser.add_argument(
            '--admin-email',
            default=None,
            help='Email de contacto VAPID. Por defecto usa el del primer superuser.',
        )

    def handle(self, *args, **options):
        # 1. Env vars ya seteadas en Railway → nada que hacer.
        env_pub = os.environ.get('VAPID_PUBLIC_KEY', '').strip()
        env_priv = os.environ.get('VAPID_PRIVATE_KEY', '').strip()
        if env_pub and env_priv and not options['force_regen']:
            self.stderr.write('VAPID keys ya presentes en el entorno; no se toca nada.')
            return

        actuales = _get_settings_map()
        pub = actuales.get(CLAVE_PUB, '').strip()
        priv = actuales.get(CLAVE_PRIV, '').strip()
        email = actuales.get(CLAVE_EMAIL, '').strip()

        # Email por defecto: primer superuser
        if not email:
            if options['admin_email']:
                email = options['admin_email']
            else:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                su = User.objects.filter(is_superuser=True, email__contains='@').order_by('id').first()
                email = f'mailto:{su.email}' if su and su.email else 'mailto:admin@sighu.local'

        if not (pub and priv) or options['force_regen']:
            pub, priv = _generar_par()
            _persistir(pub, priv, email)
            self.stderr.write('VAPID keys generadas y persistidas en ConfiguracionSistema.')
        else:
            self.stderr.write('VAPID keys ya persistidas; se re-emiten sin regenerar.')

        _emitir_export(pub, priv, email)
