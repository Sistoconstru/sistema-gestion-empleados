# =============================================================================
# apps/evaluations/management/commands/configurar_evaluaciones_iniciales.py
# Configuración inicial del sistema de evaluaciones de desempeño
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
    help = 'Configura los tipos de pregunta y evaluaciones iniciales del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recrear',
            action='store_true',
            help='Elimina configuración existente y la recrea',
        )

    def handle(self, *args, **options):
        recrear = options['recrear']
        
        if recrear:
            self.stdout.write(
                self.style.WARNING('Eliminando configuración existente...')
            )
            TipoPregunta.objects.all().delete()
            TipoEvaluacion.objects.all().delete()
            EvaluacionDesempeño.objects.all().delete()

        # 1. Crear Tipos de Pregunta
        self._crear_tipos_pregunta()
        
        # 2. Crear Tipos de Evaluación  
        self._crear_tipos_evaluacion()
        
        # 3. Crear Evaluación de Periodo de Prueba
        self._crear_evaluacion_periodo_prueba()

        self.stdout.write(
            self.style.SUCCESS('✅ Configuración de evaluaciones completada exitosamente')
        )

    def _crear_tipos_pregunta(self):
        """Crear tipos de pregunta estándar"""
        self.stdout.write('📝 Creando tipos de pregunta...')
        
        tipos_pregunta = [
            {
                'codigo': 'ESCALA_5',
                'nombre': 'Escala Likert 1-5',
                'descripcion': 'Escala de calificación de 1 (Insatisfactorio) a 5 (Excelente)',
                'permite_opciones': True,
                'permite_texto_libre': False
            },
            {
                'codigo': 'TEXTO_LIBRE',
                'nombre': 'Comentarios Abiertos',
                'descripcion': 'Campo de texto libre para comentarios y observaciones',
                'permite_opciones': False,
                'permite_texto_libre': True
            },
            {
                'codigo': 'SI_NO',
                'nombre': 'Sí/No',
                'descripcion': 'Pregunta de respuesta binaria',
                'permite_opciones': True,
                'permite_texto_libre': False
            }
        ]
        
        for tipo_data in tipos_pregunta:
            tipo, created = TipoPregunta.objects.get_or_create(
                codigo=tipo_data['codigo'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'  ✓ Tipo de pregunta creado: {tipo.nombre}')
            else:
                self.stdout.write(f'  → Tipo de pregunta existente: {tipo.nombre}')

    def _crear_tipos_evaluacion(self):
        """Crear tipos de evaluación"""
        self.stdout.write('📋 Creando tipos de evaluación...')
        
        tipos_evaluacion = [
            {
                'codigo': 'PERIODO_PRUEBA',
                'nombre': 'Evaluación Periodo de Prueba',
                'descripcion': 'Evaluación realizada a los 30 días de ingreso para determinar continuidad',
                'dias_activacion': 25,  # 5 días antes de cumplir 30
                'frecuencia_dias': None,  # Solo una vez
                'es_autoevaluacion': False,  # La hace el supervisor
                'activo': True
            },
            {
                'codigo': 'EVALUACION_ANUAL',
                'nombre': 'Evaluación Anual de Desempeño',
                'descripcion': 'Evaluación integral de desempeño realizada anualmente',
                'dias_activacion': 360,  # 5 días antes del año
                'frecuencia_dias': 365,  # Cada año
                'es_autoevaluacion': False,
                'activo': True
            },
            {
                'codigo': 'AUTOEVALUACION',
                'nombre': 'Autoevaluación de Desempeño',
                'descripcion': 'Evaluación que realiza el empleado sobre su propio desempeño',
                'dias_activacion': 180,  # Cada 6 meses
                'frecuencia_dias': 180,
                'es_autoevaluacion': True,
                'activo': False  # Inicialmente desactivada
            }
        ]
        
        for tipo_data in tipos_evaluacion:
            tipo, created = TipoEvaluacion.objects.get_or_create(
                codigo=tipo_data['codigo'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'  ✓ Tipo de evaluación creado: {tipo.nombre}')
            else:
                self.stdout.write(f'  → Tipo de evaluación existente: {tipo.nombre}')

    def _crear_evaluacion_periodo_prueba(self):
        """Crear la evaluación específica para periodo de prueba con 7 preguntas exactas del Excel"""
        self.stdout.write('🎯 Creando evaluación periodo de prueba...')
        
        # Obtener o crear usuario del sistema
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(
                self.style.ERROR('Error: No se encontró usuario administrador')
            )
            return
            
        tipo_periodo_prueba = TipoEvaluacion.objects.get(codigo='PERIODO_PRUEBA')
        tipo_pregunta_escala = TipoPregunta.objects.get(codigo='ESCALA_5')
        
        # Crear evaluación
        evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
            codigo='EVAL_PERIODO_PRUEBA_2024',
            defaults={
                'nombre': 'Evaluación de Período de Prueba',
                'descripcion': 'Evaluación integral para empleados en período de prueba - 30 días',
                'instrucciones': '''
                Esta evaluación debe realizarse 5 días hábiles antes de la terminación del período de prueba.
                
                CRITERIOS DE EVALUACIÓN:
                • De 1 a 13 puntos: El empleado NO continúa en el cargo
                • De 14 a 21 puntos: El empleado continúa en el cargo
                
                ESCALA DE PUNTUACIÓN:
                • 1 = No cumple: No tiene comportamientos relacionados con este aspecto
                • 2 = Cumple parcialmente: De manera periódica tiene comportamientos relacionados con este aspecto  
                • 3 = Cumple totalmente: Se evidencia siempre este comportamiento
                ''',
                'tipo_evaluacion': tipo_periodo_prueba,
                'version': '2024.1',
                'activa': True,
                'creada_por': usuario_sistema
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ Evaluación creada: {evaluacion.nombre}')
        else:
            self.stdout.write(f'  → Evaluación existente: {evaluacion.nombre}')
            # Limpiar preguntas existentes para recrearlas
            PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).delete()
        
        # 7 PREGUNTAS EXACTAS DEL EXCEL
        preguntas_periodo_prueba = [
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Trabajo en equipo',
                'descripcion': 'Desarrolla labores con sus compañeros, es conciliador y respetuoso de las diferencias.',
                'peso_porcentual': 14.29,  # 1/7 = 14.29%
                'orden': 1
            },
            {
                'categoria': 'Actitud Laboral',
                'pregunta': 'Compromiso',
                'descripcion': 'Se muestra colaborador y abierto a ayudar a conseguir objetivos generales del proceso, aunque deba invertir más tiempo y esfuerzo en ello, asume de manera autónoma actividades que pueda hacer para lograr una meta.',
                'peso_porcentual': 14.29,
                'orden': 2
            },
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Comunicación',
                'descripcion': 'Tiene la capacidad de expresarse coherentemente, darse a entender y llegar a un acuerdo, sabe escuchar.',
                'peso_porcentual': 14.29,
                'orden': 3
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Atención al detalle',
                'descripcion': 'Tiene una actitud de observación constante para mejorar su proceso o tarea sin pasar por alto detalles que podrían mejorar una actividad, se muestra interesado en atender pequeños detalles.',
                'peso_porcentual': 14.29,
                'orden': 4
            },
            {
                'categoria': 'Competencias Organizacionales',
                'pregunta': 'Cumplimiento de las normas y procedimientos',
                'descripcion': 'Su actuar se encamina a cumplir de manera diligente, rápida y eficiente las obligaciones, normas y procedimientos establecidos por la empresa, no tiene amonestaciones por incumplimientos relacionados con este tema.',
                'peso_porcentual': 14.29,
                'orden': 5
            },
            {
                'categoria': 'Actitud Laboral',
                'pregunta': 'Actitud respecto al trabajo',
                'descripcion': 'Tiene una actitud positiva respecto a su trabajo, a la empresa y para el desarrollo del trabajo.',
                'peso_porcentual': 14.29,
                'orden': 6
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Calidad',
                'descripcion': 'Los trabajos que desarrolla están acordes a lo exigido, sin errores repetitivos y con una evidente muestra de cuidado y esmero.',
                'peso_porcentual': 14.29,
                'orden': 7
            }
        ]
        
        # Crear preguntas
        for pregunta_data in preguntas_periodo_prueba:
            pregunta = PreguntaEvaluacion.objects.create(
                evaluacion=evaluacion,
                tipo_pregunta=tipo_pregunta_escala,
                categoria=pregunta_data['categoria'],
                pregunta=pregunta_data['pregunta'],
                descripcion=pregunta_data['descripcion'],
                peso_porcentual=pregunta_data['peso_porcentual'],
                orden=pregunta_data['orden'],
                obligatoria=True,
                activa=True
            )
            
            # Crear las 3 opciones de respuesta exactas del Excel
            opciones_respuesta = [
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
            
            for opcion_data in opciones_respuesta:
                OpcionEvaluacion.objects.create(
                    pregunta=pregunta,
                    opcion=opcion_data['opcion'],
                    valor_numerico=opcion_data['valor_numerico'],
                    orden=opcion_data['orden'],
                    activa=True
                )
            
            self.stdout.write(f'  ✓ Pregunta creada: {pregunta.pregunta}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Evaluación de período de prueba configurada con {len(preguntas_periodo_prueba)} preguntas')
        )