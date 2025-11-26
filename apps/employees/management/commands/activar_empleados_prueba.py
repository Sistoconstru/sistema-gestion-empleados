from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.employees.models import Empleado, EstadoEmpleado
from apps.evaluations.models import AsignacionEvaluacion
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Activa automáticamente empleados que han completado su periodo de prueba de 3 meses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta el comando sin hacer cambios reales, solo muestra qué se haría',
        )
        parser.add_argument(
            '--dias-periodo',
            type=int,
            default=60,
            help='Número de días del periodo de prueba (por defecto 60 días = 2 meses)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        dias_periodo = options['dias_periodo']
        
        # Obtener estados
        try:
            estado_prueba = EstadoEmpleado.objects.get(codigo='p-prue')
            
            # Buscar estado activo entre diferentes códigos posibles
            estado_activo = None
            codigos_activo = ['999', 'ACTIVO', 'Activo', 'activo']
            for codigo in codigos_activo:
                try:
                    estado_activo = EstadoEmpleado.objects.get(codigo=codigo)
                    break
                except EstadoEmpleado.DoesNotExist:
                    continue
                    
            if not estado_activo:
                raise EstadoEmpleado.DoesNotExist("No se encontró ningún estado activo válido")
                
        except EstadoEmpleado.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f'Error: No se encontraron los estados necesarios: {e}')
            )
            return

        # Calcular fecha límite (hace 2 meses)
        fecha_limite = timezone.now().date() - timedelta(days=dias_periodo)
        
        # Buscar empleados en periodo de prueba que cumplen el tiempo
        empleados_a_activar = Empleado.objects.filter(
            estado=estado_prueba,
            fecha_ingreso__lte=fecha_limite
        ).select_related('estado', 'sede')
        
        total_empleados = empleados_a_activar.count()
        
        if total_empleados == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay empleados en periodo de prueba que cumplan los 2 meses.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Encontrados {total_empleados} empleados para activar:')
        )
        
        empleados_activados = []
        empleados_con_error = []
        empleados_sin_evaluacion = []
        empleados_evaluacion_insatisfactoria = []
        
        for empleado in empleados_a_activar:
            dias_transcurridos = (timezone.now().date() - empleado.fecha_ingreso).days
            
            self.stdout.write(
                f'- {empleado.nombre_completo} (Doc: {empleado.numero_documento})'
            )
            self.stdout.write(
                f'  Fecha ingreso: {empleado.fecha_ingreso} '
                f'({dias_transcurridos} días transcurridos)'
            )
            self.stdout.write(
                f'  Sede: {empleado.sede}'
            )
            
            # VALIDACIÓN DE EVALUACIÓN DE PERIODO DE PRUEBA
            evaluacion_valida = self._verificar_evaluacion_periodo_prueba(empleado)
            
            if evaluacion_valida['estado'] == 'sin_evaluacion':
                empleados_sin_evaluacion.append(empleado)
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️ Sin evaluación de periodo de prueba - NO SE ACTIVARÁ')
                )
                continue
                
            elif evaluacion_valida['estado'] == 'pendiente':
                empleados_sin_evaluacion.append(empleado)
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️ Evaluación pendiente de completar - NO SE ACTIVARÁ')
                )
                continue
                
            elif evaluacion_valida['estado'] == 'insatisfactorio':
                empleados_evaluacion_insatisfactoria.append(empleado)
                puntaje = evaluacion_valida['puntaje']
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Evaluación insatisfactoria ({puntaje:.0f}/21 puntos) - NO SE ACTIVARÁ')
                )
                continue

            elif evaluacion_valida['estado'] == 'satisfactorio':
                puntaje = evaluacion_valida['puntaje']
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Evaluación satisfactoria ({puntaje:.0f}/21 puntos) - PROCEDE ACTIVACIÓN')
                )
            
            if not dry_run:
                try:
                    # Cambiar estado a activo
                    empleado.estado = estado_activo
                    empleado.save()
                    
                    empleados_activados.append(empleado)
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Activado exitosamente')
                    )
                    
                    # Log para auditoría
                    logger.info(
                        f'Empleado {empleado.numero_documento} '
                        f'({empleado.nombre_completo}) activado automáticamente '
                        f'después de {dias_transcurridos} días con evaluación satisfactoria '
                        f'(puntaje: {evaluacion_valida["puntaje"]:.0f}/21 puntos)'
                    )
                    
                except Exception as e:
                    empleados_con_error.append((empleado, str(e)))
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Error al activar: {e}')
                    )
                    logger.error(
                        f'Error al activar empleado {empleado.numero_documento}: {e}'
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  → Se activaría (DRY RUN)')
                )
            
            self.stdout.write('')  # Línea en blanco para separar
        
        # Resumen final
        if dry_run:
            activados = total_empleados - len(empleados_sin_evaluacion) - len(empleados_evaluacion_insatisfactoria)
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN completado. Se activarían {activados} empleados de {total_empleados} candidatos.'
                )
            )
        else:
            activados = len(empleados_activados)
            errores = len(empleados_con_error)
            sin_evaluacion = len(empleados_sin_evaluacion)
            evaluacion_insatisfactoria = len(empleados_evaluacion_insatisfactoria)
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write('📊 RESUMEN DE ACTIVACIONES:')
            self.stdout.write(
                self.style.SUCCESS(f'✅ Empleados activados: {activados}')
            )
            self.stdout.write(
                self.style.WARNING(f'⚠️ Sin evaluación/pendiente: {sin_evaluacion}')
            )
            self.stdout.write(
                self.style.ERROR(f'❌ Evaluación insatisfactoria: {evaluacion_insatisfactoria}')
            )
            if errores > 0:
                self.stdout.write(
                    self.style.ERROR(f'💥 Errores técnicos: {errores}')
                )
                for empleado, error in empleados_con_error:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  - {empleado.nombre_completo}: {error}'
                        )
                    )
        
        # Información adicional sobre configuración
        self.stdout.write('\n' + '='*60)
        self.stdout.write('⚙️ CONFIGURACIÓN UTILIZADA:')
        self.stdout.write(f'- Días de periodo de prueba: {dias_periodo}')
        self.stdout.write(f'- Fecha límite de ingreso: {fecha_limite}')
        self.stdout.write(f'- Estado origen: {estado_prueba.nombre} ({estado_prueba.codigo})')
        self.stdout.write(f'- Estado destino: {estado_activo.nombre} ({estado_activo.codigo})')
        self.stdout.write(f'- Validación de evaluación: ✅ ACTIVADA')
        self.stdout.write('='*60)

    def _verificar_evaluacion_periodo_prueba(self, empleado):
        """
        Verifica si el empleado tiene una evaluación de período de prueba completada
        y si el resultado es satisfactorio (puntaje_total >= 14 puntos)

        El puntaje se calcula por SUMA de respuestas (no promedio):
        - Evaluación tiene 7 preguntas
        - Cada pregunta se valora de 1 a 3
        - Puntaje máximo: 21 puntos (7 * 3)
        - Puntaje mínimo aprobatorio: 14 puntos

        Returns:
            dict: {
                'estado': 'sin_evaluacion'|'pendiente'|'satisfactorio'|'insatisfactorio',
                'puntaje': float|None,
                'asignacion': AsignacionEvaluacion|None
            }
        """
        try:
            # Buscar asignación de evaluación de período de prueba
            periodo_evaluacion = f"{empleado.fecha_ingreso.year}-PP"
            asignacion = AsignacionEvaluacion.objects.filter(
                empleado_evaluado=empleado,
                periodo_evaluacion=periodo_evaluacion,
                evaluacion__tipo_evaluacion__codigo='PERIODO_PRUEBA'
            ).first()

            if not asignacion:
                return {
                    'estado': 'sin_evaluacion',
                    'puntaje': None,
                    'asignacion': None
                }

            # Verificar si está completada
            if asignacion.estado != 'completada':
                return {
                    'estado': 'pendiente',
                    'puntaje': None,
                    'asignacion': asignacion
                }

            # Obtener puntaje total (suma de respuestas)
            puntaje_total = None

            # Primero intentar obtener de AsignacionEvaluacion.puntaje_total
            if asignacion.puntaje_total:
                puntaje_total = float(asignacion.puntaje_total)
            else:
                # Si no existe, intentar calcular manualmente
                puntaje_total = self._calcular_puntaje_suma(asignacion)

            if puntaje_total is None:
                return {
                    'estado': 'sin_evaluacion',
                    'puntaje': None,
                    'asignacion': asignacion
                }

            # Satisfactorio > 13 puntos (umbral de aprobación)
            if puntaje_total > 13:
                return {
                    'estado': 'satisfactorio',
                    'puntaje': puntaje_total,
                    'asignacion': asignacion
                }
            else:
                return {
                    'estado': 'insatisfactorio',
                    'puntaje': puntaje_total,
                    'asignacion': asignacion
                }

        except Exception as e:
            logger.error(f"Error verificando evaluación para empleado {empleado.id}: {e}")
            return {
                'estado': 'sin_evaluacion',
                'puntaje': None,
                'asignacion': None
            }

    def _calcular_puntaje_suma(self, asignacion):
        """
        Calcula el puntaje total por SUMA de respuestas (no promedio)

        Para evaluaciones de período de prueba:
        - 7 preguntas
        - Cada respuesta vale de 1 a 3 puntos
        - Puntaje total = suma de todas las respuestas
        """
        from apps.evaluations.models import RespuestaEvaluacion
        from decimal import Decimal

        try:
            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion=asignacion
            ).select_related('opcion_seleccionada', 'pregunta')

            if not respuestas.exists():
                return 0.0

            puntaje_total = Decimal('0.00')

            for respuesta in respuestas:
                if respuesta.opcion_seleccionada:
                    valor = respuesta.opcion_seleccionada.valor_numerico
                    puntaje_total += Decimal(str(valor))
                elif respuesta.puntaje_obtenido:
                    puntaje_total += Decimal(str(respuesta.puntaje_obtenido))

            return float(puntaje_total)

        except Exception as e:
            logger.error(f"Error calculando puntaje suma de evaluación {asignacion.id}: {e}")
            return 0.0