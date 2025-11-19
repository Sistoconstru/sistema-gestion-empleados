# =============================================================================
# apps/evaluations/management/commands/generar_respuestas_periodo_prueba.py
# Comando para generar respuestas de ejemplo para evaluaciones de período de prueba
# =============================================================================

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import random

from apps.evaluations.models import (
    AsignacionEvaluacion, RespuestaEvaluacion, PreguntaEvaluacion, 
    OpcionEvaluacion, ResultadoEvaluacion
)
from apps.employees.models import Empleado


class Command(BaseCommand):
    help = 'Genera respuestas de ejemplo para evaluaciones de período de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empleado-id',
            type=str,
            help='ID específico de empleado para generar respuestas',
        )
        parser.add_argument(
            '--tipo-perfil',
            type=str,
            choices=['excelente', 'bueno', 'regular', 'deficiente'],
            default='bueno',
            help='Tipo de perfil del empleado para las respuestas',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula las respuestas sin guardar en la base de datos',
        )

    def handle(self, *args, **options):
        empleado_id = options['empleado_id']
        tipo_perfil = options['tipo_perfil']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'🎯 Generando Respuestas de Período de Prueba - Perfil: {tipo_perfil.upper()}')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🧪 MODO SIMULACIÓN - No se guardará nada'))
        
        # Buscar asignaciones de evaluación pendientes
        asignaciones = self._buscar_asignaciones_pendientes(empleado_id)
        
        if not asignaciones:
            self.stdout.write(self.style.WARNING('❌ No se encontraron evaluaciones pendientes'))
            return
        
        total_generadas = 0
        
        for asignacion in asignaciones:
            try:
                if not dry_run:
                    respuestas_generadas = self._generar_respuestas(asignacion, tipo_perfil)
                    total_generadas += respuestas_generadas
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ {respuestas_generadas} respuestas generadas para {asignacion.empleado_evaluado.nombre_completo}'
                        )
                    )
                else:
                    # Modo simulación
                    preguntas = PreguntaEvaluacion.objects.filter(evaluacion=asignacion.evaluacion).count()
                    total_generadas += preguntas
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'🧪 SIMULARÍA: {preguntas} respuestas para {asignacion.empleado_evaluado.nombre_completo}'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error generando respuestas para {asignacion.empleado_evaluado.nombre_completo}: {e}')
                )
        
        self._mostrar_resumen(total_generadas, len(asignaciones), dry_run)

    def _buscar_asignaciones_pendientes(self, empleado_id=None):
        """Buscar asignaciones de evaluación pendientes de período de prueba"""
        
        query_filters = {
            'evaluacion__codigo': 'EVAL_PERIODO_PRUEBA_2024',
            'estado__in': ['pendiente', 'en_progreso']
        }
        
        if empleado_id:
            query_filters['empleado_evaluado__id'] = empleado_id
        
        asignaciones = AsignacionEvaluacion.objects.filter(**query_filters).select_related(
            'empleado_evaluado', 'evaluacion', 'evaluador'
        )
        
        self.stdout.write(f'📋 Asignaciones encontradas: {asignaciones.count()}')
        
        for asignacion in asignaciones:
            self.stdout.write(f'  ✓ {asignacion.empleado_evaluado.nombre_completo} - Estado: {asignacion.estado}')
        
        return asignaciones

    def _generar_respuestas(self, asignacion, tipo_perfil):
        """Generar respuestas para una asignación específica"""
        
        with transaction.atomic():
            # Obtener preguntas de la evaluación
            preguntas = PreguntaEvaluacion.objects.filter(
                evaluacion=asignacion.evaluacion
            ).order_by('orden')
            
            respuestas_generadas = 0
            puntaje_total = Decimal('0')
            
            for pregunta in preguntas:
                # Obtener opciones de respuesta
                opciones = OpcionEvaluacion.objects.filter(
                    pregunta=pregunta
                ).order_by('valor_numerico')
                
                # Seleccionar respuesta basada en el perfil
                opcion_seleccionada = self._seleccionar_respuesta_por_perfil(
                    pregunta, opciones, tipo_perfil
                )
                
                # Generar comentarios realistas
                comentarios = self._generar_comentarios_evaluador(pregunta, opcion_seleccionada)
                
                # Crear o actualizar respuesta
                respuesta, created = RespuestaEvaluacion.objects.get_or_create(
                    asignacion=asignacion,
                    pregunta=pregunta,
                    defaults={
                        'opcion_seleccionada': opcion_seleccionada,
                        'respuesta_texto': '',
                        'puntaje_obtenido': opcion_seleccionada.valor_numerico,
                        'comentarios_evaluador': comentarios
                    }
                )
                
                if not created:
                    # Actualizar si ya existe
                    respuesta.opcion_seleccionada = opcion_seleccionada
                    respuesta.puntaje_obtenido = opcion_seleccionada.valor_numerico
                    respuesta.comentarios_evaluador = comentarios
                    respuesta.save()
                
                puntaje_total += opcion_seleccionada.valor_numerico
                respuestas_generadas += 1
            
            # Actualizar asignación
            asignacion.estado = 'completada'
            asignacion.puntaje_total = puntaje_total
            asignacion.porcentaje_completado = Decimal('100')
            asignacion.save()
            
            # Generar resultado automático
            self._generar_resultado_evaluacion(asignacion, puntaje_total)
            
        return respuestas_generadas

    def _seleccionar_respuesta_por_perfil(self, pregunta, opciones, tipo_perfil):
        """Seleccionar respuesta basada en el perfil del empleado"""
        
        opciones_list = list(opciones)
        
        if tipo_perfil == 'excelente':
            # 80% probabilidad de "Cumple totalmente", 20% "Cumple parcialmente"
            return random.choices(
                opciones_list, 
                weights=[5, 20, 80], 
                k=1
            )[0] if len(opciones_list) == 3 else opciones_list[-1]
            
        elif tipo_perfil == 'bueno':
            # 50% "Cumple totalmente", 40% "Cumple parcialmente", 10% "No cumple"
            return random.choices(
                opciones_list, 
                weights=[10, 40, 50], 
                k=1
            )[0] if len(opciones_list) == 3 else opciones_list[1]
            
        elif tipo_perfil == 'regular':
            # 20% "Cumple totalmente", 60% "Cumple parcialmente", 20% "No cumple"
            return random.choices(
                opciones_list, 
                weights=[20, 60, 20], 
                k=1
            )[0] if len(opciones_list) == 3 else opciones_list[1]
            
        elif tipo_perfil == 'deficiente':
            # 10% "Cumple totalmente", 30% "Cumple parcialmente", 60% "No cumple"
            return random.choices(
                opciones_list, 
                weights=[60, 30, 10], 
                k=1
            )[0] if len(opciones_list) == 3 else opciones_list[0]
        
        # Por defecto, seleccionar al azar
        return random.choice(opciones_list)

    def _generar_comentarios_evaluador(self, pregunta, opcion_seleccionada):
        """Generar comentarios realistas del evaluador"""
        
        comentarios_por_pregunta = {
            'Trabajo en equipo': {
                1: 'Muestra dificultades para integrarse y colaborar efectivamente con el equipo.',
                2: 'Se integra al equipo pero necesita mejorar su nivel de colaboración.',
                3: 'Excelente colaborador, se integra naturalmente y aporta positivamente al equipo.'
            },
            'Compromiso': {
                1: 'Falta mayor compromiso e involucramiento con los objetivos del área.',
                2: 'Demuestra compromiso básico pero puede incrementar su nivel de involucramiento.',
                3: 'Altamente comprometido, muestra iniciativa y se involucra activamente en los objetivos.'
            },
            'Comunicación': {
                1: 'Presenta dificultades en la comunicación y necesita mejorar sus habilidades de expresión.',
                2: 'Comunica adecuadamente pero puede mejorar la claridad y precisión de sus mensajes.',
                3: 'Excelente comunicador, se expresa claramente y escucha activamente.'
            },
            'Atención al detalle': {
                1: 'Requiere mayor atención a los detalles en la ejecución de sus tareas.',
                2: 'Generalmente atiende los detalles pero ocasionalmente pasa por alto aspectos importantes.',
                3: 'Muy detallista, revisa cuidadosamente su trabajo y mantiene altos estándares de precisión.'
            },
            'Cumplimiento de las normas y procedimientos': {
                1: 'Necesita mejorar el cumplimiento de normas y procedimientos establecidos.',
                2: 'Cumple las normas básicas pero requiere refuerzo en algunos procedimientos específicos.',
                3: 'Cumple diligentemente todas las normas y procedimientos, es ejemplo para otros.'
            },
            'Actitud respecto al trabajo': {
                1: 'Su actitud hacia el trabajo necesita mejoras significativas.',
                2: 'Mantiene una actitud aceptable pero puede mostrar mayor entusiasmo y positividad.',
                3: 'Excelente actitud, siempre positivo y entusiasta hacia las responsabilidades asignadas.'
            },
            'Calidad': {
                1: 'La calidad de su trabajo requiere mejoras importantes y mayor cuidado.',
                2: 'Entrega trabajos de calidad aceptable pero puede mejorar la precisión y presentación.',
                3: 'Entrega trabajos de excelente calidad, con esmero y atención a los estándares requeridos.'
            }
        }
        
        # Buscar comentarios por título de pregunta
        for key, comentarios in comentarios_por_pregunta.items():
            if key.lower() in pregunta.pregunta.lower():
                return comentarios.get(int(opcion_seleccionada.valor_numerico), 
                                     'Evaluación registrada correctamente.')
        
        # Comentarios genéricos si no se encuentra coincidencia
        comentarios_genericos = {
            1: 'Requiere mejoras en este aspecto para alcanzar el nivel esperado.',
            2: 'Cumple de manera aceptable pero tiene potencial de mejora.',
            3: 'Cumple completamente con las expectativas en este aspecto.'
        }
        
        return comentarios_genericos.get(int(opcion_seleccionada.valor_numerico), 
                                       'Evaluación completada.')

    def _generar_resultado_evaluacion(self, asignacion, puntaje_total):
        """Generar resultado consolidado de la evaluación"""
        
        # Calcular porcentaje (sobre 21 puntos máximos)
        puntaje_maximo = Decimal('21')  # 7 preguntas x 3 puntos
        porcentaje = (puntaje_total / puntaje_maximo) * 100
        
        # Determinar nivel de desempeño
        if puntaje_total >= 19:
            nivel = 'excelente'
            aspectos_positivos = 'Empleado excepcional que cumple totalmente con todos los aspectos evaluados. Demuestra un desempeño sobresaliente en el período de prueba.'
            areas_mejora = 'Continuar manteniendo este excelente nivel de desempeño.'
        elif puntaje_total >= 16:
            nivel = 'sobresaliente'
            aspectos_positivos = 'Empleado con muy buen desempeño que cumple satisfactoriamente con la mayoría de aspectos evaluados.'
            areas_mejora = 'Continuar desarrollando las competencias para alcanzar un nivel excelente.'
        elif puntaje_total >= 14:
            nivel = 'satisfactorio'
            aspectos_positivos = 'Empleado que cumple con los requisitos básicos del período de prueba.'
            areas_mejora = 'Fortalecer las competencias que obtuvieron menor puntaje para mejorar el desempeño general.'
        else:
            nivel = 'insatisfactorio'
            aspectos_positivos = 'Se identifican algunas fortalezas pero requiere mejoras significativas.'
            areas_mejora = 'Requiere plan de mejora inmediato en múltiples competencias evaluadas.'
        
        # Crear o actualizar resultado
        resultado, created = ResultadoEvaluacion.objects.get_or_create(
            asignacion=asignacion,
            defaults={
                'puntaje_final': puntaje_total,
                'porcentaje_obtenido': porcentaje,
                'nivel_desempeño': nivel,
                'aspectos_positivos': aspectos_positivos,
                'areas_mejora': areas_mejora,
                'comentarios_generales': f'Evaluación de período de prueba completada. Puntaje: {puntaje_total}/21.',
                'generado_por': asignacion.evaluador.usuario if asignacion.evaluador else asignacion.asignado_por
            }
        )
        
        if not created:
            resultado.puntaje_final = puntaje_total
            resultado.porcentaje_obtenido = porcentaje
            resultado.nivel_desempeño = nivel
            resultado.aspectos_positivos = aspectos_positivos
            resultado.areas_mejora = areas_mejora
            resultado.save()

    def _mostrar_resumen(self, total_respuestas, total_evaluaciones, dry_run):
        """Mostrar resumen de la operación"""
        self.stdout.write('\n' + '='*60)
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'🧪 SIMULACIÓN COMPLETADA:')
            )
            self.stdout.write(f'   - {total_respuestas} respuestas simuladas')
            self.stdout.write(f'   - {total_evaluaciones} evaluaciones procesadas')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ GENERACIÓN COMPLETADA:')
            )
            self.stdout.write(f'   - {total_respuestas} respuestas generadas')
            self.stdout.write(f'   - {total_evaluaciones} evaluaciones completadas')
            
        self.stdout.write('\n📋 PRÓXIMOS PASOS:')
        self.stdout.write('   1. Las evaluaciones están listas para aprobación administrativa')
        self.stdout.write('   2. Revisar resultados en: /evaluaciones/admin/pendientes-aprobacion/')
        self.stdout.write('   3. Los puntajes se calcularon automáticamente')
        
        self.stdout.write('\n🔗 ENLACES ÚTILES:')
        self.stdout.write('   - Ver evaluaciones: /evaluaciones/')
        self.stdout.write('   - Admin aprobaciones: /admin/evaluations/asignacionevaluacion/')
        self.stdout.write('='*60)