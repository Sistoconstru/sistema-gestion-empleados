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
        
        # 7 PREGUNTAS CON RESPUESTAS DINÁMICAS DEL DOCUMENTO
        preguntas_periodo_prueba = [
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Trabajo en equipo',
                'descripcion': 'Desarrolla labores con sus compañeros, es conciliador y respetuoso de las diferencias.',
                'peso_porcentual': 14.29,
                'orden': 1,
                'respuestas': {
                    1: {
                        'observacion': 'Se presentan dificultades para integrarse plenamente con el equipo. En algunas ocasiones surgen desacuerdos debido a la falta de escucha activa o a una disposición limitada para colaborar.',
                        'recomendacion': 'Fortalecer la comunicación y la participación dentro del equipo, solicitando apoyo cuando sea necesario y brindándolo igualmente. Involucrarse de manera más activa en actividades grupales contribuirá a un mejor clima laboral.',
                        'ejemplo': 'Iniciar ofreciendo apoyo en tareas sencillas para generar confianza y mejorar la relación con los compañeros'
                    },
                    2: {
                        'observacion': 'Participa en el trabajo en equipo, aunque a veces resulta difícil mantener una actitud conciliadora o abierta frente a diferentes puntos de vista.',
                        'recomendacion': 'Trabajar en una actitud más constante y equilibrada, especialmente en situaciones de presión, fomentando el diálogo y el respeto mutuo.',
                        'ejemplo': 'Antes de responder en una discusión laboral, tomar un momento para escuchar plenamente la opinión del compañero y reflexionar antes de intervenir.'
                    },
                    3: {
                        'observacion': 'Se integra adecuadamente al equipo, respeta las diferencias y contribuye a un ambiente armonioso.',
                        'recomendacion': 'Mantener esta actitud colaborativa y continuar siendo un referente positivo y un apoyo para los compañeros.',
                        'ejemplo': ''
                    }
                }
            },
            {
                'categoria': 'Actitud Laboral',
                'pregunta': 'Compromiso',
                'descripcion': 'Colabora y ayuda a lograr los objetivos del proceso, incluso si requiere mayor esfuerzo, y asume actividades autónomamente.',
                'peso_porcentual': 14.29,
                'orden': 2,
                'respuestas': {
                    1: {
                        'observacion': 'Actualmente no se evidencia disposición para asumir tareas adicionales ni un compromiso claro con los objetivos del área.',
                        'recomendacion': 'Desarrollar mayor iniciativa y asumir responsabilidades acordes al cargo. Es importante actuar de manera proactiva, sin esperar instrucciones para realizar tareas necesarias.',
                        'ejemplo': 'Puede empezar completando tareas sin necesidad de recordatorios constantes.'
                    },
                    2: {
                        'observacion': 'Muestra compromiso en algunas ocasiones, pero este no es constante y requiere acompañamiento para asumir determinadas actividades.',
                        'recomendacion': 'Fortalecer la constancia y demostrar mayor autonomía en las labores diarias. Atender con diligencia aquellas tareas no contempladas explícitamente en las funciones, pero que surgen de manera cotidiana y son importantes para garantizar la calidad del trabajo.',
                        'ejemplo': 'Identificar tareas pendientes y gestionarlas de manera autónoma, sin esperar instrucciones directas.'
                    },
                    3: {
                        'observacion': 'Demuestra compromiso constante, disposición al esfuerzo adicional y autonomía para asumir actividades que aportan al logro de objetivos.',
                        'recomendacion': 'Continuar manteniendo esta actitud proactiva, siendo referente de compromiso para el equipo.',
                        'ejemplo': ''
                    }
                }
            },
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Comunicación',
                'descripcion': 'Se expresa coherentemente, logra darse a entender, llegar a acuerdos y sabe escuchar.',
                'peso_porcentual': 14.29,
                'orden': 3,
                'respuestas': {
                    1: {
                        'observacion': 'La información que proporciona no siempre es clara o precisa, y en algunas ocasiones interrumpe o no escucha activamente a los demás.',
                        'recomendacion': 'Fortalecer la capacidad de escuchar y comunicar de manera clara y oportuna, asegurando que la información requerida llegue correctamente a los demás para alcanzar los objetivos del equipo.',
                        'ejemplo': 'Antes de actuar, repetir brevemente lo entendido para confirmar la información y evitar errores.'
                    },
                    2: {
                        'observacion': 'Se comunica adecuadamente en la mayoría de las situaciones, aunque en ocasiones surgen malentendidos por falta de claridad o retroalimentación.',
                        'recomendacion': 'Promover un intercambio de información constante y efectivo, asegurando que todos los miembros del equipo estén correctamente informados.',
                        'ejemplo': 'Organizar las ideas antes de explicar un proceso o procedimiento.'
                    },
                    3: {
                        'observacion': 'Se comunica de forma clara, escucha activamente y facilita la resolución de acuerdos.',
                        'recomendacion': 'Mantener y fortalecer esta habilidad, continuando como un referente de comunicación efectiva.',
                        'ejemplo': ''
                    }
                }
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Atención al detalle',
                'descripcion': 'Observa permanentemente su proceso para mejorar y atiende pequeños detalles que pueden optimizar resultados.',
                'peso_porcentual': 14.29,
                'orden': 4,
                'respuestas': {
                    1: {
                        'observacion': 'Se han identificado oportunidades de mejora en la revisión de tareas, ya que en ocasiones algunos detalles pasan inadvertidos y pueden influir en la calidad final del trabajo.',
                        'recomendacion': 'Se sugiere revisar cuidadosamente el trabajo antes de su entrega y apoyarse en herramientas como listas de verificación o recordatorios para asegurar que no se omitan aspectos relevantes.',
                        'ejemplo': 'Tomar 2 minutos para revisar documentos antes de enviarlos o contar con una lista de verificación.'
                    },
                    2: {
                        'observacion': 'Suele mostrar una buena atención en sus tareas; sin embargo, en algunas ocasiones ciertos detalles pueden pasar desapercibidos.',
                        'recomendacion': 'Se sugiere fortalecer la concentración, especialmente en tareas críticas, para asegurar que todos los elementos relevantes sean considerados.',
                        'ejemplo': 'Subrayar o marcar los puntos importantes de cada actividad antes de ejecutarla.'
                    },
                    3: {
                        'observacion': 'Tiene una actitud constante de observación y cuidado del detalle.',
                        'recomendacion': 'Se recomienda mantener este buen nivel de precisión en sus tareas.',
                        'ejemplo': ''
                    }
                }
            },
            {
                'categoria': 'Competencias Organizacionales',
                'pregunta': 'Cumplimiento de normas y procedimientos',
                'descripcion': 'Cumple de manera rápida y eficiente las normas, sin incurrir en incumplimientos.',
                'peso_porcentual': 14.29,
                'orden': 5,
                'respuestas': {
                    1: {
                        'observacion': 'Actualmente tiene dificultades para seguir los procedimientos establecidos y requiere recordatorios frecuentes para completar las tareas de acuerdo con los protocolos.',
                        'recomendacion': 'Se sugiere revisar nuevamente los protocolos del área y practicarlos de forma constante para lograr una aplicación más segura y uniforme.',
                        'ejemplo': 'Revisar el manual del área antes de realizar procedimientos clave.'
                    },
                    2: {
                        'observacion': 'En general sigue las normas y procedimientos; sin embargo, se han presentado algunas inconsistencias puntuales. Mejorar la consistencia en la ejecución contribuirá a resultados más confiables.',
                        'recomendacion': 'Se recomienda reforzar la disciplina en el cumplimiento de procesos para mantener un desempeño estable y sin omisiones.',
                        'ejemplo': 'Crear un paso a paso personal para evitar saltarse etapas.'
                    },
                    3: {
                        'observacion': 'Cumple de forma eficiente todas las normas y procedimientos establecidos.',
                        'recomendacion': 'Continuar siendo referente de cumplimiento y orden.',
                        'ejemplo': ''
                    }
                }
            },
            {
                'categoria': 'Actitud Laboral',
                'pregunta': 'Actitud respecto al trabajo',
                'descripcion': 'Tiene una actitud positiva hacia sus funciones, la empresa y el desarrollo del trabajo.',
                'peso_porcentual': 14.29,
                'orden': 6,
                'respuestas': {
                    1: {
                        'observacion': 'En algunas tareas se ha notado poca disposición o actitudes que pueden afectar el desarrollo del trabajo.',
                        'recomendacion': 'Fomentar una actitud más abierta y receptiva que permita aprovechar mejor las oportunidades de aprendizaje y colaboración.',
                        'ejemplo': 'Antes de rechazar una tarea, consultar sobre su propósito o impacto para comprender mejor su importancia.'
                    },
                    2: {
                        'observacion': 'Generalmente muestra buena actitud, pero en situaciones de presión se ve afectada su disposición.',
                        'recomendacion': 'Fortalecer su manejo emocional en situaciones de alta demanda para mantener la estabilidad y el enfoque.',
                        'ejemplo': 'Aplicar técnicas breves de respiración o pausas conscientes cuando surja el estrés.'
                    },
                    3: {
                        'observacion': 'Mantiene una actitud positiva, colaborativa y dispuesta.',
                        'recomendacion': 'Seguir impulsando esta actitud, ya que genera un ambiente laboral favorable y motiva al equipo.',
                        'ejemplo': ''
                    }
                }
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Calidad',
                'descripcion': 'Entrega trabajos acordes a lo exigido, sin errores repetitivos y con cuidado y esmero.',
                'peso_porcentual': 14.29,
                'orden': 7,
                'respuestas': {
                    1: {
                        'observacion': 'Se han identificado errores recurrentes en las tareas o falta de una revisión final antes de entregarlas.',
                        'recomendacion': 'Fortalecer el control de calidad para asegurar resultados más precisos y completos.',
                        'ejemplo': 'Antes de finalizar, revisar tres aspectos clave: formato, exactitud de la información y coherencia del contenido.'
                    },
                    2: {
                        'observacion': 'La calidad del trabajo suele ser buena, aunque ocasionalmente se presentan fallas por descuidos puntuales.',
                        'recomendacion': 'Incrementar la atención en actividades repetitivas o que requieren mayor detalle para evitar errores menores.',
                        'ejemplo': 'Solicitar retroalimentación sobre las entregas para identificar oportunidades de mejora continua.'
                    },
                    3: {
                        'observacion': 'Entregas de excelente calidad, sin errores y con evidente cuidado.',
                        'recomendacion': 'Mantener este nivel de dedicación y precisión en todas las tareas asignadas, ya que aporta significativamente a la calidad del trabajo del equipo.',
                        'ejemplo': ''
                    }
                }
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

            # Crear las 3 opciones de respuesta con contenido del documento
            respuestas_por_nivel = pregunta_data['respuestas']

            opciones_respuesta = [
                {
                    'valor': 1,
                    'etiqueta': 'No cumple',
                    'observacion': respuestas_por_nivel[1]['observacion'],
                    'recomendacion': respuestas_por_nivel[1]['recomendacion'],
                    'ejemplo': respuestas_por_nivel[1]['ejemplo']
                },
                {
                    'valor': 2,
                    'etiqueta': 'Cumple parcialmente',
                    'observacion': respuestas_por_nivel[2]['observacion'],
                    'recomendacion': respuestas_por_nivel[2]['recomendacion'],
                    'ejemplo': respuestas_por_nivel[2]['ejemplo']
                },
                {
                    'valor': 3,
                    'etiqueta': 'Cumple totalmente',
                    'observacion': respuestas_por_nivel[3]['observacion'],
                    'recomendacion': respuestas_por_nivel[3]['recomendacion'],
                    'ejemplo': respuestas_por_nivel[3]['ejemplo']
                }
            ]

            for idx, opcion_data in enumerate(opciones_respuesta, 1):
                # Crear opción con contenido dinámico
                opcion_texto = f"{opcion_data['etiqueta']}\n\nObservación: {opcion_data['observacion']}\n\nRecomendación: {opcion_data['recomendacion']}"
                if opcion_data['ejemplo']:
                    opcion_texto += f"\n\nEjemplo: {opcion_data['ejemplo']}"

                OpcionEvaluacion.objects.create(
                    pregunta=pregunta,
                    opcion=opcion_texto,
                    valor_numerico=float(opcion_data['valor']),
                    orden=idx,
                    activa=True
                )

            self.stdout.write(f'  ✓ Pregunta creada: {pregunta.pregunta} (con 3 respuestas dinámicas)')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Evaluación de período de prueba configurada con {len(preguntas_periodo_prueba)} preguntas')
        )