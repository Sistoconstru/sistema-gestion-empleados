"""Carga o actualiza vehículos a mano, mientras Odoo expone su listado.

Es un puente temporal: cuando exista GET /sighu_sync/vehiculos, la carga la
hará la sincronización y este comando quedará solo para pruebas. Por eso
exige el id de Odoo — así los vehículos que se registren ahora cruzan con
los que llegue a mandar Odoo, sin reconciliar nada a mano después.

Uso:
    python manage.py cargar_vehiculos --json vehiculos.json
    python manage.py cargar_vehiculos --odoo-id 12 --placa "JYN 240" \\
        --marca Chevrolet --modelo NPR --anio 2019 --conductor 71391550
"""
import json

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.employees.models import Empleado
from apps.transporte.models import Vehiculo


class Command(BaseCommand):
    help = 'Crea o actualiza vehículos por su id de Odoo (puente mientras no hay sincronización).'

    def add_arguments(self, parser):
        parser.add_argument('--json', help='Archivo JSON con una lista de vehículos')
        parser.add_argument('--odoo-id', type=int, help='ID del vehículo en Odoo')
        parser.add_argument('--placa')
        parser.add_argument('--marca', default='')
        parser.add_argument('--modelo', default='')
        parser.add_argument('--anio', type=int)
        parser.add_argument('--conductor', help='Cédula del conductor a asignar')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, **options):
        if options['json']:
            with open(options['json'], encoding='utf-8') as f:
                registros = json.load(f)
            if not isinstance(registros, list):
                raise CommandError('El JSON debe ser una lista de objetos.')
        else:
            if not options['odoo_id'] or not options['placa']:
                raise CommandError('Indica --json, o bien --odoo-id y --placa.')
            registros = [{
                'odoo_id': options['odoo_id'],
                'placa': options['placa'],
                'marca': options['marca'],
                'modelo': options['modelo'],
                'anio': options['anio'],
                'conductor': options['conductor'],
            }]

        dry_run = options['dry_run']
        creados = actualizados = 0

        for r in registros:
            odoo_id = r.get('odoo_id')
            if not odoo_id:
                self.stdout.write(self.style.ERROR(f'  sin odoo_id, se omite: {r}'))
                continue

            conductor = None
            cedula = r.get('conductor')
            if cedula:
                conductor = Empleado.objects.filter(numero_documento=str(cedula)).first()
                if not conductor:
                    self.stdout.write(self.style.WARNING(
                        f'  cédula {cedula} no encontrada; el vehículo queda sin conductor'))

            datos = {
                'placa': r.get('placa', ''),
                'marca': r.get('marca', '') or '',
                'modelo': r.get('modelo', '') or '',
                'anio': r.get('anio'),
                'fecha_sincronizacion': timezone.now(),
            }
            if conductor:
                datos['conductor'] = conductor

            existente = Vehiculo.objects.filter(odoo_id=odoo_id).first()
            accion = 'actualizaría' if existente else 'crearía'
            if dry_run:
                self.stdout.write(f'  {accion}: odoo_id={odoo_id} {datos["placa"]}')
                continue

            vehiculo, creado = Vehiculo.objects.update_or_create(
                odoo_id=odoo_id, defaults=datos)
            if creado:
                creados += 1
            else:
                actualizados += 1
            self.stdout.write(
                f'  {"creado" if creado else "actualizado"}: {vehiculo.placa} '
                f'(odoo_id={odoo_id}'
                f'{", conductor=" + conductor.nombre_completo if conductor else ""})')

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nDRY RUN sobre {len(registros)} registro(s). No se guardó nada.'))
            return

        self.stdout.write(self.style.SUCCESS(
            f'\nVehículos creados: {creados} | actualizados: {actualizados}'))
