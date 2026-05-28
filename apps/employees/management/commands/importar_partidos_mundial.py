# =============================================================================
# apps/employees/management/commands/importar_partidos_mundial.py
# Comando para importar partidos del Mundial 2026 desde TheSportsDB API Premium
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from apps.employees.models import PartidoMundial
import requests
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Importa partidos del Mundial 2026 desde TheSportsDB API Premium'

    def add_arguments(self, parser):
        parser.add_argument(
            '--season',
            type=str,
            default='2026',
            help='Temporada del mundial (default: 2026)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar actualización de partidos existentes'
        )

    def handle(self, *args, **options):
        season = options['season']
        force_update = options['force']

        self.stdout.write(self.style.WARNING(f'Importando partidos del Mundial {season}...'))

        # Obtener API key desde variables de entorno
        API_KEY = os.getenv('THESPORTSDB_API_KEY', '3')

        if API_KEY == 'TU_API_KEY_PREMIUM_AQUI' or API_KEY == '3':
            self.stdout.write(self.style.ERROR('⚠️  ADVERTENCIA: Usando API key gratuita o no configurada'))
            self.stdout.write(self.style.WARNING('Configura THESPORTSDB_API_KEY en tu archivo .env con tu API key premium'))
            self.stdout.write(self.style.WARNING('Continúa con limitaciones de la API gratuita (15 requests/mes)...\n'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Usando API key Premium: {API_KEY[:6]}...'))

        BASE_URL = 'https://www.thesportsdb.com/api/v1/json'

        # ID de la liga del Mundial de FIFA
        LEAGUE_ID = '4429'  # FIFA World Cup

        try:
            # Obtener eventos (partidos) de la liga
            url = f'{BASE_URL}/{API_KEY}/eventsseason.php?id={LEAGUE_ID}&s={season}'
            self.stdout.write(f'Consultando: {url}')

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            if not data or 'events' not in data or data['events'] is None:
                self.stdout.write(self.style.ERROR('No se encontraron partidos para esta temporada'))
                self.stdout.write(self.style.WARNING('Nota: Los partidos del Mundial 2026 pueden no estar disponibles aún en la API'))
                return

            events = data['events']
            self.stdout.write(self.style.SUCCESS(f'Se encontraron {len(events)} partidos'))

            creados = 0
            actualizados = 0

            for event in events:
                # Procesar fecha y hora
                fecha_str = event.get('dateEvent')  # Formato: YYYY-MM-DD
                hora_str = event.get('strTime', '00:00:00')  # Formato: HH:MM:SS

                if not fecha_str:
                    continue

                try:
                    fecha_hora = datetime.strptime(f'{fecha_str} {hora_str}', '%Y-%m-%d %H:%M:%S')
                    fecha_hora = timezone.make_aware(fecha_hora)
                except (ValueError, TypeError):
                    self.stdout.write(self.style.WARNING(f'Fecha inválida: {fecha_str} {hora_str}'))
                    continue

                # Determinar fase del torneo basándose en el nombre del round
                round_name = event.get('strEvent', '').lower()
                fase = self._determinar_fase(round_name)

                # Datos del partido
                partido_data = {
                    'equipo_local': event.get('strHomeTeam', 'TBD'),
                    'equipo_visitante': event.get('strAwayTeam', 'TBD'),
                    'fecha_hora': fecha_hora,
                    'fase': fase,
                    'estadio': event.get('strVenue', ''),
                    'ciudad': event.get('strCity', ''),
                    'api_id': event.get('idEvent'),
                }

                # Verificar si el partido ya existe por API ID
                if partido_data['api_id']:
                    partido, created = PartidoMundial.objects.update_or_create(
                        api_id=partido_data['api_id'],
                        defaults=partido_data
                    )

                    if created:
                        creados += 1
                        self.stdout.write(self.style.SUCCESS(f'✓ Creado: {partido.equipo_local} vs {partido.equipo_visitante}'))
                    else:
                        actualizados += 1
                        self.stdout.write(f'  Actualizado: {partido.equipo_local} vs {partido.equipo_visitante}')

            self.stdout.write(self.style.SUCCESS(f'\n=== Resumen ==='))
            self.stdout.write(self.style.SUCCESS(f'Partidos creados: {creados}'))
            self.stdout.write(self.style.SUCCESS(f'Partidos actualizados: {actualizados}'))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error al consultar la API: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error inesperado: {e}'))

    def _determinar_fase(self, round_name):
        """Determina la fase del torneo basándose en el nombre del round"""
        round_name = round_name.lower()

        if 'final' in round_name and 'semi' not in round_name and 'quarter' not in round_name:
            return 'final'
        elif 'semi' in round_name or 'semifinal' in round_name:
            return 'semifinal'
        elif 'third' in round_name or 'tercer' in round_name:
            return 'tercer_lugar'
        elif 'quarter' in round_name or 'cuartos' in round_name:
            return 'cuartos'
        elif 'round of 16' in round_name or 'octavos' in round_name:
            return 'octavos'
        else:
            return 'grupos'
