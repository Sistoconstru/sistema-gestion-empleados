# =============================================================================
# apps/evaluations/management/commands/configurar_evaluacion_periodo_prueba.py
# Configuración específica para evaluación de período de prueba con 7 preguntas del Excel
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta

from apps.evaluations.models import (
    TipoPregunta, TipoEvaluacion, EvaluacionDesempeño, 
    PreguntaEvaluacion, OpcionEvaluacion
)
from apps.authentication.models import Usuario


class Command(BaseCommand):
    help = 'Configura la evaluación de período de prueba con las 7 preguntas exactas del Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recrear',
            action='store_true',
            help='Elimina evaluación existente y la recrea',
        )

    def handle(self, *args, **options):
        recrear = options['recrear']
        
        self.stdout.write(
            self.style.SUCCESS('🎯 Configurando Evaluación de Período de Prueba - Excel')
        )
        
        # 1. Verificar tipos básicos
        self._verificar_tipos_basicos()
        
        # 2. Crear evaluación de período de prueba
        self._crear_evaluacion_periodo_prueba(recrear)

        self.stdout.write(
            self.style.SUCCESS('✅ Evaluación de período de prueba configurada exitosamente')
        )

    def _verificar_tipos_basicos(self):
        """Verificar que existan los tipos básicos necesarios"""
        # Verificar que existe TipoPregunta ESCALA_3
        try:
            tipo_pregunta = TipoPregunta.objects.get(codigo='ESCALA_3')
            self.stdout.write('  ✓ TipoPregunta ESCALA_3 encontrado')
        except TipoPregunta.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ TipoPregunta ESCALA_3 no existe')
            )
            self.stdout.write(
                self.style.WARNING('💡 Ejecute: python manage.py crear_tipos_pregunta_estandar')
            )
            raise ValueError("Tipos de pregunta no configurados")
        
        # Verificar TipoEvaluacion
        tipo_evaluacion, created = TipoEvaluacion.objects.get_or_create(
            codigo='PERIODO_PRUEBA',
            defaults={
                'nombre': 'Evaluación de Período de Prueba',
                'descripcion': 'Evaluación realizada a empleados al cumplir 30 días en la empresa',
                'dias_activacion': 30,  # Se asigna a los 30 días
                'frecuencia_dias': None,  # No es periódica
                'es_autoevaluacion': False,
                'activo': True
            }
        )
        if created:
            self.stdout.write('  ✓ TipoEvaluacion PERIODO_PRUEBA creado')

    def _crear_evaluacion_periodo_prueba(self, recrear):
        """Crear la evaluación de período de prueba con las 7 preguntas exactas del Excel"""
        
        # Obtener usuario sistema
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(self.style.ERROR('❌ No se encontró usuario administrador'))
            return
        
        # Obtener tipos necesarios
        tipo_evaluacion = TipoEvaluacion.objects.get(codigo='PERIODO_PRUEBA')
        tipo_pregunta = TipoPregunta.objects.get(codigo='ESCALA_3')
        
        # Crear o actualizar evaluación
        evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
            codigo='EVAL_PERIODO_PRUEBA_2024',
            defaults={
                'nombre': 'Evaluación de Período de Prueba',
                'descripcion': 'Evaluación integral para empleados en período de prueba - 30 días',
                'instrucciones': '''EVALUACIÓN EN PERÍODO DE PRUEBA

Esta evaluación debe realizarse al cumplir 30 días en la empresa.

CRITERIOS DE EVALUACIÓN:
• De 1 a 13 puntos: El empleado NO continúa en el cargo
• De 14 a 21 puntos: El empleado continúa en el cargo

ESCALA DE PUNTUACIÓN:
• 1 = No cumple: No tiene comportamientos relacionados con este aspecto
• 2 = Cumple parcialmente: De manera periódica tiene comportamientos relacionados con este aspecto  
• 3 = Cumple totalmente: Se evidencia siempre este comportamiento

La evaluación final se debe realizar 5 días hábiles antes de la terminación del período de prueba.''',
                'tipo_evaluacion': tipo_evaluacion,
                'version': '2024.1',
                'activa': True,
                'creada_por': usuario_sistema
            }
        )
        
        if recrear and not created:
            # Eliminar preguntas existentes
            PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).delete()
            self.stdout.write('  🗑️ Preguntas existentes eliminadas')
        
        if created or recrear:
            self.stdout.write(f'  ✓ Evaluación: {evaluacion.nombre}')
            self._crear_preguntas_excel(evaluacion, tipo_pregunta)
        else:
            self.stdout.write(f'  → Evaluación existente: {evaluacion.nombre}')

    def _crear_preguntas_excel(self, evaluacion, tipo_pregunta):
        """Crear las 7 preguntas exactas del Excel"""
        
        # 7 PREGUNTAS EXACTAS DEL DOCUMENTO EXCEL
        preguntas_excel = [
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Trabajo en equipo',
                'descripcion': 'Desarrolla labores con sus compañeros es conciliador y respetuoso de las diferencias.',
                'peso_porcentual': 14.29,  # 1/7 ≈ 14.29%
                'orden': 1
            },
            {
                'categoria': 'Actitud y Compromiso',
                'pregunta': 'Compromiso',
                'descripcion': 'Se muestra colaborador y abierto a ayudar a conseguir objetivos generales del proceso, aunque deba invertir mas tiempo y esfuerzo en ello, asume de manera autonoma actividades que pueda hacer para lograr una meta.',
                'peso_porcentual': 14.29,
                'orden': 2
            },
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Comunicación',
                'descripcion': 'Tiene la Capacidad de expresarse coherentemente, darse a entender y llegar a un acuerdo, sabe escuchar.',
                'peso_porcentual': 14.29,
                'orden': 3
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Atención al detalle',
                'descripcion': 'Tiene una actitud de observacion constante para mejorar su proceso o tarea sin pasar por alto detalles que podrian mejorar una actividad, se muestra interesado en atender pequeños detalles.',
                'peso_porcentual': 14.29,
                'orden': 4
            },
            {
                'categoria': 'Cumplimiento Organizacional',
                'pregunta': 'Cumplimiento de las normas y procedimientos',
                'descripcion': 'Su actuar se encamina a cumplir de manera diligente, rapida y eficiente las obligaciones, normas y procedimientos establecidos por la empresa, no tiene amonestaciones por incumplimientos relacionados con este tema.',
                'peso_porcentual': 14.29,
                'orden': 5
            },
            {
                'categoria': 'Actitud y Compromiso',
                'pregunta': 'Actitud respecto al trabajo',
                'descripcion': 'Tiene una actitud positiva respecto a su trabajo, a la empresa y para el desarrollo del trabajo.',
                'peso_porcentual': 14.29,
                'orden': 6
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Calidad',
                'descripcion': 'Los trabajos que desarrolla estan acordes a lo exigido, sin errores repetitivos y con una evidente muestra de cuidado y esmero.',
                'peso_porcentual': 14.28,  # 14.28 para que sume exactamente 100%
                'orden': 7
            }
        ]
        
        self.stdout.write('  📊 Creando las 7 preguntas del Excel...')
        
        for pregunta_data in preguntas_excel:
            pregunta = PreguntaEvaluacion.objects.create(
                evaluacion=evaluacion,
                tipo_pregunta=tipo_pregunta,
                categoria=pregunta_data['categoria'],
                pregunta=pregunta_data['pregunta'],
                descripcion=pregunta_data['descripcion'],
                peso_porcentual=pregunta_data['peso_porcentual'],
                orden=pregunta_data['orden'],
                obligatoria=True,
                activa=True
            )
            
            # Crear las 3 opciones de respuesta exactas del Excel
            self._crear_opciones_respuesta(pregunta)
            
            self.stdout.write(f'    ✓ {pregunta.orden}. {pregunta.pregunta}')
        
        self.stdout.write(f'  ✅ {len(preguntas_excel)} preguntas creadas exitosamente')

    def _crear_opciones_respuesta(self, pregunta):
        """Crear las 3 opciones exactas del Excel para cada pregunta"""
        opciones_excel = [
            {
                'opcion': 'No cumple',
                'valor_numerico': 1.00,
                'orden': 1
            },
            {
                'opcion': 'Cumple parcialmente',
                'valor_numerico': 2.00,
                'orden': 2
            },
            {
                'opcion': 'Cumple totalmente',
                'valor_numerico': 3.00,
                'orden': 3
            }
        ]
        
        for opcion_data in opciones_excel:
            OpcionEvaluacion.objects.create(
                pregunta=pregunta,
                opcion=opcion_data['opcion'],
                valor_numerico=opcion_data['valor_numerico'],
                orden=opcion_data['orden'],
                activa=True
            )