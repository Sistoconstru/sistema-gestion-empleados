"""
Comando para configurar la evaluación anual de Afiladores
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import TipoEvaluacion, EvaluacionDesempeño, PreguntaEvaluacion, TipoPregunta, OpcionEvaluacion
from apps.authentication.models import Usuario


class Command(BaseCommand):
    help = 'Configura la evaluación anual para Afiladores (10 preguntas)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando evaluación de Afiladores...'))

        # Obtener usuario del sistema para creada_por
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(self.style.ERROR('Error: No se encontró un usuario administrador'))
            return

        # 1. Crear o actualizar el tipo de evaluación
        tipo_eval, created = TipoEvaluacion.objects.get_or_create(
            codigo='ANUAL_AFILADORES',
            defaults={
                'nombre': 'Evaluación Anual - Afiladores',
                'descripcion': 'Evaluación anual de desempeño para Afiladores',
                'dias_activacion': 365,
                'activo': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Tipo de evaluación creado: {tipo_eval.nombre}'))
        else:
            self.stdout.write(self.style.WARNING(f'○ Tipo de evaluación ya existía: {tipo_eval.nombre}'))

        # 2. Crear o actualizar la evaluación
        evaluacion, eval_created = EvaluacionDesempeño.objects.get_or_create(
            codigo='EVAL_AFILADORES_2025',
            defaults={
                'tipo_evaluacion': tipo_eval,
                'nombre': 'Evaluación Anual - Afiladores 2025',
                'descripcion': 'Evaluación de competencias para Afiladores con sistema ponderado',
                'activa': True,
                'creada_por': usuario_sistema
            }
        )

        if eval_created:
            self.stdout.write(self.style.SUCCESS(f'✓ Evaluación creada: {evaluacion.nombre}'))
        else:
            self.stdout.write(self.style.WARNING(f'○ Evaluación ya existía: {evaluacion.nombre}'))
            # Eliminar preguntas antiguas para recrearlas
            PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).delete()
            self.stdout.write(self.style.WARNING('  → Preguntas anteriores eliminadas'))

        # 3. Obtener tipo de pregunta ESCALA_5
        tipo_pregunta_escala5, _ = TipoPregunta.objects.get_or_create(
            codigo='ESCALA_5',
            defaults={
                'nombre': 'Escala Likert 1-5',
                'descripcion': 'Escala de 1 a 5 (Muy bajo a Muy alto)'
            }
        )

        # 4. Crear categorías con ponderación y preguntas
        categorias_data = [
            {
                'nombre': 'Competencias Organizacionales',
                'ponderacion': 10,
                'preguntas': [
                    ('COMUNICACIÓN', 'Capacidad para comunicar, de forma voluntaria, transmitir ideas, información y opiniones de forma clara y convincente, por escrito y oralmente, escuchando y siendo receptivo/a a las propuestas de los/as demás'),
                    ('TRABAJO EN EQUIPO', 'Capacidad para establecer relaciones de participación y cooperación con otras personas, compartiendo recursos y conocimiento, armonizando intereses y contribuyendo activamente al logro de los objetivos de la organización'),
                    ('MEJORA CONTINUA', 'Capacidad para llevar a cabo las actividades, funciones y responsabilidades inherentes al puesto de trabajo bajo estándares de calidad y buscando la mejora continua proponiendo la adaptación y modernización de los procesos y metodologías vigentes en la organización')
                ]
            },
            {
                'nombre': 'Objetivos',
                'ponderacion': 40,
                'preguntas': [
                    ('MANTENER HERRAMENTAL EN CONDICIONES ÓPTIMAS', 'Mantener el herramental de corte en condiciones óptimas de afilado y geometría, garantizando la calidad del acabado de la madera y la vida útil del equipo')
                ]
            },
            {
                'nombre': 'Competencias Interpersonales',
                'ponderacion': 25,
                'preguntas': [
                    ('DINAMISMO / ENERGÍA', 'Capacidad para trabajar activamente en situaciones cambiantes y retadoras, con interlocutores diversos, en jornadas extensas de trabajo, sin que por esto se vean afectados su nivel de actividad o su juicio profesional. Comportamiento esperado: Capacidad para mantener la concentración en tareas minuciosas durante toda la jornada'),
                    ('ANÁLISIS DE PROBLEMAS', 'Comportamiento esperado: Identifica la causa raíz de una falla mecánica recurrente y propone una solución definitiva'),
                    ('ATENCIÓN AL DETALLE', 'Comportamiento esperado: Logra niveles de precisión milimétricos en el afilado')
                ]
            },
            {
                'nombre': 'Competencias Técnicas',
                'ponderacion': 25,
                'preguntas': [
                    ('CALIDAD DEL TRABAJO', 'Su estándar de entrega es impecable, entendiendo que el afilado afecta directamente el consumo de energía y la calidad'),
                    ('EFECTIVIDAD DEL ARREGLO', 'Capacidad para realizar reparaciones técnicas que solucionan la causa raíz de las fallas, asegurando durabilidad en el tiempo, reduciendo reincidencias y contribuyendo a la estabilidad operativa de la planta'),
                    ('CUMPLIMIENTO DE CRONOGRAMA', 'Ejecución al 100% del plan de mantenimiento preventivo y/o actividades asignadas')
                ]
            }
        ]

        orden_global = 1
        total_preguntas = sum(len(cat['preguntas']) for cat in categorias_data)

        for cat_data in categorias_data:
            categoria_nombre = cat_data['nombre']
            num_preguntas = len(cat_data['preguntas'])
            peso_por_pregunta = round(cat_data['ponderacion'] / num_preguntas, 2)

            self.stdout.write(f'\n  Categoría: {categoria_nombre} ({cat_data["ponderacion"]}%)')
            self.stdout.write(f'    → {num_preguntas} preguntas, {peso_por_pregunta}% c/u')

            # Crear preguntas de la categoría
            for pregunta_texto, descripcion in cat_data['preguntas']:
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    categoria=categoria_nombre,
                    tipo_pregunta=tipo_pregunta_escala5,
                    pregunta=pregunta_texto,
                    descripcion=descripcion,
                    orden=orden_global,
                    peso_porcentual=peso_por_pregunta,
                    obligatoria=True
                )

                # Crear opciones 1-5 para la pregunta
                opciones = [
                    (1, 'Muy bajo'),
                    (2, 'Bajo'),
                    (3, 'Moderado'),
                    (4, 'Alto'),
                    (5, 'Muy alto')
                ]

                for valor, texto in opciones:
                    OpcionEvaluacion.objects.create(
                        pregunta=pregunta,
                        opcion=texto,
                        valor_numerico=valor,
                        orden=valor
                    )

                self.stdout.write(f'      ✓ Pregunta {orden_global}: {pregunta_texto[:60]}...')
                orden_global += 1

        # Resumen final
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('✓ CONFIGURACIÓN COMPLETADA'))
        self.stdout.write('='*80)
        self.stdout.write(f'Evaluación: {evaluacion.nombre}')
        self.stdout.write(f'Total de categorías: {len(categorias_data)}')
        self.stdout.write(f'Total de preguntas: {total_preguntas}')
        self.stdout.write('\nPonderaciones configuradas:')
        for cat in categorias_data:
            self.stdout.write(f'  • {cat["nombre"]}: {cat["ponderacion"]}%')
        self.stdout.write('\nEscala de calificación: 1-5 (Muy bajo a Muy alto)')
        self.stdout.write('Sistema de cálculo: Ponderado por categorías')
