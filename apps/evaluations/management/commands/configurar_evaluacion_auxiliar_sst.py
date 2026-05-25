"""
Comando para configurar la evaluación anual de Auxiliar de SST
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.evaluations.models import (
    TipoEvaluacion,
    EvaluacionDesempeño,
    PreguntaEvaluacion,
    OpcionEvaluacion,
    TipoPregunta
)
from apps.authentication.models import Usuario


class Command(BaseCommand):
    help = 'Configura la evaluación anual de Auxiliar de SST con sistema ponderado'

    def handle(self, *args, **options):
        self.stdout.write('='*80)
        self.stdout.write('CONFIGURACION DE EVALUACION ANUAL - AUXILIAR DE SST')
        self.stdout.write('='*80)

        try:
            with transaction.atomic():
                # Obtener usuario del sistema
                usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
                if not usuario_sistema:
                    self.stdout.write(self.style.ERROR('No se encontró un superusuario'))
                    return

                # 1. Crear tipo de evaluación
                self.stdout.write('\n1. Creando tipo de evaluacion...')
                tipo_eval, created = TipoEvaluacion.objects.get_or_create(
                    codigo='ANUAL_AUX_SST',
                    defaults={
                        'nombre': 'Evaluación Anual - Auxiliar de SST',
                        'descripcion': 'Evaluación anual de desempeño para Auxiliar de Seguridad y Salud en el Trabajo',
                        'dias_activacion': 365,
                        'frecuencia_dias': 365,
                        'es_autoevaluacion': False,
                        'activo': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'   [OK] Tipo de evaluacion creado: {tipo_eval.codigo}'))
                else:
                    self.stdout.write(self.style.WARNING(f'   [INFO] Tipo ya existia: {tipo_eval.codigo}'))

                # 2. Crear evaluación
                self.stdout.write('\n2. Creando evaluacion...')
                evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
                    codigo='EVAL_AUX_SST_2025',
                    defaults={
                        'tipo_evaluacion': tipo_eval,
                        'nombre': 'Evaluacion Anual Auxiliar de SST 2025',
                        'descripcion': 'Evaluación anual de desempeño para Auxiliar de Seguridad y Salud en el Trabajo',
                        'activa': True,
                        'creada_por': usuario_sistema
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'   [OK] Evaluacion creada: {evaluacion.codigo}'))
                else:
                    self.stdout.write(self.style.WARNING(f'   [INFO] Evaluacion ya existia'))
                    if PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).exists():
                        self.stdout.write(self.style.WARNING('   Ya tiene preguntas. Saliendo...'))
                        return

                # 3. Obtener tipo de pregunta
                self.stdout.write('\n3. Obteniendo tipo de pregunta...')
                tipo_pregunta_escala5, _ = TipoPregunta.objects.get_or_create(
                    codigo='ESCALA_5',
                    defaults={
                        'nombre': 'Escala 1-5',
                        'descripcion': 'Escala numérica del 1 al 5'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'   [OK] Tipo de pregunta: {tipo_pregunta_escala5.nombre}'))

                # 4. Configurar categorías y preguntas
                self.stdout.write('\n4. Creando preguntas...')
                self.stdout.write('   Distribucion:')
                self.stdout.write('   - Competencias Organizacionales (10%): 3 preguntas')
                self.stdout.write('   - Objetivos (40%): 1 pregunta')
                self.stdout.write('   - Competencias Interpersonales (25%): 3 preguntas')
                self.stdout.write('   - Competencias Tecnicas (25%): 5 preguntas')

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
                            ('Ejecutar operativamente las actividades de campo del SG-SST', 'Ejecutar operativamente las actividades de campo del SG-SST de Construinmuniza: inspecciones diarias de planta, control y entrega de EPP, gestión documental del sistema, apoyo en capacitaciones y plan de emergencias, garantizando condiciones seguras de trabajo para todos los colaboradores en todas las sedes, bajo la dirección del Coordinador y Director de SST.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Interpersonales - El Ser',
                        'ponderacion': 25,
                        'preguntas': [
                            ('COMPROMISO Y RESPONSABILIDAD', 'Cumplir a cabalidad con los compromisos adquiridos, actuando con integridad en el manejo de recursos económicos. → Comportamiento esperado: Realiza consignaciones, pagos y cierres de caja en los horarios y fechas establecidos sin necesidad de recordatorios.'),
                            ('ATENCIÓN AL DETALLE', 'Habilidad para revisar y procesar información financiera y bancaria con exactitud, detectando errores antes de que se materialicen. → Comportamiento esperado: Verifica que cada comprobante de pago coincida con el soporte, la orden y el valor autorizado antes de ejecutar la transacción.'),
                            ('ORIENTACIÓN AL CLIENTE INTERNO', 'Actitud proactiva para atender con eficiencia las solicitudes de pago, reembolsos y consultas del personal interno. → Comportamiento esperado: Responde oportunamente las solicitudes de pagos a proveedores y anticipa las fechas de vencimiento para no generar mora.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Técnicas - El Saber',
                        'ponderacion': 25,
                        'preguntas': [
                            ('PLANEACIÓN Y CUMPLIMIENTO DE ACTIVIDADES', 'Capacidad para organizar, ejecutar y dar seguimiento a las tareas asignadas, garantizando el cumplimiento oportuno de cronogramas, frecuencias y coberturas establecidas.'),
                            ('ORGANIZACIÓN DOCUMENTAL', 'Mantiene los registros del SG-SST organizados cronológicamente, completos y listos para auditorías internas o externas.'),
                            ('NORMATIVIDAD EN SALUD Y SEGURIDAD', 'Demuestra conocimiento básico de la normatividad vigente en Seguridad y Salud en el Trabajo (SST), identificando sus campos de aplicación y aplicándola adecuadamente en el desarrollo de sus funciones. Reconoce la importancia del cumplimiento de las normas de seguridad y participa activamente en la prevención de riesgos laborales.'),
                            ('MANEJO BÁSICO DE OFFICE / EXCEL', 'Demuestra manejo básico de herramientas ofimáticas (Word, Excel, correo electrónico y plataformas digitales), utilizándolas para el registro, control y seguimiento de información relacionada con equipos, elementos de protección personal (EPP), extintores y demás implementos de seguridad de la organización.'),
                            ('CONTROL Y SEGUIMIENTO DE IMPLEMENTOS Y EQUIPOS DE SEGURIDAD', 'Realiza el control, inspección y seguimiento de los implementos y equipos de seguridad de la organización, tales como extintores, elementos de protección personal (EPP), botiquines y demás recursos de prevención, garantizando su disponibilidad, buen estado y cumplimiento de los requisitos establecidos.')
                        ]
                    }
                ]

                orden_global = 1
                total_preguntas = sum(len(cat['preguntas']) for cat in categorias_data)

                for cat_data in categorias_data:
                    categoria_nombre = cat_data['nombre']
                    num_preguntas = len(cat_data['preguntas'])
                    peso_por_pregunta = round(cat_data['ponderacion'] / num_preguntas, 2)

                    self.stdout.write(f'\n  === {categoria_nombre.upper()} ({cat_data["ponderacion"]}%) ===')
                    self.stdout.write(f'    -> {num_preguntas} preguntas, {peso_por_pregunta}% c/u')

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

                        # Crear opciones 1-5
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

                # Pregunta SST
                self.stdout.write('\n  === OBSERVACION SST ===')
                pregunta_sst = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='¿El empleado utiliza adecuadamente los Elementos de Protección Personal (EPP) y promueve su uso?',
                    descripcion='Observación sobre el cumplimiento de normas de seguridad y uso de EPP. No afecta la calificación.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Observación SST',
                    orden=orden_global,
                    peso_porcentual=0,
                    obligatoria=True
                )

                opciones_sst = [
                    (1, 'No los usa o no promueve su uso'),
                    (2, 'A veces no los usa adecuadamente'),
                    (3, 'Los usa correctamente y promueve su uso')
                ]

                for valor, texto in opciones_sst:
                    OpcionEvaluacion.objects.create(
                        pregunta=pregunta_sst,
                        opcion=texto,
                        valor_numerico=valor,
                        orden=valor
                    )

                self.stdout.write(f'      [OK] Pregunta {orden_global}: Observacion SST')

                # Resumen
                self.stdout.write('\n' + '='*80)
                self.stdout.write(self.style.SUCCESS('[OK] CONFIGURACION COMPLETADA'))
                self.stdout.write('='*80)
                self.stdout.write(f'Evaluacion: {evaluacion.nombre}')
                self.stdout.write(f'Total de preguntas: {total_preguntas} evaluadas + 1 SST')
                self.stdout.write('\nDistribucion:')
                for cat in categorias_data:
                    self.stdout.write(f'  - {cat["nombre"]}: {cat["ponderacion"]}% ({len(cat["preguntas"])} preguntas)')
                self.stdout.write('='*80)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise
