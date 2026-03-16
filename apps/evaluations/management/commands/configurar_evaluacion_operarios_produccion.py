"""
Comando para configurar la evaluación anual de Operarios de Producción con sistema ponderado
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
from apps.evaluations.utils.respuestas_predefinidas_operarios_produccion import PONDERACION_CATEGORIAS


class Command(BaseCommand):
    help = 'Configura la evaluación anual para Operarios de Producción (escala 1-5 ponderada)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando evaluación anual para Operarios de Producción...'))

        try:
            with transaction.atomic():
                # Obtener usuario del sistema
                usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
                if not usuario_sistema:
                    self.stdout.write(self.style.ERROR('No hay usuarios superusuarios en el sistema'))
                    return

                # 1. Obtener o crear tipo de evaluación
                tipo_eval, created = TipoEvaluacion.objects.get_or_create(
                    codigo='ANUAL_OPERARIOS_PROD',
                    defaults={
                        'nombre': 'Evaluación Anual - Operarios de Producción',
                        'descripcion': 'Evaluación anual de desempeño para operarios de producción con sistema ponderado',
                        'dias_activacion': 365,  # Se asigna al cumplir un año
                        'activo': True
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Tipo de evaluación creado: {tipo_eval.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ Tipo de evaluación ya existe: {tipo_eval.nombre}'))

                # 2. Crear evaluación
                evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
                    tipo_evaluacion=tipo_eval,
                    nombre='Evaluación Anual Operarios de Producción 2025',
                    defaults={
                        'descripcion': 'Evaluación anual con escala 1-5 y sistema de ponderación por categorías',
                        'activa': True,
                        'creada_por': usuario_sistema
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Evaluación creada: {evaluacion.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ Evaluación ya existe: {evaluacion.nombre}'))
                    # Limpiar preguntas existentes para reconfigurar
                    PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).delete()
                    self.stdout.write(self.style.WARNING('  Preguntas anteriores eliminadas para reconfiguración'))

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
                            ('Comunicación', 'Capacidad para comunicar, de forma voluntaria, transmitir ideas, información y opiniones de forma clara y convincente.'),
                            ('Trabajo en equipo', 'Capacidad para establecer relaciones de participación y cooperación con otras personas.'),
                            ('Mejora continua', 'Capacidad para llevar a cabo las actividades, funciones y responsabilidades inherentes al puesto de trabajo bajo estándares de calidad.')
                        ]
                    },
                    {
                        'nombre': 'Objetivos',
                        'ponderacion': 40,
                        'preguntas': [
                            ('Operación de equipos y máquinas', 'Operar, controlar y mantener equipos y máquinas industriales para la transformación de la madera, asegurando el cumplimiento de medidas, estándares de calidad y normas de seguridad.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Interpersonales',
                        'ponderacion': 25,
                        'preguntas': [
                            ('Atención al detalle', 'Capacidad de reducir errores revisando sistemáticamente las tareas. Comportamiento esperado: Detecta desviaciones en medidas de manera antes de que pase al siguiente proceso.'),
                            ('Dinamismo y Energía', 'Habilidad para trabajar duro en jornadas prolongadas y situaciones cambiantes. Comportamiento esperado: Mantiene el ritmo de producción constante sin afectar la seguridad.'),
                            ('Tolerancia a la Presión', 'Seguir actuando con eficacia bajo exigencia de tiempo o desacuerdos. Comportamiento esperado: Responde bien ante picos de producción o fallas inesperadas en la máquina.'),
                            ('Productividad', 'Capacidad de lograr resultados con los estándares de calidad esperados. Comportamiento esperado: Optimiza el uso de la materia prima para evitar desperdicios.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Técnicas',
                        'ponderacion': 25,
                        'preguntas': [
                            ('Operación técnica de la máquina', 'Configuración de medidas y cambio de cuchillas según la orden.'),
                            ('Mantenimiento Preventivo', 'Diligenciamiento correcto del formato de estado de máquina y limpieza.'),
                            ('Calidad del Producto', 'Minimización de maderas inconformes por errores o problemas de calidad.')
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
                self.stdout.write('\nCriterios de cumplimiento:')
                self.stdout.write('  • 91-100%: Muy alto')
                self.stdout.write('  • 76-90%: Alto')
                self.stdout.write('  • 61-75%: Moderado')
                self.stdout.write('  • 41-60%: Bajo')
                self.stdout.write('  • 1-40%: Muy bajo')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
            raise
