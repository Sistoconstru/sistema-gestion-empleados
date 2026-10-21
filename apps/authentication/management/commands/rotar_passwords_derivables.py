"""Detecta y rota las contraseñas que siguen siendo las generadas automáticamente.

El alta automática de usuarios (apps/employees/signals.py y la vista de creación
de empleado) genera la contraseña como `{PrimerNombre}{numero_documento}`. Como
el número de documento sale en varios listados y exportaciones, la contraseña de
cualquier empleado que nunca la cambió es derivable sin adivinar nada: no hace
falta fuerza bruta, se calcula. Este comando mide cuántas cuentas siguen así y
las rota.

Estrategia:
- Para cada empleado con usuario, reconstruye la contraseña derivable y la
  compara con `check_password`. Solo detecta las que nunca se cambiaron.
- Por defecto solo mira cuentas con privilegios (is_staff/is_superuser), que son
  las que convierten el hallazgo en acceso total a la base.
- La contraseña nueva es aleatoria (get_random_string, 16 caracteres) y se
  escribe únicamente en el CSV de --salida, nunca en stdout, para que no quede
  en el historial de la terminal ni en los logs del contenedor.

Modos:
- Sin flags → dry-run: informa cuántas cuentas están afectadas.
- --solo-marcar → no toca la contraseña, solo activa `debe_cambiar_password`.
  El usuario entra con la que tiene y el middleware lo obliga a cambiarla antes
  de poder usar el sistema. No hay que repartir credenciales, pero la contraseña
  derivable sigue sirviendo hasta que cada persona ingrese.
- --apply --salida <archivo.csv> → rota a una contraseña aleatoria y además
  activa el flag. Cierra la ventana de inmediato, a cambio de tener que entregar
  la temporal por un canal aparte.
- --scope todos → incluye a todos los empleados, no solo a los privilegiados.

Ojo: --apply con --scope todos invalida la contraseña de casi toda la empresa.
Para un despliegue masivo normalmente conviene --solo-marcar.
"""
import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.crypto import get_random_string

from apps.employees.models import Empleado


class Command(BaseCommand):
    help = 'Detecta y rota contraseñas que siguen siendo las derivables del alta automática.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true',
                            help='Rota la contraseña y activa el flag. Sin este flag es dry-run.')
        parser.add_argument('--solo-marcar', action='store_true',
                            help='Solo activa debe_cambiar_password, sin tocar la contraseña.')
        parser.add_argument('--scope', choices=['privilegiados', 'todos'],
                            default='privilegiados',
                            help='A quién revisar (default: privilegiados).')
        parser.add_argument('--salida', type=str, default=None,
                            help='CSV donde escribir usuario,password. Obligatorio con --apply.')

    def handle(self, *args, **options):
        aplicar = options['apply']
        solo_marcar = options['solo_marcar']
        scope = options['scope']
        salida = options['salida']

        if aplicar and solo_marcar:
            raise CommandError('--apply y --solo-marcar son excluyentes.')
        if aplicar and not salida:
            raise CommandError(
                '--apply requiere --salida <archivo.csv>: las contraseñas nuevas no '
                'se imprimen en pantalla para que no queden en logs ni historial.'
            )

        qs = (Empleado.objects
              .select_related('usuario')
              .exclude(usuario__isnull=True)
              .order_by('apellidos', 'nombres'))
        if scope == 'privilegiados':
            qs = qs.filter(usuario__is_staff=True) | qs.filter(usuario__is_superuser=True)
            qs = qs.distinct()

        total = afectadas = 0
        objetivo = []

        for empleado in qs:
            usuario = empleado.usuario
            if not usuario or not empleado.nombres.strip():
                continue
            total += 1
            derivable = f"{empleado.nombres.split()[0].capitalize()}{empleado.numero_documento}"
            if usuario.check_password(derivable):
                afectadas += 1
                objetivo.append(usuario)

        self.stdout.write(f"Cuentas revisadas ({scope}): {total}")
        self.stdout.write(f"Conservan la contraseña derivable: {afectadas}")
        for usuario in objetivo:
            etiqueta = 'superuser' if usuario.is_superuser else ('staff' if usuario.is_staff else 'empleado')
            self.stdout.write(f"   - {usuario.username} ({etiqueta})")

        if not afectadas:
            self.stdout.write(self.style.SUCCESS('Nada por rotar.'))
            return

        if not aplicar and not solo_marcar:
            self.stdout.write(self.style.WARNING(
                f"\nDry-run: no se cambió nada. Para estas {afectadas} cuentas:\n"
                f"  # obligar el cambio sin repartir credenciales\n"
                f"  python manage.py rotar_passwords_derivables --scope {scope} --solo-marcar\n"
                f"  # o rotar ya y entregar una temporal\n"
                f"  python manage.py rotar_passwords_derivables --scope {scope} "
                f"--apply --salida credenciales.csv"
            ))
            return

        if solo_marcar:
            with transaction.atomic():
                for usuario in objetivo:
                    usuario.debe_cambiar_password = True
                    usuario.save(update_fields=['debe_cambiar_password'])
            self.stdout.write(self.style.SUCCESS(
                f"\n{len(objetivo)} cuentas marcadas. En su próximo ingreso el "
                f"middleware las manda a cambiar la contraseña antes de dejarlas "
                f"usar el sistema."
            ))
            self.stdout.write(self.style.WARNING(
                'La contraseña derivable sigue funcionando para ese primer ingreso. '
                'Si necesitas cerrar la ventana de inmediato, usa --apply.'
            ))
            return

        credenciales = []
        with transaction.atomic():
            for usuario in objetivo:
                nueva = get_random_string(16)
                usuario.set_password(nueva)
                usuario.debe_cambiar_password = True
                usuario.save(update_fields=['password', 'debe_cambiar_password'])
                credenciales.append((usuario.username, usuario.email or '', nueva))

        with open(salida, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(['usuario', 'email', 'password_temporal'])
            writer.writerows(credenciales)

        self.stdout.write(self.style.SUCCESS(
            f"\n{len(credenciales)} contraseñas rotadas. Credenciales en: {salida}"
        ))
        self.stdout.write(self.style.WARNING(
            'Son temporales: el middleware exige cambiarlas en el primer ingreso. '
            'Entrégalas por un canal privado y borra el CSV cuando termines.'
        ))
