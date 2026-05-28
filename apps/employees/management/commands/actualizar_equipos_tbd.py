# =============================================================================
# apps/employees/management/commands/actualizar_equipos_tbd.py
# Comando para actualizar partidos con equipos TBD (To Be Determined)
# cuando se definan los clasificados en la fase eliminatoria
# =============================================================================

from django.core.management.base import BaseCommand
from apps.employees.models import PartidoMundial
import requests
import os

class Command(BaseCommand):
    help = 'Actualiza equipos TBD cuando se definan los clasificados'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Actualizando equipos TBD...'))

        # Obtener API key desde variables de entorno
        API_KEY = os.getenv('THESPORTSDB_API_KEY', '3')
        BASE_URL = 'https://www.thesportsdb.com/api/v1/json'

        # Buscar partidos con equipos TBD
        partidos_tbd = PartidoMundial.objects.filter(
            api_id__isnull=False
        ).filter(
            equipo_local__icontains='TBD'
        ) | PartidoMundial.objects.filter(
            api_id__isnull=False,
            equipo_visitante__icontains='TBD'
        )

        total = partidos_tbd.count()
        self.stdout.write(f'Partidos con TBD encontrados: {total}')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('✓ No hay partidos con equipos TBD'))
            return

        actualizados = 0

        for partido in partidos_tbd:
            try:
                # Consultar el partido en la API
                url = f'{BASE_URL}/{API_KEY}/lookupevent.php?id={partido.api_id}'
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                data = response.json()

                if data and 'events' in data and data['events']:
                    event = data['events'][0]

                    equipo_local_nuevo = event.get('strHomeTeam', 'TBD')
                    equipo_visitante_nuevo = event.get('strAwayTeam', 'TBD')

                    # Verificar si cambió algún equipo
                    if equipo_local_nuevo != partido.equipo_local or equipo_visitante_nuevo != partido.equipo_visitante:
                        partido.equipo_local = equipo_local_nuevo
                        partido.equipo_visitante = equipo_visitante_nuevo
                        partido.save()

                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Actualizado: {partido.equipo_local} vs {partido.equipo_visitante}'
                        ))
                        actualizados += 1

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.WARNING(f'Error consultando partido {partido.api_id}: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error procesando partido {partido.id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n=== Resumen ==='))
        self.stdout.write(self.style.SUCCESS(f'Partidos actualizados: {actualizados}'))
        self.stdout.write(self.style.SUCCESS(f'Partidos pendientes (aún TBD): {total - actualizados}'))
