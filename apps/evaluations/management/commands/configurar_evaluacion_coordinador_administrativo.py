"""
Comando para configurar la evaluación anual de Coordinador Administrativo
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import TipoEvaluacion, EvaluacionDesempeño, PreguntaEvaluacion, TipoPregunta, OpcionEvaluacion
from apps.authentication.models import Usuario


class Command(BaseCommand):
    help = 'Configura la evaluación anual para Coordinador Administrativo (12 preguntas + SST)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando evaluación de Coordinador Administrativo...'))

        # Obtener usuario del sistema para creada_por
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(self.style.ERROR('Error: No se encontró un usuario administrador'))
            return

        # 1. Crear o actualizar el tipo de evaluación
        tipo_eval, created = TipoEvaluacion.objects.get_or_create(
            codigo='ANUAL_COORD_ADMIN',
            defaults={
                'nombre': 'Evaluación Anual - Coordinador Administrativo',
                'descripcion': 'Evaluación anual de desempeño para Coordinadores del Área Administrativa con sistema ponderado',
                'dias_activacion': 365,
                'frecuencia_dias': 365,
                'es_autoevaluacion': False,
                'activo': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Tipo de evaluación creado: {tipo_eval.nombre}'))
        else:
            self.stdout.write(self.style.WARNING(f'[-] Tipo de evaluación ya existía: {tipo_eval.nombre}'))

        # 2. Crear o actualizar la evaluación
        evaluacion, eval_created = EvaluacionDesempeño.objects.get_or_create(
            codigo='EVAL_COORD_ADMIN_2025',
            defaults={
                'tipo_evaluacion': tipo_eval,
                'nombre': 'Evaluación Anual - Coordinador Administrativo 2025',
                'descripcion': 'Evaluación de competencias para Coordinador Administrativo: Org 10%, Obj 40%, Interp 25%, Téc 25%',
                'activa': True,
                'creada_por': usuario_sistema
            }
        )

        if eval_created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Evaluación creada: {evaluacion.nombre}'))
        else:
            self.stdout.write(self.style.WARNING(f'[-] Evaluación ya existía: {evaluacion.nombre}'))
            # Eliminar preguntas antiguas para recrearlas
            PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).delete()
            self.stdout.write(self.style.WARNING('  -> Preguntas anteriores eliminadas'))

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
                    ('COMUNICACIÓN', 'Capacidad para transmitir ideas, información y opiniones de forma clara y convincente, por escrito y oralmente, escuchando activamente y siendo receptivo/a a las propuestas de los demás.'),
                    ('TRABAJO EN EQUIPO', 'Capacidad para establecer relaciones de participación y cooperación con otras personas, compartiendo recursos y conocimiento, y contribuyendo activamente al logro de los objetivos organizacionales.'),
                    ('MEJORA CONTINUA', 'Capacidad para llevar a cabo las actividades bajo estándares de calidad, buscando la mejora continua y proponiendo la adaptación y modernización de procesos y metodologías vigentes.')
                ]
            },
            {
                'nombre': 'Objetivos - El Hacer',
                'ponderacion': 40,
                'preguntas': [
                    ('PLANEAR, DIRIGIR Y CONTROLAR', 'Planear, dirigir y controlar las actividades del proceso a su cargo, asegurando el cumplimiento de las metas productivas o administrativas, la eficiencia en el uso de recursos, la calidad del servicio o producto y el bienestar y seguridad del equipo de trabajo.')
                ]
            },
            {
                'nombre': 'Competencias Interpersonales - El Ser',
                'ponderacion': 25,
                'preguntas': [
                    ('LIDERAZGO', 'Capacidad para dirigir equipos de trabajo, comunicar la visión organizacional y motivar al equipo hacia el logro de metas.\n-> Comportamiento esperado: Orienta a su equipo con claridad, mantiene la motivación y asegura el cumplimiento de las normas de seguridad.'),
                    ('TOMA DE DECISIONES', 'Capacidad para ejecutar acciones con calidad, oportunidad y conciencia de las posibles consecuencias.\n-> Comportamiento esperado: Elige soluciones rápidas y acertadas ante imprevistos sin detener la operación.'),
                    ('ORIENTACIÓN A RESULTADOS', 'Capacidad de encaminar todos los actos al logro de lo esperado, actuando con velocidad y sentido de urgencia.\n-> Comportamiento esperado: Monitorea indicadores de su proceso y toma acciones correctivas antes del cierre del período.'),
                    ('INTEGRIDAD', 'Comportarse de acuerdo con los valores morales y prácticas profesionales, siendo congruente entre el decir y el hacer.\n-> Comportamiento esperado: Actúa como modelo en el cumplimiento de procesos y es coherente entre lo que exige y lo que practica.')
                ]
            },
            {
                'nombre': 'Competencias Técnicas - El Saber',
                'ponderacion': 25,
                'preguntas': [
                    ('GESTIÓN Y CONTROL DEL PROCESO', 'Capacidad para medir indicadores del proceso, identificar desviaciones y proponer acciones de mejora.'),
                    ('PLANIFICACIÓN Y PROGRAMACIÓN', 'Habilidad para elaborar cronogramas, asignar tareas y hacer seguimiento al cumplimiento del plan.'),
                    ('CONOCIMIENTO TÉCNICO DEL ÁREA', 'Dominio profundo de los procedimientos, equipos, normativas o servicios del proceso bajo su responsabilidad.'),
                    ('MANEJO DE OFFICE / SISTEMA DE INFORMACIÓN', 'Uso eficiente de herramientas ofimáticas y del sistema de información para generar reportes e indicadores.')
                ]
            }
        ]

        # 5. Crear preguntas y opciones
        orden_pregunta = 1

        for categoria_info in categorias_data:
            categoria_nombre = categoria_info['nombre']
            ponderacion_categoria = categoria_info['ponderacion']
            preguntas = categoria_info['preguntas']
            num_preguntas = len(preguntas)
            peso_por_pregunta = ponderacion_categoria / num_preguntas

            for pregunta_titulo, pregunta_texto in preguntas:
                # Crear pregunta
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria=categoria_nombre,
                    pregunta=f'{pregunta_titulo}',
                    descripcion=pregunta_texto,
                    orden=orden_pregunta,
                    obligatoria=True,
                    peso_porcentual=peso_por_pregunta
                )

                # Crear opciones (escala 1-5)
                opciones_data = [
                    ('Muy bajo', 1, 'Desempeño muy por debajo de lo esperado'),
                    ('Bajo', 2, 'Desempeño por debajo de lo esperado'),
                    ('Moderado', 3, 'Cumple con lo esperado'),
                    ('Alto', 4, 'Supera lo esperado'),
                    ('Muy alto', 5, 'Desempeño excepcional')
                ]

                for opcion_texto, valor, _ in opciones_data:
                    OpcionEvaluacion.objects.create(
                        pregunta=pregunta,
                        opcion=opcion_texto,
                        valor_numerico=valor,
                        orden=valor
                    )

                self.stdout.write(f'  [OK] Pregunta {orden_pregunta}: {pregunta_titulo} (Peso: {peso_por_pregunta:.2f}%)')
                orden_pregunta += 1

        # 6. Crear pregunta SST (no ponderada)
        pregunta_sst = PreguntaEvaluacion.objects.create(
            evaluacion=evaluacion,
            tipo_pregunta=tipo_pregunta_escala5,
            categoria='Observación SST',
            pregunta='¿El empleado utiliza adecuadamente los Elementos de Protección Personal (EPP) y promueve su uso?',
            descripcion='Observación sobre el cumplimiento de normas de seguridad y uso de EPP. Esta pregunta no afecta la calificación de desempeño.',
            orden=orden_pregunta,
            obligatoria=False,
            peso_porcentual=0  # No cuenta para el puntaje
        )

        # Crear opciones para pregunta SST
        opciones_sst = [
            ('No los usa o no promueve su uso', 1),
            ('A veces no los usa adecuadamente', 2),
            ('Los usa correctamente y promueve su uso', 3)
        ]

        for opcion_texto, valor in opciones_sst:
            OpcionEvaluacion.objects.create(
                pregunta=pregunta_sst,
                opcion=opcion_texto,
                valor_numerico=valor,
                orden=valor
            )

        self.stdout.write(f'  [OK] Pregunta {orden_pregunta}: SST con 3 opciones (no ponderada)')

        # Resumen
        total_preguntas = PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).count()
        self.stdout.write(self.style.SUCCESS(f'\n[OK] Evaluación configurada exitosamente'))
        self.stdout.write(f'   Total preguntas: {total_preguntas} (12 evaluadas + 1 SST)')
        self.stdout.write(f'   Ponderación: Org 10%, Obj 40%, Interp 25%, Téc 25%')
        self.stdout.write(f'   Código tipo: {tipo_eval.codigo}')
        self.stdout.write(f'   Código evaluación: {evaluacion.codigo}')
