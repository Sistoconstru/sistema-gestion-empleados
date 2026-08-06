"""Genera un par de claves VAPID nuevas listas para pegar en el .env.

Corre una vez por entorno (dev, prod). No reemplaza claves existentes en el
entorno automáticamente — imprime lo que se debe pegar.
"""
import base64
from django.core.management.base import BaseCommand
from py_vapid import Vapid


class Command(BaseCommand):
    help = 'Genera un par VAPID (pública y privada) para configurar Web Push.'

    def handle(self, *args, **options):
        v = Vapid()
        v.generate_keys()

        # Pública: uncompressed X9.62 → base64url (formato que espera pushManager.subscribe)
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        pub_der = v.public_key.public_bytes(
            encoding=Encoding.X962, format=PublicFormat.UncompressedPoint
        )
        pub_b64 = base64.urlsafe_b64encode(pub_der).rstrip(b'=').decode()

        # Privada: raw 32-byte value → base64url (formato que espera pywebpush)
        priv_bytes = v.private_key.private_numbers().private_value.to_bytes(32, 'big')
        priv_b64 = base64.urlsafe_b64encode(priv_bytes).rstrip(b'=').decode()

        self.stdout.write(self.style.SUCCESS('Par VAPID generado.'))
        self.stdout.write('')
        self.stdout.write('Copia esto en tu .env (o secret store en producción):')
        self.stdout.write('')
        self.stdout.write(f'VAPID_PUBLIC_KEY={pub_b64}')
        self.stdout.write(f'VAPID_PRIVATE_KEY={priv_b64}')
        self.stdout.write(f'VAPID_ADMIN_EMAIL=mailto:tu-correo@dominio.com')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING(
            'IMPORTANTE: si cambias las claves, todas las suscripciones actuales '
            'quedan inválidas y los usuarios tendrán que volver a activar '
            'notificaciones. Solo regenera en la primera configuración o si hay '
            'sospecha de compromiso.'
        ))
