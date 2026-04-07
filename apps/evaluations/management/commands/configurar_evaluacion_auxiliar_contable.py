"""
Comando para configurar la evaluación anual de Auxiliar Contable con sistema ponderado
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
    help = 'Configura la evaluación anual para Auxiliar Contable (escala 1-5 ponderada)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando evaluacion anual para Auxiliar Contable...'))

        try:
            with transaction.atomic():
                # Obtener usuario del sistema
                usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
                if not usuario_sistema:
                    self.stdout.write(self.style.ERROR('No hay usuarios superusuarios en el sistema'))
                    return

                # 1. Obtener o crear tipo de evaluación
                tipo_eval, created = TipoEvaluacion.objects.get_or_create(
                    codigo='ANUAL_AUX_CONTABLE',
                    defaults={
                        'nombre': 'Evaluación Anual - Auxiliar Contable',
                        'descripcion': 'Evaluación anual de desempeño para auxiliar contable con sistema ponderado',
                        'dias_activacion': 365,
                        'frecuencia_dias': 365,
                        'es_autoevaluacion': False,
                        'activo': True
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'[OK] Tipo de evaluacion creado: {tipo_eval.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'[!] Tipo de evaluacion ya existe: {tipo_eval.nombre}'))

                # 2. Crear evaluación
                evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
                    codigo='EVAL_ANUAL_AUX_CONTABLE_2025',
                    defaults={
                        'tipo_evaluacion': tipo_eval,
                        'nombre': 'Evaluacion Anual Auxiliar Contable 2025',
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
                        'nombre': 'Escala 1-5',
                        'descripcion': 'Escala del 1 al 5'
                    }
                )

                # ===== 1. COMPETENCIAS ORGANIZACIONALES (10%) =====
                self.stdout.write('\n1. Creando Competencias Organizacionales (10%)...')

                orden = 1

                # Pregunta 1: COMUNICACIÓN
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='COMUNICACIÓN: Capacidad para transmitir ideas, información y opiniones de forma clara y convincente, por escrito y oralmente, escuchando activamente y siendo receptivo/a a las propuestas de los demás.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Organizacionales',
                    peso_porcentual=3.33,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                # Pregunta 2: TRABAJO EN EQUIPO
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='TRABAJO EN EQUIPO: Capacidad para establecer relaciones de participación y cooperación con otras personas, compartiendo recursos y conocimiento, y contribuyendo activamente al logro de los objetivos organizacionales.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Organizacionales',
                    peso_porcentual=3.33,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                # Pregunta 3: MEJORA CONTINUA
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='MEJORA CONTINUA: Capacidad para llevar a cabo las actividades bajo estándares de calidad, buscando la mejora continua y proponiendo la adaptación y modernización de procesos y metodologías vigentes.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Organizacionales',
                    peso_porcentual=3.34,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                self.stdout.write(self.style.SUCCESS('[OK] 3 preguntas de Competencias Organizacionales'))

                # ===== 2. OBJETIVOS - EL HACER (40%) =====
                self.stdout.write('\n2. Creando Objetivos - El Hacer (40%)...')

                # Pregunta 4: OBJETIVOS
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='Registrar, clasificar y verificar las transacciones contables de la empresa en el software contable, apoyar la elaboración de informes financieros, conciliaciones bancarias, causaciones y documentación de soporte, garantizando la exactitud, oportunidad y cumplimiento de las normas contables vigentes.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Objetivos - El Hacer',
                    peso_porcentual=40.00,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                self.stdout.write(self.style.SUCCESS('[OK] 1 pregunta de Objetivos - El Hacer'))

                # ===== 3. COMPETENCIAS INTERPERSONALES - EL SER (25%) =====
                self.stdout.write('\n3. Creando Competencias Interpersonales - El Ser (25%)...')

                # Pregunta 5: COMPROMISO Y RESPONSABILIDAD
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='COMPROMISO Y RESPONSABILIDAD: Apoyar e instrumentar decisiones comprometido/a con el logro de objetivos. Cumplir sus compromisos. → Comportamiento esperado: Entrega los registros contables en las fechas establecidas y reporta oportunamente cualquier inconsistencia.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Interpersonales - El Ser',
                    peso_porcentual=8.33,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                # Pregunta 6: ATENCIÓN AL DETALLE
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='ATENCIÓN AL DETALLE: Habilidad para procesar información numérica y contable con exactitud, efectividad y consistencia. → Comportamiento esperado: Verifica cifras, cuentas y soportes antes de registrar cualquier asiento contable.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Interpersonales - El Ser',
                    peso_porcentual=8.33,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                # Pregunta 7: CAPACIDAD DE PLANEACIÓN Y ORGANIZACIÓN
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='CAPACIDAD DE PLANEACIÓN Y ORGANIZACIÓN: Capacidad para anticipar y organizar ordenadamente las actividades contables del periodo. → Comportamiento esperado: Prioriza las causaciones y cierre del mes para no afectar los informes gerenciales.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Interpersonales - El Ser',
                    peso_porcentual=8.34,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                self.stdout.write(self.style.SUCCESS('[OK] 3 preguntas de Competencias Interpersonales - El Ser'))

                # ===== 4. COMPETENCIAS TÉCNICAS - EL SABER (25%) =====
                self.stdout.write('\n4. Creando Competencias Técnicas - El Saber (25%)...')

                # Pregunta 8: MANEJO BÁSICO DE OFFICE
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='MANEJO BÁSICO DE OFFICE: Dominio de Excel (tablas dinámicas, fórmulas, conciliaciones) y demás herramientas de Office.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Técnicas - El Saber',
                    peso_porcentual=6.25,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                # Pregunta 9: MANEJO DEL PUC
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='MANEJO DEL PUC (Plan Único de Cuentas): Conocimiento y aplicación correcta del catálogo de cuentas contables para clasificar adecuadamente las transacciones.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Técnicas - El Saber',
                    peso_porcentual=6.25,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                # Pregunta 10: MANEJO DEL SOFTWARE CONTABLE
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='MANEJO DEL SOFTWARE CONTABLE: Dominio del sistema contable de la empresa para registro de facturas, notas, pagos y generación de informes.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Técnicas - El Saber',
                    peso_porcentual=6.25,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                # Pregunta 11: CONOCIMIENTO DE NORMAS CONTABLES (NIIF BÁSICA)
                pregunta = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='CONOCIMIENTO DE NORMAS CONTABLES (NIIF BÁSICA): Comprensión de los principios contables generalmente aceptados y las Normas de Información Financiera aplicables.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Competencias Técnicas - El Saber',
                    peso_porcentual=6.25,
                    orden=orden,
                    obligatoria=True
                )
                self._crear_opciones_escala5(pregunta)
                orden += 1

                self.stdout.write(self.style.SUCCESS('[OK] 4 preguntas de Competencias Técnicas - El Saber'))

                # ===== 5. PREGUNTA SST (No afecta puntaje) =====
                self.stdout.write('\n5. Creando pregunta de Observación SST...')

                pregunta_sst = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='¿El empleado utiliza adecuadamente los Elementos de Protección Personal (EPP) y promueve su uso?',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Observación SST',
                    peso_porcentual=0,
                    orden=orden,
                    obligatoria=True
                )

                # Crear 3 opciones para SST
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

                self.stdout.write(self.style.SUCCESS('[OK] Pregunta SST creada'))

                # Resumen final
                total_preguntas = PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).count()
                self.stdout.write('')
                self.stdout.write('=' * 80)
                self.stdout.write(self.style.SUCCESS(f'[COMPLETADO] Total de preguntas creadas: {total_preguntas}'))
                self.stdout.write(self.style.SUCCESS(f'[COMPLETADO] Evaluacion Auxiliar Contable configurada exitosamente'))
                self.stdout.write('=' * 80)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Error al configurar evaluacion: {str(e)}'))
            raise

    def _crear_opciones_escala5(self, pregunta):
        """Crea las 5 opciones estándar de escala 1-5"""
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
