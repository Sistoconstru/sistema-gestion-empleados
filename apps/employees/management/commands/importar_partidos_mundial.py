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
import pytz
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
            self.stdout.write(self.style.ERROR('ADVERTENCIA: Usando API key gratuita o no configurada'))
            self.stdout.write(self.style.WARNING('Configura THESPORTSDB_API_KEY en tu archivo .env con tu API key premium'))
            self.stdout.write(self.style.WARNING('Continua con limitaciones de la API gratuita (15 requests/mes)...\n'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Usando API key Premium: {API_KEY[:6]}...'))

        # TheSportsDB API Premium usa v1 endpoint con más requests permitidos
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
                    # La API devuelve fechas/horas en UTC, debemos convertir a timezone local
                    fecha_hora_naive = datetime.strptime(f'{fecha_str} {hora_str}', '%Y-%m-%d %H:%M:%S')
                    # Interpretar como UTC primero
                    fecha_hora_utc = timezone.make_aware(fecha_hora_naive, timezone=pytz.UTC)
                    # Convertir a America/Bogota para almacenar correctamente
                    fecha_hora = fecha_hora_utc.astimezone(pytz.timezone('America/Bogota'))
                except (ValueError, TypeError):
                    self.stdout.write(self.style.WARNING(f'Fecha inválida: {fecha_str} {hora_str}'))
                    continue

                # Determinar fase del torneo basándose en las fechas oficiales de FIFA 2026
                # Prioridad 1: Usar strRound si está disponible
                # Prioridad 2: Usar fecha del partido según calendario oficial FIFA
                round_name = event.get('strRound', '')

                if round_name:
                    # Si la API tiene strRound, usarlo
                    fase = self._determinar_fase(round_name)
                    self.stdout.write(f'  → strRound: "{round_name}" → fase: {fase}')
                else:
                    # Determinar fase por fecha según calendario oficial FIFA 2026
                    fase = self._determinar_fase_por_fecha(fecha_hora)
                    self.stdout.write(f'  → Fecha: {fecha_hora.strftime("%Y-%m-%d")} → fase: {fase}')

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
                        self.stdout.write(self.style.SUCCESS(f'Creado: {partido.equipo_local} vs {partido.equipo_visitante}'))
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
        """
        Determina la fase del torneo basándose en el nombre del round

        Valores esperados de la API:
        - "Group Stage" -> grupos (multiplicador 1x)
        - "Round of 32" -> dieciseisavos (multiplicador 1x, igual que grupos)
        - "Round of 16" -> octavos (multiplicador 2x)
        - "Quarter-Final" -> cuartos (multiplicador 3x)
        - "Semi-Final" -> semifinal (multiplicador 4x)
        - "Third Place" -> tercer_lugar (multiplicador 4x)
        - "Final" -> final (multiplicador 5x)
        """
        if not round_name:
            return 'grupos'

        round_name_lower = round_name.lower()

        # Verificar en orden de especificidad para evitar conflictos

        # Tercer lugar (verificar antes que "final")
        if 'third' in round_name_lower or '3rd' in round_name_lower or 'tercer' in round_name_lower:
            return 'tercer_lugar'

        # Semifinal (verificar antes que "final")
        if 'semi' in round_name_lower:
            return 'semifinal'

        # Cuartos de final (verificar antes que "final")
        if 'quarter' in round_name_lower or 'cuartos' in round_name_lower:
            return 'cuartos'

        # Octavos de final
        if 'round of 16' in round_name_lower or 'octavos' in round_name_lower or 'round 16' in round_name_lower:
            return 'octavos'

        # Dieciseisavos de final (Round of 32) - mismo multiplicador que grupos
        if 'round of 32' in round_name_lower or 'dieciseisavos' in round_name_lower or 'round 32' in round_name_lower:
            return 'dieciseisavos'

        # Final (verificar al final para evitar que capture "Semi-Final" o "Quarter-Final")
        if round_name_lower == 'final' or round_name_lower.strip() == 'final':
            return 'final'

        # Fase de grupos (Group Stage o cualquier otro valor no reconocido)
        return 'grupos'

    def _determinar_fase_por_fecha(self, fecha_hora):
        """
        Determina la fase del torneo basándose en la fecha oficial de FIFA 2026

        Calendario oficial FIFA World Cup 2026:
        - Fase de grupos: 11 junio - 27 junio 2026
        - Round of 32 (Dieciseisavos): 28 junio - 3 julio 2026
        - Round of 16 (Octavos): 4 julio - 7 julio 2026
        - Cuartos de final: 9 julio - 11 julio 2026
        - Semifinales: 14 julio - 15 julio 2026
        - Tercer lugar: 18 julio 2026
        - Final: 19 julio 2026
        """
        from datetime import datetime

        # Convertir a naive para comparación simple de fechas
        fecha = fecha_hora.date()

        # Definir rangos de fechas por fase (año 2026)
        # Grupos: 11-27 junio
        if datetime(2026, 6, 11).date() <= fecha <= datetime(2026, 6, 27).date():
            return 'grupos'

        # Dieciseisavos (Round of 32): 28 junio - 3 julio
        elif datetime(2026, 6, 28).date() <= fecha <= datetime(2026, 7, 3).date():
            return 'dieciseisavos'

        # Octavos (Round of 16): 4-7 julio
        elif datetime(2026, 7, 4).date() <= fecha <= datetime(2026, 7, 7).date():
            return 'octavos'

        # Cuartos: 9-11 julio
        elif datetime(2026, 7, 9).date() <= fecha <= datetime(2026, 7, 11).date():
            return 'cuartos'

        # Semifinales: 14-15 julio
        elif datetime(2026, 7, 14).date() <= fecha <= datetime(2026, 7, 15).date():
            return 'semifinal'

        # Tercer lugar: 18 julio
        elif fecha == datetime(2026, 7, 18).date():
            return 'tercer_lugar'

        # Final: 19 julio
        elif fecha == datetime(2026, 7, 19).date():
            return 'final'

        # Por defecto, grupos (para partidos fuera de rango)
        else:
            return 'grupos'
