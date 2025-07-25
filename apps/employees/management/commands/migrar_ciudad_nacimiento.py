from django.core.management.base import BaseCommand
from apps.employees.models import Empleado, Ciudad

class Command(BaseCommand):
    help = 'Migra ciudad_nacimiento_text a ciudad_nacimiento (ForeignKey)'

    def handle(self, *args, **options):
        total = 0
        for empleado in Empleado.objects.all():
            texto = (empleado.ciudad_nacimiento_text or '').strip().upper()
            if texto:
                partes = texto.split(',')
                ciudad_nombre = partes[0].strip()
                ciudad = Ciudad.objects.filter(nombre__iexact=ciudad_nombre).first()
                if ciudad:
                    empleado.ciudad_nacimiento = ciudad
                    empleado.save()
                    total += 1
        self.stdout.write(self.style.SUCCESS(f'Migrados {total} empleados.'))