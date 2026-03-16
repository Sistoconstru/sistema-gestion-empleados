# =============================================================================
# apps/evaluations/management/commands/configurar_evaluacion_auxiliar_procesos.py
# Configuración de evaluación anual de desempeño para Auxiliares de Procesos
# 11 preguntas | Escala 1-5 | Sistema de ponderación por categorías
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
    help = 'Configura la evaluación anual de desempeño para Auxiliares de Procesos (11 preguntas, escala 1-5, ponderada)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recrear',
            action='store_true',
            help='Elimina evaluación existente y la recrea',
        )

    def handle(self, *args, **options):
        recrear = options['recrear']

        self.stdout.write(
            self.style.SUCCESS('Configurando Evaluacion Anual - Auxiliares de Procesos')
        )

        # 1. Verificar tipos básicos
        self._verificar_tipos_basicos()

        # 2. Crear evaluación
        self._crear_evaluacion_auxiliar_procesos(recrear)

        self.stdout.write(
            self.style.SUCCESS('OK - Evaluacion Anual - Auxiliares de Procesos configurada exitosamente')
        )

    def _verificar_tipos_basicos(self):
        """Verificar que existan los tipos básicos necesarios"""
        # Verificar que existe TipoPregunta ESCALA_5
        tipo_pregunta, created = TipoPregunta.objects.get_or_create(
            codigo='ESCALA_5',
            defaults={
                'nombre': 'Escala 1-5',
                'descripcion': 'Pregunta con escala numérica del 1 al 5',
                'permite_opciones': True,
                'permite_texto_libre': False
            }
        )
        if created:
            self.stdout.write('  [OK] TipoPregunta ESCALA_5 creado')
        else:
            self.stdout.write('  [OK] TipoPregunta ESCALA_5 encontrado')

        # Verificar TipoEvaluacion
        tipo_evaluacion, created = TipoEvaluacion.objects.get_or_create(
            codigo='ANUAL_AUX_PROCESOS',
            defaults={
                'nombre': 'Evaluación Anual de Desempeño - Auxiliar de Procesos',
                'descripcion': 'Evaluación anual de desempeño para personal de producción/planta (auxiliares de procesos)',
                'dias_activacion': 365,  # Se asigna al cumplir un año
                'frecuencia_dias': 365,  # Anual
                'es_autoevaluacion': False,
                'activo': True
            }
        )
        if created:
            self.stdout.write('  [OK] TipoEvaluacion ANUAL_AUXILIAR_PROCESOS creado')
        else:
            self.stdout.write('  [OK] TipoEvaluacion ANUAL_AUXILIAR_PROCESOS encontrado')

    def _crear_evaluacion_auxiliar_procesos(self, recrear):
        """Crear la evaluación anual con las 11 preguntas ponderadas"""

        # Obtener usuario sistema
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(self.style.ERROR('[ERROR] No se encontro usuario administrador'))
            return

        # Obtener tipos necesarios
        tipo_evaluacion = TipoEvaluacion.objects.get(codigo='ANUAL_AUX_PROCESOS')
        tipo_pregunta = TipoPregunta.objects.get(codigo='ESCALA_5')

        # Crear o actualizar evaluación
        evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
            codigo='EVAL_ANUAL_AUX_PROCESOS_2025',
            defaults={
                'nombre': 'Evaluación Anual de Desempeño - Auxiliar de Procesos',
                'descripcion': 'Evaluación integral anual para auxiliares de procesos de producción/planta',
                'instrucciones': '''EVALUACIÓN ANUAL DE DESEMPEÑO - AUXILIAR DE PROCESOS

Le invitamos a diligenciar la presente Evaluación de Desempeño con responsabilidad, objetividad y coherencia.

SISTEMA DE CALIFICACIÓN:
La calificación se encuentra en escala de 1 a 5, siendo 1 el puntaje más bajo y 5 el más alto.
Los valores intermedios entre estos dos límites indicarán en grado de inclinación hacia una valoración baja o alta, según sea considerado.

CATEGORÍAS Y PONDERACIÓN:
• Competencias Organizacionales (10%): Comunicación, Trabajo en equipo, Mejora continua
• Objetivos (40%): Apoyo a procesos de producción (cargue, descargue, clasificación, arrumado, mantenimiento)
• Competencias Interpersonales (25%): Trabajo en equipo colaborativo, Dinamismo, Responsabilidad
• Competencias Técnicas (20%): Clasificación de madera, Orden y aseo, Apoyo al proceso

ESCALA DE PUNTUACIÓN:
• 1 = Muy bajo: Requiere mejora urgente
• 2 = Bajo: Necesita desarrollo
• 3 = Moderado: Cumple lo esperado
• 4 = Alto: Supera expectativas
• 5 = Muy alto: Excelencia

CRITERIOS DE RESULTADO FINAL:
• Muy bajo (1): 1%-40%
• Bajo (2): 41%-60%
• Moderado (3): 61%-75%
• Alto (4): 76%-90%
• Muy alto (5): 91%-100%

El resultado final se calculará aplicando la ponderación de cada categoría.
''',
                'tipo_evaluacion': tipo_evaluacion,
                'version': '2025.1',
                'activa': True,
                'creada_por': usuario_sistema
            }
        )

        if recrear and not created:
            # Eliminar preguntas existentes
            PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).delete()
            self.stdout.write('  [LIMPIEZA] Preguntas existentes eliminadas')

        if created or recrear:
            self.stdout.write(f'  [OK] Evaluacion: {evaluacion.nombre}')
            self._crear_preguntas_ponderadas(evaluacion, tipo_pregunta)
        else:
            self.stdout.write(f'  [INFO] Evaluacion existente: {evaluacion.nombre} (use --recrear para actualizar)')

    def _crear_preguntas_ponderadas(self, evaluacion, tipo_pregunta):
        """Crear las 10 preguntas con ponderación por categorías"""

        # 10 PREGUNTAS CORREGIDAS SEGÚN DOCUMENTO EXCEL
        # Ponderación: Org 10% (3 preg), Objetivos 40% (1 preg), Interp 25% (3 preg), Técnicas 20% (3 preg)

        preguntas = [
            # ==================== COMPETENCIAS ORGANIZACIONALES (10% total) ====================
            {
                'categoria': 'Competencias Organizacionales',
                'pregunta': 'Comunicación: Capacidad para comunicar, de forma voluntaria, transmitir ideas, información y opiniones de forma clara y convincente, por escrito y oralmente, escuchando y siendo receptivo/a a las propuestas de los/as demás',
                'descripcion': 'Evalúa habilidades de comunicación efectiva, expresión clara y escucha activa.',
                'peso_porcentual': 3.33,
                'orden': 1
            },
            {
                'categoria': 'Competencias Organizacionales',
                'pregunta': 'Trabajo en equipo: Capacidad para establecer relaciones de participación y cooperación con otras personas, compartiendo recursos y conocimiento, armonizando intereses y contribuyendo activamente al logro de los objetivos de la organización',
                'descripcion': 'Evalúa colaboración, cooperación y contribución a objetivos comunes.',
                'peso_porcentual': 3.33,
                'orden': 2
            },
            {
                'categoria': 'Competencias Organizacionales',
                'pregunta': 'Mejora continua: Capacidad para llevar a cabo las actividades, funciones y responsabilidades inherentes al puesto de trabajo bajo estándares de calidad y buscando la mejora continua proponiendo la adaptación y modernización de los procesos y metodologías vigentes en la organización',
                'descripcion': 'Evalúa búsqueda de mejoras, adaptación a cambios y modernización de procesos.',
                'peso_porcentual': 3.34,
                'orden': 3
            },

            # ==================== OBJETIVOS (40% total) ====================
            {
                'categoria': 'Objetivos',
                'pregunta': 'Apoya los procesos de producción mediante el cargue, descargue, clasificación y arrumado de madera, colaborando en el mantenimiento básico del área y asegurando que el flujo de materiales sea constante.',
                'descripcion': 'Evalúa desempeño en operaciones principales de producción: cargue, descargue, clasificación, arrumado y mantenimiento.',
                'peso_porcentual': 40.00,
                'orden': 4
            },

            # ==================== COMPETENCIAS INTERPERSONALES (25% total) ====================
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Trabajo en equipo: Capacidad para colaborar con otros para lograr objetivos comunes. Comportamiento esperado: Promueve el intercambio entre áreas y orienta el trabajo de pares a la consecución de la estrategia organizacional',
                'descripcion': 'Evalúa colaboración inter-áreas y orientación estratégica del equipo.',
                'peso_porcentual': 8.33,
                'orden': 5
            },
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Dinamismo: Capacidad de respuesta y agilidad en tareas físicas. Comportamiento esperado: Realiza el arrumado y clasificación con agilidad para no represar la salida de máquina',
                'descripcion': 'Evalúa velocidad, agilidad y eficiencia en ejecución de tareas físicas, arrumado y clasificación sin generar cuellos de botella.',
                'peso_porcentual': 8.34,
                'orden': 6
            },
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Responsabilidad: Capacidad para promover el logro de los objetivos corporativos y un adecuado ambiente laboral. Comportamiento esperado: Demuestra preocupación por realizar las tareas con precisión y calidad, con el propósito de contribuir, a través de su accionar, a la consecución.',
                'descripcion': 'Evalúa responsabilidad, calidad de trabajo y contribución a objetivos organizacionales.',
                'peso_porcentual': 8.33,
                'orden': 7
            },

            # ==================== COMPETENCIAS TÉCNICAS (20% total) ====================
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Clasificación: Selecciona correctamente la madera por diámetro, longitud y calidad',
                'descripcion': 'Evalúa precisión técnica en clasificación de madera según especificaciones.',
                'peso_porcentual': 6.67,
                'orden': 8
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Orden y Aseo: Mantenimiento del puesto de trabajo libre de materiales y herramientas en desuso',
                'descripcion': 'Evalúa organización, orden y limpieza del área de trabajo (5S).',
                'peso_porcentual': 6.67,
                'orden': 9
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Apoyo al proceso: Disponibilidad y eficiencia en el cargue, descargue y arrumado de paquetes para no represar la salida de máquina',
                'descripcion': 'Evalúa eficiencia operativa y sincronización con proceso productivo.',
                'peso_porcentual': 6.66,
                'orden': 10
            }
        ]

        self.stdout.write('  [INFO] Creando las 10 preguntas ponderadas...')

        for pregunta_data in preguntas:
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

            # Crear las 5 opciones de respuesta (escala 1-5)
            self._crear_opciones_respuesta_escala_5(pregunta)

            self.stdout.write(
                f'    [OK] {pregunta.orden}. [{pregunta.categoria}] {pregunta.peso_porcentual}%'
            )

        self.stdout.write(f'  [OK] {len(preguntas)} preguntas creadas exitosamente')
        self.stdout.write('')
        self.stdout.write('  RESUMEN DE PONDERACION:')
        self.stdout.write('    * Competencias Organizacionales: 10% (3 preguntas)')
        self.stdout.write('    * Objetivos: 40% (1 pregunta)')
        self.stdout.write('    * Competencias Interpersonales: 25% (3 preguntas)')
        self.stdout.write('    * Competencias Tecnicas: 20% (3 preguntas)')
        self.stdout.write('    TOTAL: 100%')

    def _crear_opciones_respuesta_escala_5(self, pregunta):
        """Crear las 5 opciones de respuesta (escala 1-5)"""
        opciones = [
            {
                'opcion': 'Muy bajo',
                'valor_numerico': 1.00,
                'orden': 1
            },
            {
                'opcion': 'Bajo',
                'valor_numerico': 2.00,
                'orden': 2
            },
            {
                'opcion': 'Moderado',
                'valor_numerico': 3.00,
                'orden': 3
            },
            {
                'opcion': 'Alto',
                'valor_numerico': 4.00,
                'orden': 4
            },
            {
                'opcion': 'Muy alto',
                'valor_numerico': 5.00,
                'orden': 5
            }
        ]

        for opcion_data in opciones:
            OpcionEvaluacion.objects.create(
                pregunta=pregunta,
                opcion=opcion_data['opcion'],
                valor_numerico=opcion_data['valor_numerico'],
                orden=opcion_data['orden'],
                activa=True
            )
