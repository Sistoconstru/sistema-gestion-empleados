"""
Comando para configurar la evaluación anual de Auxiliares Administrativos con sistema ponderado
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.evaluations.models import (
    TipoEvaluacion,
    EvaluacionDesempeño,
    PreguntaEvaluacion,
    TipoPregunta,
    OpcionEvaluacion
)
from apps.authentication.models import Usuario


class Command(BaseCommand):
    help = 'Configura la evaluación anual para Auxiliares Administrativos (escala 1-5 ponderada)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando evaluacion anual para Auxiliares Administrativos...'))

        try:
            with transaction.atomic():
                # Obtener usuario del sistema
                usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
                if not usuario_sistema:
                    self.stdout.write(self.style.ERROR('No hay usuarios superusuarios en el sistema'))
                    return

                # 1. Obtener o crear tipo de evaluación
                tipo_eval, created = TipoEvaluacion.objects.get_or_create(
                    codigo='ANUAL_AUX_ADMIN',
                    defaults={
                        'nombre': 'Evaluación Anual - Auxiliares Administrativos',
                        'descripcion': 'Evaluación anual de desempeño para auxiliares administrativos con sistema ponderado',
                        'dias_activacion': 365,  # Se asigna al cumplir un año
                        'activo': True
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'[OK] Tipo de evaluacion creado: {tipo_eval.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'[!] Tipo de evaluacion ya existe: {tipo_eval.nombre}'))

                # 2. Crear evaluación
                evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
                    codigo='EVAL_ANUAL_AUX_ADMIN_2025',
                    defaults={
                        'tipo_evaluacion': tipo_eval,
                        'nombre': 'Evaluacion Anual Auxiliares Administrativos 2025',
                        'descripcion': 'Evaluacion anual con escala 1-5 y sistema de ponderacion por categorias',
                        'activa': True,
                        'creada_por': usuario_sistema
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'[OK] Evaluacion creada: {evaluacion.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'[!] Evaluacion ya existe: {evaluacion.nombre}'))
                    # Limpiar preguntas existentes para reconfigurar
                    PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).delete()
                    self.stdout.write(self.style.WARNING('  Preguntas anteriores eliminadas para reconfiguracion'))

                # 3. Obtener tipo de pregunta ESCALA_5
                tipo_pregunta_escala5, _ = TipoPregunta.objects.get_or_create(
                    codigo='ESCALA_5',
                    defaults={
                        'nombre': 'Escala Likert 1-5',
                        'descripcion': 'Escala de 1 a 5 (Muy bajo a Muy alto)'
                    }
                )

                # 4. Crear categorías con ponderación
                categorias_data = [
                    {
                        'nombre': 'Competencias Organizacionales',
                        'ponderacion': 10,
                        'preguntas': [
                            ('Comunicación', 'Capacidad para transmitir ideas, información y opiniones de forma clara y convincente, por escrito y oralmente, escuchando activamente y siendo receptivo/a a las propuestas de los demás.'),
                            ('Trabajo en equipo', 'Capacidad para establecer relaciones de participación y cooperación con otras personas, compartiendo recursos y conocimiento, y contribuyendo activamente al logro de los objetivos organizacionales.'),
                            ('Mejora continua', 'Capacidad para llevar a cabo las actividades bajo estándares de calidad, buscando la mejora continua y proponiendo la adaptación y modernización de procesos y metodologías vigentes.')
                        ]
                    },
                    {
                        'nombre': 'Objetivos',
                        'ponderacion': 40,
                        'preguntas': [
                            ('Brindar soporte operativo y administrativo', 'Brindar soporte operativo y administrativo a los diferentes procesos organizacionales: gestión documental, atención a clientes internos/externos, manejo de correspondencia, apoyo en trámites y actividades de oficina, garantizando eficiencia, orden y oportunidad en cada tarea.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Interpersonales',
                        'ponderacion': 25,
                        'preguntas': [
                            ('Orientación al cliente', 'Actitud permanente por detectar y satisfacer las necesidades y prioridades de los clientes internos y externos. → Comportamiento esperado: Resuelve solicitudes de manera oportuna y con actitud de servicio, anticipando necesidades.'),
                            ('Atención al detalle', 'Habilidad para procesar información detallada con efectividad y consistencia. → Comportamiento esperado: Revisa documentos y registros antes de radicarlos o enviarlos, evitando errores.'),
                            ('Capacidad de planeación y organización', 'Capacidad para anticipar y asignar de manera lógica y ordenada las acciones a seguir. → Comportamiento esperado: Organiza su agenda y prioridades diarias sin necesidad de supervisión constante.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Técnicas',
                        'ponderacion': 25,
                        'preguntas': [
                            ('Manejo básico de Office', 'Dominio de Word, Excel y PowerPoint para elaboración de documentos, informes y presentaciones.'),
                            ('Gestión documental y archivo', 'Conocimiento y aplicación de técnicas de clasificación, radicación, almacenamiento y custodia de documentos.'),
                            ('Manejo de software contable/administrativo', 'Capacidad para operar el sistema de información de la empresa (facturación, órdenes, correspondencia).'),
                            ('Conocimiento básico contable', 'Comprensión de conceptos contables básicos para apoyar procesos de facturación y cuentas por cobrar/pagar.')
                        ]
                    }
                ]

                orden_global = 1
                total_preguntas = sum(len(cat['preguntas']) for cat in categorias_data)

                for cat_data in categorias_data:
                    categoria_nombre = cat_data['nombre']
                    num_preguntas = len(cat_data['preguntas'])
                    peso_por_pregunta = round(cat_data['ponderacion'] / num_preguntas, 2)

                    self.stdout.write(f'\n  Categoria: {categoria_nombre} ({cat_data["ponderacion"]}%)')
                    self.stdout.write(f'    -> {num_preguntas} preguntas, {peso_por_pregunta}% c/u')

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

                        self.stdout.write(f'      [OK] Pregunta {orden_global}: {pregunta_texto[:60]}...')
                        orden_global += 1

                # Resumen final
                self.stdout.write('\n' + '='*80)
                self.stdout.write(self.style.SUCCESS('[OK] CONFIGURACION COMPLETADA'))
                self.stdout.write('='*80)
                self.stdout.write(f'Evaluacion: {evaluacion.nombre}')
                self.stdout.write(f'Total de categorias: {len(categorias_data)}')
                self.stdout.write(f'Total de preguntas: {total_preguntas}')
                self.stdout.write('\nPonderaciones configuradas:')
                for cat in categorias_data:
                    self.stdout.write(f'  - {cat["nombre"]}: {cat["ponderacion"]}%')
                self.stdout.write('\nEscala de calificacion: 1-5 (Muy bajo a Muy alto)')
                self.stdout.write('Sistema de calculo: Ponderado por categorias')
                self.stdout.write('\nCriterios de cumplimiento:')
                self.stdout.write('  - 91-100%: Muy alto')
                self.stdout.write('  - 76-90%: Alto')
                self.stdout.write('  - 61-75%: Moderado')
                self.stdout.write('  - 41-60%: Bajo')
                self.stdout.write('  - 1-40%: Muy bajo')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Error: {str(e)}'))
            raise
