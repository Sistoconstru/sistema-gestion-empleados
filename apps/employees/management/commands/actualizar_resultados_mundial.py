# =============================================================================
# apps/employees/management/commands/actualizar_resultados_mundial.py
# Comando para actualizar resultados de partidos y calcular puntos de predicciones
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.employees.models import PartidoMundial, PrediccionMundial
import requests
import os

class Command(BaseCommand):
    help = 'Actualiza resultados de partidos del Mundial y calcula puntos de predicciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recalcular',
            action='store_true',
            help='Recalcula puntos de todas las predicciones de partidos finalizados'
        )
        parser.add_argument(
            '--resincronizar',
            action='store_true',
            help='Re-sincroniza TODOS los partidos finalizados desde la API y recalcula puntos (corrección de marcadores)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada'
        )

    def handle(self, *args, **options):
        recalcular = options['recalcular']
        resincronizar = options['resincronizar']
        self.verbose = options['verbose']

        if resincronizar:
            self.stdout.write(self.style.WARNING('Re-sincronizando TODOS los partidos finalizados desde API...'))
            self._resincronizar_todos()
        elif recalcular:
            self.stdout.write(self.style.WARNING('Recalculando puntos de todas las predicciones...'))
            self._recalcular_todos()
        else:
            self.stdout.write(self.style.WARNING('Actualizando resultados desde TheSportsDB Premium...'))
            self._actualizar_desde_api()

    def _actualizar_desde_api(self):
        """Actualiza resultados desde la API de TheSportsDB Premium"""
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

        # Solo consultar partidos en su "ventana de recién terminado":
        # - empezaron hace 2h+ (un partido dura ~2h, ya debería haber terminado)
        # - pero no hace más de 24h (margen para que la API publique; pasado eso
        #   requiere revisión manual)
        # Esto minimiza el consumo de API: si no hay partidos terminando, no se
        # hace ninguna request. Permite correr el job cada pocos minutos sin gastar
        # el plan mensual de la API.
        ahora = timezone.now()
        partidos_pendientes = PartidoMundial.objects.filter(
            api_id__isnull=False,
            finalizado=False,
            fecha_hora__lte=ahora - timedelta(hours=2),
            fecha_hora__gte=ahora - timedelta(hours=24),
        )

        if not partidos_pendientes.exists():
            self.stdout.write('Sin partidos en ventana de finalización (0 requests a la API)')
            self.stdout.write(self.style.SUCCESS('\n=== Resumen ===\nPartidos actualizados: 0'))
            return

        self.stdout.write(f'Partidos en ventana de finalización: {partidos_pendientes.count()}')

        actualizados = 0

        for partido in partidos_pendientes:
            try:
                # Consultar resultado del evento específico
                url = f'{BASE_URL}/{API_KEY}/lookupevent.php?id={partido.api_id}'
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                data = response.json()

                if data and 'events' in data and data['events']:
                    event = data['events'][0]

                    # Verificar estado del partido
                    status = event.get('strStatus', '')
                    home_score = event.get('intHomeScore')
                    away_score = event.get('intAwayScore')

                    # Solo actualizar si el partido REALMENTE finalizó (Full Time)
                    # strStatus puede ser: "FT" (Full Time), "AET" (After Extra Time), "PEN" (Penalties), etc.
                    # No actualizar si está "Live", "HT" (Half Time), o en progreso
                    if home_score is not None and away_score is not None and status in ['FT', 'AET', 'PEN', 'AOT']:
                        # Actualizar resultado final
                        partido.goles_local = int(home_score)
                        partido.goles_visitante = int(away_score)
                        partido.finalizado = True
                        partido.save()

                        self.stdout.write(self.style.SUCCESS(
                            f'Actualizado [{status}]: {partido.equipo_local} {partido.goles_local} - {partido.goles_visitante} {partido.equipo_visitante}'
                        ))

                        # Calcular puntos de todas las predicciones de este partido
                        predicciones = PrediccionMundial.objects.filter(partido=partido)
                        puntos_calculados = 0

                        for prediccion in predicciones:
                            prediccion.calcular_puntos()
                            prediccion.save()
                            puntos_calculados += 1

                        self.stdout.write(f'  → {puntos_calculados} predicciones actualizadas')
                        actualizados += 1

                    elif home_score is not None and away_score is not None:
                        # Partido tiene marcador pero aún no finalizó (Live, HT, etc.)
                        if self.verbose:
                            self.stdout.write(self.style.WARNING(
                                f'En progreso [{status}]: {partido.equipo_local} {home_score} - {away_score} {partido.equipo_visitante} (esperando finalización...)'
                            ))

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.WARNING(f'Error consultando partido {partido.api_id}: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error procesando partido {partido.id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n=== Resumen ==='))
        self.stdout.write(self.style.SUCCESS(f'Partidos actualizados: {actualizados}'))

    def _recalcular_todos(self):
        """Recalcula puntos de todas las predicciones de partidos finalizados"""
        partidos_finalizados = PartidoMundial.objects.filter(finalizado=True)

        self.stdout.write(f'Partidos finalizados: {partidos_finalizados.count()}')

        total_predicciones = 0

        for partido in partidos_finalizados:
            predicciones = PrediccionMundial.objects.filter(partido=partido)

            for prediccion in predicciones:
                prediccion.calcular_puntos()
                prediccion.save()
                total_predicciones += 1

        self.stdout.write(self.style.SUCCESS(f'\n=== Resumen ==='))
        self.stdout.write(self.style.SUCCESS(f'Predicciones recalculadas: {total_predicciones}'))

    def _resincronizar_todos(self):
        """Re-sincroniza TODOS los partidos finalizados desde la API y recalcula puntos"""
        # Obtener API key
        API_KEY = os.getenv('THESPORTSDB_API_KEY', '3')

        if API_KEY == 'TU_API_KEY_PREMIUM_AQUI' or API_KEY == '3':
            self.stdout.write(self.style.ERROR('ADVERTENCIA: Usando API key gratuita'))
            self.stdout.write(self.style.WARNING('Configura THESPORTSDB_API_KEY en tu archivo .env\n'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Usando API key Premium: {API_KEY[:6]}...'))

        BASE_URL = 'https://www.thesportsdb.com/api/v1/json'

        # Obtener TODOS los partidos que están marcados como finalizados
        partidos_finalizados = PartidoMundial.objects.filter(
            finalizado=True,
            api_id__isnull=False
        )

        self.stdout.write(f'Partidos marcados como finalizados: {partidos_finalizados.count()}')
        self.stdout.write(self.style.WARNING('ADVERTENCIA: Esto consumira 1 request de API por cada partido'))

        actualizados = 0
        corregidos = 0
        total_predicciones = 0

        for partido in partidos_finalizados:
            try:
                # Consultar resultado actualizado desde la API
                url = f'{BASE_URL}/{API_KEY}/lookupevent.php?id={partido.api_id}'
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                data = response.json()

                if data and 'events' in data and data['events']:
                    event = data['events'][0]

                    # Obtener estado y marcador
                    status = event.get('strStatus', '')
                    home_score = event.get('intHomeScore')
                    away_score = event.get('intAwayScore')

                    if home_score is not None and away_score is not None and status in ['FT', 'AET', 'PEN', 'AOT']:
                        marcador_anterior = f'{partido.goles_local}-{partido.goles_visitante}'
                        marcador_nuevo = f'{int(home_score)}-{int(away_score)}'

                        # Verificar si cambió el marcador
                        if marcador_anterior != marcador_nuevo:
                            self.stdout.write(self.style.WARNING(
                                f'CORRECCION [{status}]: {partido.equipo_local} {marcador_anterior} -> {marcador_nuevo} {partido.equipo_visitante}'
                            ))
                            corregidos += 1
                        else:
                            self.stdout.write(
                                f'OK [{status}]: {partido.equipo_local} {marcador_nuevo} {partido.equipo_visitante}'
                            )

                        # Actualizar marcador
                        partido.goles_local = int(home_score)
                        partido.goles_visitante = int(away_score)
                        partido.save()

                        # Recalcular puntos de TODAS las predicciones
                        predicciones = PrediccionMundial.objects.filter(partido=partido)

                        for prediccion in predicciones:
                            prediccion.calcular_puntos()
                            prediccion.save()
                            total_predicciones += 1

                        actualizados += 1

                    else:
                        self.stdout.write(self.style.ERROR(
                            f'NO FINALIZADO [{status}]: {partido.equipo_local} vs {partido.equipo_visitante} (marcado incorrectamente como finalizado)'
                        ))

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.WARNING(f'Error consultando partido {partido.api_id}: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error procesando partido {partido.id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n=== Resumen ==='))
        self.stdout.write(self.style.SUCCESS(f'Partidos re-sincronizados: {actualizados}'))
        self.stdout.write(self.style.WARNING(f'Marcadores corregidos: {corregidos}'))
        self.stdout.write(self.style.SUCCESS(f'Predicciones recalculadas: {total_predicciones}'))
