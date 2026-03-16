"""
Comando para configurar la evaluación anual de Coordinadores de Procesos
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import TipoEvaluacion, EvaluacionDesempeño, PreguntaEvaluacion, TipoPregunta, OpcionEvaluacion
from apps.authentication.models import Usuario


class Command(BaseCommand):
    help = 'Configura la evaluación anual para Coordinadores de Procesos (11 preguntas)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando evaluación de Coordinadores de Procesos...'))

        # Obtener usuario del sistema para creada_por
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(self.style.ERROR('Error: No se encontró un usuario administrador'))
            return

        # 1. Crear o actualizar el tipo de evaluación
        tipo_eval, created = TipoEvaluacion.objects.get_or_create(
            codigo='ANUAL_COORD_PROC',
            defaults={
                'nombre': 'Evaluación Anual - Coordinadores de Procesos',
                'descripcion': 'Evaluación anual de desempeño para Coordinadores de Procesos',
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
            codigo='EVAL_COORD_PROC_2025',
            defaults={
                'tipo_evaluacion': tipo_eval,
                'nombre': 'Evaluación Anual - Coordinadores de Procesos 2025',
                'descripcion': 'Evaluación de competencias para Coordinadores de Procesos con sistema ponderado',
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
                    ('COMUNICACIÓN', 'Se comunica de forma efectiva con su equipo, superiores y otras áreas. Transmite información clara y oportuna.'),
                    ('TRABAJO EN EQUIPO', 'Colabora activamente con su equipo y otras áreas para lograr objetivos comunes.'),
                    ('MEJORA CONTINUA', 'Identifica oportunidades de mejora e implementa soluciones en sus procesos.')
                ]
            },
            {
                'nombre': 'Objetivos',
                'ponderacion': 40,
                'preguntas': [
                    ('PLANIFICACIÓN Y CONTROL DE PRODUCCIÓN', 'Cumple con los objetivos de producción establecidos. Planifica eficientemente y controla los procesos bajo su responsabilidad.')
                ]
            },
            {
                'nombre': 'Competencias Interpersonales',
                'ponderacion': 25,
                'preguntas': [
                    ('LIDERAZGO', 'Guía, motiva y desarrolla a su equipo de trabajo hacia el logro de objetivos.'),
                    ('TOMA DE DECISIONES', 'Toma decisiones oportunas y efectivas basadas en análisis y criterio.'),
                    ('TOLERANCIA A LA PRESIÓN', 'Mantiene efectividad y control bajo presión y situaciones de estrés.'),
                    ('INTEGRIDAD', 'Actúa con honestidad, ética y coherencia. Cumple compromisos y es ejemplo para su equipo.')
                ]
            },
            {
                'nombre': 'Competencias Técnicas',
                'ponderacion': 25,
                'preguntas': [
                    ('GESTIÓN DE PRODUCCIÓN Y RENDIMIENTOS', 'Domina los procesos productivos, optimiza rendimientos y gestiona recursos eficientemente.'),
                    ('CONTROL DE CALIDAD Y NORMATIVIDAD', 'Asegura el cumplimiento de estándares de calidad y normativas aplicables. Gestiona no conformidades.'),
                    ('SUPERVISIÓN DE MANTENIMIENTO', 'Coordina y supervisa el mantenimiento preventivo y correctivo. Minimiza tiempos de paro.')
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
