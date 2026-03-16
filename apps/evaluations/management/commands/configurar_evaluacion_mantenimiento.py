# =============================================================================
# apps/evaluations/management/commands/configurar_evaluacion_mantenimiento.py
# Configuración de evaluación anual de desempeño para Personal de Mantenimiento
# 10 preguntas | Escala 1-5 | Sistema de ponderación por categorías
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
    help = 'Configura la evaluación anual de desempeño para Personal de Mantenimiento (10 preguntas, escala 1-5, ponderada)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recrear',
            action='store_true',
            help='Elimina evaluación existente y la recrea',
        )

    def handle(self, *args, **options):
        recrear = options['recrear']

        self.stdout.write(
            self.style.SUCCESS('Configurando Evaluacion Anual - Mantenimiento')
        )

        # 1. Verificar tipos básicos
        self._verificar_tipos_basicos()

        # 2. Crear evaluación
        self._crear_evaluacion_mantenimiento(recrear)

        self.stdout.write(
            self.style.SUCCESS('OK - Evaluacion Anual - Mantenimiento configurada exitosamente')
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
            codigo='ANUAL_MANTENIMIENTO',
            defaults={
                'nombre': 'Evaluación Anual de Desempeño - Mantenimiento',
                'descripcion': 'Evaluación anual de desempeño para personal de mantenimiento',
                'dias_activacion': 365,  # Se asigna al cumplir un año
                'frecuencia_dias': 365,  # Anual
                'es_autoevaluacion': False,
                'activo': True
            }
        )
        if created:
            self.stdout.write('  [OK] TipoEvaluacion ANUAL_MANTENIMIENTO creado')
        else:
            self.stdout.write('  [OK] TipoEvaluacion ANUAL_MANTENIMIENTO encontrado')

    def _crear_evaluacion_mantenimiento(self, recrear):
        """Crear la evaluación anual con las 10 preguntas ponderadas"""

        # Obtener usuario sistema
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(self.style.ERROR('[ERROR] No se encontro usuario administrador'))
            return

        # Obtener tipos necesarios
        tipo_evaluacion = TipoEvaluacion.objects.get(codigo='ANUAL_MANTENIMIENTO')
        tipo_pregunta = TipoPregunta.objects.get(codigo='ESCALA_5')

        # Crear o actualizar evaluación
        evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
            codigo='EVAL_ANUAL_MANT_2025',
            defaults={
                'nombre': 'Evaluación Anual de Desempeño - Mantenimiento',
                'descripcion': 'Evaluación integral anual para personal de mantenimiento',
                'instrucciones': '''EVALUACIÓN ANUAL DE DESEMPEÑO - MANTENIMIENTO

Le invitamos a diligenciar la presente Evaluación de Desempeño con responsabilidad, objetividad y coherencia.

La calificación se encuentra en escala de 1 a 5 siendo 1 el puntaje más bajo y 5 el más alto, y los valores intermedios entre estos dos límites indicarán el grado de inclinación hacia una valoración baja o alta, según sea considerado.

SISTEMA DE PONDERACIÓN:
• Competencias Organizacionales: 10%
• Objetivos: 40%
• Competencias Interpersonales: 25%
• Competencias Técnicas: 25%

El puntaje final se calcula mediante promedio ponderado de las categorías.

NOTA: El uso estricto de EPP y verificación de paros de emergencia es obligatorio en todas las actividades de mantenimiento.''',
                'tipo_evaluacion': tipo_evaluacion,
                'creada_por': usuario_sistema,
                'activa': True,
            }
        )

        if not created and not recrear:
            self.stdout.write('  [OK] Evaluacion: ' + evaluacion.nombre)
            return

        if recrear:
            # Eliminar preguntas existentes
            PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).delete()
            self.stdout.write('  [LIMPIEZA] Preguntas existentes eliminadas')

        self.stdout.write('  [OK] Evaluacion: ' + evaluacion.nombre)

        # ==================== 10 PREGUNTAS PONDERADAS ====================
        preguntas_data = [
            # ===== COMPETENCIAS ORGANIZACIONALES (10%) - 3 preguntas =====
            {
                'categoria': 'Competencias Organizacionales',
                'pregunta': 'Comunicación: Capacidad para comunicar de forma voluntaria, transmitir ideas, información y opiniones de forma clara y convincente, por escrito y oralmente, escuchando y siendo receptivo/a a las propuestas de los/as demás',
                'descripcion': 'Evalúa la capacidad de transmitir información técnica de forma clara, escuchar activamente y comunicarse efectivamente con el equipo.',
                'peso_porcentual': 3.33,
                'orden': 1
            },
            {
                'categoria': 'Competencias Organizacionales',
                'pregunta': 'Trabajo en Equipo: Capacidad para establecer relaciones de participación y cooperación con otras personas, compartiendo recursos y conocimiento, armonizando intereses y contribuyendo activamente al logro de los objetivos de la organización',
                'descripcion': 'Evalúa colaboración con compañeros, disposición para ayudar y contribuir al logro de objetivos comunes.',
                'peso_porcentual': 3.33,
                'orden': 2
            },
            {
                'categoria': 'Competencias Organizacionales',
                'pregunta': 'Mejora Continua: Capacidad para llevar a cabo las actividades, funciones y responsabilidades inherentes al puesto de trabajo bajo estándares de calidad y buscando la mejora continua proponiendo la adaptación y modernización de los procesos y metodologías vigentes en la organización',
                'descripcion': 'Evalúa iniciativa para proponer mejoras en procesos de mantenimiento, adaptarse a nuevas tecnologías y optimizar procedimientos.',
                'peso_porcentual': 3.34,
                'orden': 3
            },

            # ===== OBJETIVOS (40%) - 1 pregunta =====
            {
                'categoria': 'Objetivos',
                'pregunta': 'Mantenimiento de Maquinaria: Asegurar la disponibilidad y el correcto funcionamiento de toda la maquinaria de la planta (aserradoras, cilindradoras, calderas, etc.) mediante el mantenimiento preventivo y correctivo, minimizando los tiempos de parada',
                'descripcion': 'Evalúa el cumplimiento del objetivo principal del cargo: mantener la maquinaria operativa mediante mantenimiento preventivo y correctivo eficaz.',
                'peso_porcentual': 40.0,
                'orden': 4
            },

            # ===== COMPETENCIAS INTERPERSONALES (25%) - 3 preguntas =====
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Iniciativa / Proactividad: Capacidad para actuar proactivamente, idear e implementar soluciones a nuevas problemáticas y/o retos, con decisión e independencia de criterio. Comportamiento esperado: Se anticipa a la falla; no espera a que la máquina se rompa si detecta un sonido o vibración inusual',
                'descripcion': 'Evalúa la capacidad de anticiparse a problemas, detectar fallas potenciales y actuar preventivamente.',
                'peso_porcentual': 8.33,
                'orden': 5
            },
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Análisis de Problemas: Identifica la causa raíz de una falla mecánica recurrente y propone una solución definitiva',
                'descripcion': 'Evalúa capacidad analítica para diagnosticar fallas, identificar causas raíz y proponer soluciones efectivas y duraderas.',
                'peso_porcentual': 8.34,
                'orden': 6
            },
            {
                'categoria': 'Competencias Interpersonales',
                'pregunta': 'Responsabilidad: Capacidad para promover el logro de los objetivos corporativos y un adecuado ambiente laboral. Comportamiento esperado: Analiza y elabora soluciones que permiten mejorar los tiempos y la calidad en la ejecución de las tareas y procesos, y facilita así el logro de los objetivos organizacionales',
                'descripcion': 'Evalúa compromiso con objetivos organizacionales, calidad en el trabajo y contribución al ambiente laboral positivo.',
                'peso_porcentual': 8.33,
                'orden': 7
            },

            # ===== COMPETENCIAS TÉCNICAS (25%) - 3 preguntas =====
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Disponibilidad de Máquina: Reducción de tiempos de parada por fallas mecánicas/eléctricas',
                'descripcion': 'Evalúa la efectividad en mantener las máquinas operativas, reduciendo al mínimo los tiempos de parada no programados.',
                'peso_porcentual': 8.33,
                'orden': 8
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Efectividad del Arreglo: Capacidad del mecánico para realizar reparaciones técnicas que solucionen la causa raíz de las fallas, asegurando durabilidad en el tiempo, reduciendo reincidencias y contribuyendo a la estabilidad operativa de la planta',
                'descripcion': 'Evalúa calidad y durabilidad de las reparaciones, capacidad para solucionar definitivamente las fallas.',
                'peso_porcentual': 8.33,
                'orden': 9
            },
            {
                'categoria': 'Competencias Técnicas',
                'pregunta': 'Cumplimiento de Cronograma: Ejecución al 100% del plan de mantenimiento preventivo y/o actividades asignadas',
                'descripcion': 'Evalúa cumplimiento puntual del cronograma de mantenimiento preventivo y tareas programadas.',
                'peso_porcentual': 8.34,
                'orden': 10
            },
        ]

        self.stdout.write('  [INFO] Creando las 10 preguntas ponderadas...')

        for pregunta_info in preguntas_data:
            # Crear pregunta
            pregunta = PreguntaEvaluacion.objects.create(
                evaluacion=evaluacion,
                tipo_pregunta=tipo_pregunta,
                categoria=pregunta_info['categoria'],
                pregunta=pregunta_info['pregunta'],
                descripcion=pregunta_info['descripcion'],
                orden=pregunta_info['orden'],
                obligatoria=True,
                peso_porcentual=pregunta_info['peso_porcentual']
            )

            # Crear opciones de escala 1-5
            opciones = [
                {'opcion': 'Muy bajo', 'valor': 1},
                {'opcion': 'Bajo', 'valor': 2},
                {'opcion': 'Moderado', 'valor': 3},
                {'opcion': 'Alto', 'valor': 4},
                {'opcion': 'Muy alto', 'valor': 5},
            ]

            for opcion_data in opciones:
                OpcionEvaluacion.objects.create(
                    pregunta=pregunta,
                    opcion=opcion_data['opcion'],
                    valor_numerico=opcion_data['valor'],
                    orden=opcion_data['valor']
                )

            self.stdout.write(
                f'    [OK] {pregunta.orden}. [{pregunta.categoria}] {pregunta.peso_porcentual}%'
            )

        self.stdout.write(f'  [OK] {len(preguntas_data)} preguntas creadas exitosamente')

        # Mostrar resumen de ponderación
        self.stdout.write('\n  RESUMEN DE PONDERACION:')
        self.stdout.write('    * Competencias Organizacionales: 10% (3 preguntas)')
        self.stdout.write('    * Objetivos: 40% (1 pregunta)')
        self.stdout.write('    * Competencias Interpersonales: 25% (3 preguntas)')
        self.stdout.write('    * Competencias Tecnicas: 25% (3 preguntas)')
        self.stdout.write('    TOTAL: 100%')
