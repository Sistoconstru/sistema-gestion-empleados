from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.employees.models import Empleado, EstadoEmpleado
from apps.evaluations.models import AsignacionEvaluacion, EvaluacionDesempeño, TipoEvaluacion
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Asigna automáticamente evaluaciones de período de prueba a empleados con 30-60 días de servicio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta el comando sin hacer cambios reales, solo muestra qué se haría',
        )
        parser.add_argument(
            '--dias-minimos',
            type=int,
            default=30,
            help='Número mínimo de días para asignar evaluación (por defecto 30 días)',
        )
        parser.add_argument(
            '--dias-maximos',
            type=int,
            default=60,
            help='Número máximo de días para asignar evaluación (por defecto 60 días)',
        )

    def handle(self, **options):
        dry_run = options['dry_run']
        dias_minimos = options['dias_minimos']
        dias_maximos = options['dias_maximos']

        # Obtener configuración necesaria
        try:
            estado_prueba = EstadoEmpleado.objects.get(codigo='p-prue')
            tipo_evaluacion = TipoEvaluacion.objects.get(codigo='PERIODO_PRUEBA')
            evaluacion = EvaluacionDesempeño.objects.filter(
                tipo_evaluacion=tipo_evaluacion,
                activa=True
            ).first()

            if not evaluacion:
                self.stdout.write(
                    self.style.ERROR('Error: No se encontró evaluación activa de período de prueba')
                )
                return

        except (EstadoEmpleado.DoesNotExist, TipoEvaluacion.DoesNotExist) as e:
            self.stdout.write(
                self.style.ERROR(f'Error: No se encontraron las configuraciones necesarias: {e}')
            )
            return

        # Calcular fechas límite
        fecha_hoy = timezone.now().date()
        fecha_limite_minima = fecha_hoy - timedelta(days=dias_maximos)  # Hace 60 días
        fecha_limite_maxima = fecha_hoy - timedelta(days=dias_minimos)  # Hace 30 días

        # Buscar empleados elegibles (entre 30 y 60 días)
        empleados_candidatos = Empleado.objects.filter(
            estado=estado_prueba,
            fecha_ingreso__gte=fecha_limite_minima,
            fecha_ingreso__lte=fecha_limite_maxima
        ).select_related('sede')

        total_candidatos = empleados_candidatos.count()

        if total_candidatos == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay empleados en período de prueba con 30-60 días de servicio.')
            )
            return

        self.stdout.write(
            self.style.WARNING(f'Encontrados {total_candidatos} empleados elegibles para evaluación:')
        )

        asignaciones_creadas = []
        asignaciones_existentes = []
        sin_jefe_directo = []
        empleados_con_error = []

        for empleado in empleados_candidatos:
            dias_transcurridos = (fecha_hoy - empleado.fecha_ingreso).days
            periodo_evaluacion = f"{empleado.fecha_ingreso.year}-PP"

            self.stdout.write(
                f'\n- {empleado.nombre_completo} (Doc: {empleado.numero_documento})'
            )
            self.stdout.write(
                f'  Fecha ingreso: {empleado.fecha_ingreso} '
                f'({dias_transcurridos} días transcurridos)'
            )
            self.stdout.write(
                f'  Sede: {empleado.sede}'
            )

            # Verificar si ya tiene asignación
            existe_asignacion = AsignacionEvaluacion.objects.filter(
                empleado_evaluado=empleado,
                evaluacion=evaluacion,
                periodo_evaluacion=periodo_evaluacion
            ).exists()

            if existe_asignacion:
                asignaciones_existentes.append(empleado)
                self.stdout.write(
                    self.style.WARNING(f'  [!] Ya tiene evaluacion asignada - NO SE CREARA OTRA')
                )
                continue

            # Buscar jefe directo desde HistorialCargo
            jefe_directo = self._buscar_jefe_directo(empleado)

            if not jefe_directo:
                sin_jefe_directo.append(empleado)
                self.stdout.write(
                    self.style.WARNING(f'  [!] No se encontro jefe directo - NO SE ASIGNARA')
                )
                continue

            self.stdout.write(
                f'  Jefe directo: {jefe_directo.nombre_completo}'
            )

            # Calcular fecha de vencimiento (15 días después de asignación)
            fecha_vencimiento = fecha_hoy + timedelta(days=15)

            if not dry_run:
                try:
                    # Crear asignación
                    AsignacionEvaluacion.objects.create(
                        empleado_evaluado=empleado,
                        evaluacion=evaluacion,
                        evaluador=jefe_directo,
                        periodo_evaluacion=periodo_evaluacion,
                        fecha_vencimiento=fecha_vencimiento,
                        estado='pendiente',
                        es_autoevaluacion=False,
                    )

                    asignaciones_creadas.append(empleado)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  [OK] Evaluacion asignada - Vence: {fecha_vencimiento}'
                        )
                    )

                    # Log para auditoría
                    logger.info(
                        f'Evaluación de período de prueba asignada a {empleado.numero_documento} '
                        f'({empleado.nombre_completo}) con {dias_transcurridos} días de servicio. '
                        f'Evaluador: {jefe_directo.nombre_completo}'
                    )

                except Exception as e:
                    empleados_con_error.append((empleado, str(e)))
                    self.stdout.write(
                        self.style.ERROR(f'  [X] Error al asignar evaluacion: {e}')
                    )
                    logger.error(
                        f'Error al asignar evaluación a empleado {empleado.numero_documento}: {e}'
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  > Se asignaria evaluacion (DRY RUN)')
                )
                self.stdout.write(
                    f'    Evaluador: {jefe_directo.nombre_completo}'
                )
                self.stdout.write(
                    f'    Vencimiento: {fecha_vencimiento}'
                )

        # Resumen final
        if dry_run:
            total_asignables = total_candidatos - len(asignaciones_existentes) - len(sin_jefe_directo)
            self.stdout.write('\n' + '='*60)
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN completado. Se asignarían {total_asignables} evaluaciones de {total_candidatos} candidatos.'
                )
            )
        else:
            creadas = len(asignaciones_creadas)
            existentes = len(asignaciones_existentes)
            sin_jefe = len(sin_jefe_directo)
            errores = len(empleados_con_error)

            self.stdout.write('\n' + '='*60)
            self.stdout.write('RESUMEN DE ASIGNACIONES:')
            self.stdout.write(
                self.style.SUCCESS(f'[OK] Evaluaciones asignadas: {creadas}')
            )
            self.stdout.write(
                self.style.WARNING(f'[!] Ya tenian evaluacion: {existentes}')
            )
            self.stdout.write(
                self.style.WARNING(f'[!] Sin jefe directo: {sin_jefe}')
            )
            if errores > 0:
                self.stdout.write(
                    self.style.ERROR(f'[ERROR] Errores tecnicos: {errores}')
                )
                for empleado, error in empleados_con_error:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  - {empleado.nombre_completo}: {error}'
                        )
                    )

        # Información adicional sobre configuración
        self.stdout.write('\n' + '='*60)
        self.stdout.write('CONFIGURACION UTILIZADA:')
        self.stdout.write(f'- Días mínimos de servicio: {dias_minimos}')
        self.stdout.write(f'- Días máximos de servicio: {dias_maximos}')
        self.stdout.write(f'- Rango de fechas de ingreso: {fecha_limite_minima} a {fecha_limite_maxima}')
        self.stdout.write(f'- Estado empleado: {estado_prueba.nombre} ({estado_prueba.codigo})')
        self.stdout.write(f'- Tipo evaluación: {tipo_evaluacion.nombre} ({tipo_evaluacion.codigo})')
        self.stdout.write(f'- Evaluación: {evaluacion.nombre}')
        self.stdout.write(f'- Días para vencimiento: 15 días')
        self.stdout.write('='*60)

    def _buscar_jefe_directo(self, empleado):
        """
        Busca el jefe directo del empleado desde su historial de cargo actual.

        Returns:
            Empleado: El jefe directo si existe, None en caso contrario
        """
        from apps.employees.models import HistorialCargo

        try:
            # Buscar historial de cargo activo del empleado
            historial_activo = HistorialCargo.objects.filter(
                empleado=empleado,
                activo=True
            ).select_related('jefe_directo').first()

            if historial_activo and historial_activo.jefe_directo:
                jefe = historial_activo.jefe_directo

                # Verificar que el jefe esté activo
                if jefe.estado.codigo in ['999', 'ACTIVO', 'Activo', 'activo']:
                    return jefe
                else:
                    logger.warning(
                        f'El jefe directo {jefe.nombre_completo} del empleado '
                        f'{empleado.nombre_completo} no está activo (estado: {jefe.estado.codigo})'
                    )
                    return None

            logger.warning(
                f'No se encontró jefe directo para empleado {empleado.nombre_completo} '
                f'(ID: {empleado.id})'
            )
            return None

        except Exception as e:
            logger.error(
                f'Error buscando jefe directo para empleado {empleado.id}: {e}'
            )
            return None
