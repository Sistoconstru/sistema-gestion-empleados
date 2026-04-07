"""
Comando para configurar la evaluación anual de Auxiliar de RRHH.

Estructura de la evaluación:
- 11 preguntas en total
- Sistema de calificación: Escala 1-5 (Muy bajo a Muy alto)
- Sistema de ponderación por categorías:
  * Competencias Organizacionales (10%): 3 preguntas
  * Objetivos (40%): 1 pregunta
  * Competencias Interpersonales (25%): 3 preguntas
  * Competencias Técnicas (25%): 4 preguntas
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.evaluations.models import (
    TipoEvaluacion, EvaluacionDesempeño, PreguntaEvaluacion, TipoPregunta, OpcionEvaluacion
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura la evaluación anual para Auxiliar de RRHH con 11 preguntas y sistema de ponderación'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando evaluacion anual para Auxiliar de RRHH...'))

        try:
            with transaction.atomic():
                # Obtener o crear usuario sistema
                usuario_sistema, _ = User.objects.get_or_create(
                    username='sistema',
                    defaults={
                        'email': 'sistema@empresa.com',
                        'is_active': False
                    }
                )

                # 1. Crear tipo de evaluación
                tipo_eval, created = TipoEvaluacion.objects.get_or_create(
                    codigo='ANUAL_AUX_RRHH',
                    defaults={
                        'nombre': 'Evaluación Anual - Auxiliar de RRHH',
                        'descripcion': 'Evaluación anual de desempeño para auxiliares de recursos humanos con sistema ponderado',
                        'dias_activacion': 365,
                        'activo': True
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'[OK] Tipo de evaluacion creado: {tipo_eval.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'[!] Tipo de evaluacion ya existe: {tipo_eval.nombre}'))

                # 2. Crear evaluación
                evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
                    codigo='EVAL_ANUAL_AUX_RRHH_2025',
                    defaults={
                        'tipo_evaluacion': tipo_eval,
                        'nombre': 'Evaluacion Anual Auxiliar de RRHH 2025',
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
                            ('Apoyar los procesos de selección, contratación, inducción, bienestar y administración de personal', 'Gestión de novedades de nómina, afiliaciones a seguridad social, control de asistencia, archivo de hojas de vida y seguimiento a evaluaciones de desempeño, garantizando el cumplimiento de la normatividad laboral vigente.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Interpersonales',
                        'ponderacion': 25,
                        'preguntas': [
                            ('Orientación al cliente interno', 'Actitud proactiva para atender y solucionar las necesidades del personal de la organización. Comportamiento esperado: Responde oportunamente las consultas del personal sobre liquidaciones, certificaciones y novedades.'),
                            ('Discreción y confidencialidad', 'Capacidad para manejar información sensible del personal con absoluta reserva y ética profesional. Comportamiento esperado: Protege los datos personales y laborales de los empleados sin compartirlos fuera de los canales autorizados.'),
                            ('Capacidad de planeación y organización', 'Habilidad para gestionar múltiples tareas y procesos de manera simultánea y ordenada. Comportamiento esperado: Cumple los cronogramas de nómina, vencimientos de contratos y fechas de evaluación sin retrasos.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Técnicas',
                        'ponderacion': 25,
                        'preguntas': [
                            ('Gestión de nómina y seguridad social', 'Conocimiento de liquidación de nómina, horas extras, vacaciones y afiliaciones a EPS, ARL, AFP y Caja de Compensación.'),
                            ('Legislación laboral', 'Dominio básico del Código Sustantivo del Trabajo: tipos de contrato, cesantías, primas, liquidaciones.'),
                            ('Manejo de software de RRHH / Office', 'Manejo de herramientas ofimáticas y software de gestión humana para control de personal y reportes.'),
                            ('Gestión documental de personal', 'Organización y custodia de expedientes de empleados: hojas de vida, contratos, evaluaciones y afiliaciones.')
                        ]
                    }
                ]

                # 5. Crear preguntas
                self.stdout.write('')
                orden_pregunta = 1

                for categoria_info in categorias_data:
                    nombre_categoria = categoria_info['nombre']
                    ponderacion = categoria_info['ponderacion']
                    preguntas_lista = categoria_info['preguntas']
                    num_preguntas = len(preguntas_lista)
                    peso_individual = round(ponderacion / num_preguntas, 2)

                    self.stdout.write(f'  Categoria: {nombre_categoria} ({ponderacion}%)')
                    self.stdout.write(f'    -> {num_preguntas} preguntas, {peso_individual}% c/u')

                    for pregunta_titulo, pregunta_descripcion in preguntas_lista:
                        pregunta = PreguntaEvaluacion.objects.create(
                            evaluacion=evaluacion,
                            pregunta=pregunta_titulo,
                            descripcion=pregunta_descripcion,
                            tipo_pregunta=tipo_pregunta_escala5,
                            orden=orden_pregunta,
                            categoria=nombre_categoria,
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

                        self.stdout.write(f'      [OK] Pregunta {orden_pregunta}: {pregunta_titulo[:60]}...')
                        orden_pregunta += 1

                    self.stdout.write('')

                # 5. Agregar pregunta de Observación SST (no afecta puntaje)
                self.stdout.write('\n  === OBSERVACION DE SEGURIDAD Y SALUD EN EL TRABAJO (SST) ===')
                self.stdout.write('  Nota: Esta observacion es independiente y NO afecta el puntaje')

                pregunta_sst = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='¿El empleado utiliza adecuadamente los Elementos de Protección Personal (EPP) y promueve su uso?',
                    descripcion='Observación sobre el cumplimiento de normas de seguridad y uso de EPP. Esta pregunta no afecta la calificación de desempeño.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    orden=orden_pregunta,
                    categoria='Observación SST',
                    obligatoria=True
                )

                # Crear 3 opciones específicas para SST
                opciones_sst = [
                    (1, 'No los usa o no promueve su uso', 'El empleado no cumple con las normas de seguridad'),
                    (2, 'A veces no los usa adecuadamente', 'Se han observado ocasiones donde no cumple con las normas'),
                    (3, 'Los usa correctamente y promueve su uso', 'El empleado cumple completamente con las normas de seguridad')
                ]

                for valor, texto, descripcion_opcion in opciones_sst:
                    OpcionEvaluacion.objects.create(
                        pregunta=pregunta_sst,
                        opcion=texto,
                        valor_numerico=valor,
                        orden=valor
                    )

                self.stdout.write(f'      [OK] Pregunta {orden_pregunta}: Observacion SST - Uso de EPP')
                self.stdout.write('')

                # 6. Resumen final
                total_preguntas = PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).count()
                categorias_unicas = PreguntaEvaluacion.objects.filter(
                    evaluacion=evaluacion
                ).values_list('categoria', flat=True).distinct()

                self.stdout.write('=' * 80)
                self.stdout.write(self.style.SUCCESS('[OK] CONFIGURACION COMPLETADA'))
                self.stdout.write('=' * 80)
                self.stdout.write(f'Evaluacion: {evaluacion.nombre}')
                self.stdout.write(f'Total de categorias: {len(categorias_unicas)}')
                self.stdout.write(f'Total de preguntas: {total_preguntas}')
                self.stdout.write('')
                self.stdout.write('Ponderaciones configuradas:')
                for cat_info in categorias_data:
                    self.stdout.write(f'  - {cat_info["nombre"]}: {cat_info["ponderacion"]}%')
                self.stdout.write('')
                self.stdout.write('Escala de calificacion: 1-5 (Muy bajo a Muy alto)')
                self.stdout.write('Sistema de calculo: Ponderado por categorias')
                self.stdout.write('')
                self.stdout.write('Criterios de cumplimiento:')
                self.stdout.write('  - 91-100%: Muy alto')
                self.stdout.write('  - 76-90%: Alto')
                self.stdout.write('  - 61-75%: Moderado')
                self.stdout.write('  - 41-60%: Bajo')
                self.stdout.write('  - 1-40%: Muy bajo')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise


# Importar transaction después de las otras importaciones
from django.db import transaction
