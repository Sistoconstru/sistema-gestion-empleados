"""
Comando para configurar la evaluación anual de Directores
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
    help = 'Configura la evaluación anual de Directores con sistema ponderado'

    def handle(self, *args, **options):
        self.stdout.write('='*80)
        self.stdout.write('CONFIGURACION DE EVALUACION ANUAL - DIRECTORES')
        self.stdout.write('='*80)

        try:
            with transaction.atomic():
                # Obtener usuario del sistema para asignar como creador
                usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
                if not usuario_sistema:
                    self.stdout.write(self.style.ERROR('No se encontró un superusuario en el sistema'))
                    return

                # 1. Crear o obtener tipo de evaluación
                self.stdout.write('\n1. Creando tipo de evaluacion...')
                tipo_eval, created = TipoEvaluacion.objects.get_or_create(
                    codigo='ANUAL_DIRECTOR',
                    defaults={
                        'nombre': 'Evaluación Anual - Directores',
                        'descripcion': 'Evaluación anual de desempeño para Directores con sistema ponderado por categorías',
                        'dias_activacion': 365,
                        'frecuencia_dias': 365,
                        'es_autoevaluacion': False,
                        'activo': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'   [OK] Tipo de evaluacion creado: {tipo_eval.codigo}'))
                else:
                    self.stdout.write(self.style.WARNING(f'   [INFO] Tipo de evaluacion ya existia: {tipo_eval.codigo}'))

                # 2. Crear o obtener evaluación
                self.stdout.write('\n2. Creando evaluacion...')
                evaluacion, created = EvaluacionDesempeño.objects.get_or_create(
                    codigo='EVAL_DIRECTOR_2025',
                    defaults={
                        'tipo_evaluacion': tipo_eval,
                        'nombre': 'Evaluacion Anual Directores 2025',
                        'descripcion': 'Evaluación anual de desempeño para Directores - Sistema ponderado',
                        'activa': True,
                        'creada_por': usuario_sistema
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'   [OK] Evaluacion creada: {evaluacion.codigo}'))
                else:
                    self.stdout.write(self.style.WARNING(f'   [INFO] Evaluacion ya existia: {evaluacion.codigo}'))
                    # Si ya existe, verificar si ya tiene preguntas
                    if PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).exists():
                        self.stdout.write(self.style.WARNING('   [INFO] La evaluacion ya tiene preguntas configuradas'))
                        self.stdout.write(self.style.WARNING('   [INFO] Saliendo sin modificar...'))
                        return

                # 3. Obtener tipo de pregunta (escala 1-5)
                self.stdout.write('\n3. Obteniendo tipo de pregunta...')
                tipo_pregunta_escala5, _ = TipoPregunta.objects.get_or_create(
                    codigo='ESCALA_5',
                    defaults={
                        'nombre': 'Escala 1-5',
                        'descripcion': 'Escala numérica del 1 al 5'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'   [OK] Tipo de pregunta: {tipo_pregunta_escala5.nombre}'))

                # 4. Crear preguntas
                self.stdout.write('\n4. Creando preguntas de evaluacion...')
                self.stdout.write('   Distribucion de pesos:')
                self.stdout.write('   - Competencias Organizacionales (10%): 3.33%, 3.33%, 3.34%')
                self.stdout.write('   - Objetivos - El Hacer (40%): 40%')
                self.stdout.write('   - Competencias Interpersonales - El Ser (25%): 6.25% cada una (4 preguntas)')
                self.stdout.write('   - Competencias Tecnicas - El Saber (25%): 6.25% cada una (4 preguntas)')

                orden_global = 1

                # === COMPETENCIAS ORGANIZACIONALES (10% total) ===
                self.stdout.write('\n  === COMPETENCIAS ORGANIZACIONALES (10%) ===')

                preguntas_organizacionales = [
                    {
                        'pregunta': 'COMUNICACIÓN: Capacidad para transmitir ideas, información y opiniones de forma clara y convincente, por escrito y oralmente, escuchando activamente y siendo receptivo/a a las propuestas de los demás.',
                        'peso': 3.33
                    },
                    {
                        'pregunta': 'TRABAJO EN EQUIPO: Capacidad para establecer relaciones de participación y cooperación con otras personas, compartiendo recursos y conocimiento, y contribuyendo activamente al logro de los objetivos organizacionales.',
                        'peso': 3.33
                    },
                    {
                        'pregunta': 'MEJORA CONTINUA: Capacidad para llevar a cabo las actividades bajo estándares de calidad, buscando la mejora continua y proponiendo la adaptación y modernización de procesos y metodologías vigentes.',
                        'peso': 3.34
                    }
                ]

                # Crear opciones 1-5
                opciones = [
                    (1, 'Muy bajo'),
                    (2, 'Bajo'),
                    (3, 'Moderado'),
                    (4, 'Alto'),
                    (5, 'Muy alto')
                ]

                for item in preguntas_organizacionales:
                    pregunta = PreguntaEvaluacion.objects.create(
                        evaluacion=evaluacion,
                        pregunta=item['pregunta'],
                        tipo_pregunta=tipo_pregunta_escala5,
                        categoria='Competencias Organizacionales',
                        orden=orden_global,
                        peso_porcentual=item['peso'],
                        obligatoria=True
                    )

                    for valor, texto in opciones:
                        OpcionEvaluacion.objects.create(
                            pregunta=pregunta,
                            opcion=texto,
                            valor_numerico=valor,
                            orden=valor
                        )

                    self.stdout.write(f'      [OK] Pregunta {orden_global}: {item["pregunta"][:60]}... ({item["peso"]}%)')
                    orden_global += 1

                # === OBJETIVOS - EL HACER (40%) ===
                self.stdout.write('\n  === OBJETIVOS - EL HACER (40%) ===')

                pregunta_objetivo = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='Diseñar, implementar y controlar la estrategia del área bajo su responsabilidad, asegurando el cumplimiento de los objetivos organizacionales, la gestión eficiente de los recursos, el desarrollo del equipo y la alineación con la visión, misión y valores de la empresa.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Objetivos - El Hacer',
                    orden=orden_global,
                    peso_porcentual=40.0,
                    obligatoria=True
                )

                for valor, texto in opciones:
                    OpcionEvaluacion.objects.create(
                        pregunta=pregunta_objetivo,
                        opcion=texto,
                        valor_numerico=valor,
                        orden=valor
                    )

                self.stdout.write(f'      [OK] Pregunta {orden_global}: Objetivos - Gestion directiva estrategica (40%)')
                orden_global += 1

                # === COMPETENCIAS INTERPERSONALES - EL SER (25% total) ===
                self.stdout.write('\n  === COMPETENCIAS INTERPERSONALES - EL SER (25%) ===')

                preguntas_interpersonales = [
                    {
                        'pregunta': 'LIDERAZGO ESTRATÉGICO: Capacidad para dirigir equipos de trabajo, comunicar la visión y estrategia organizacional y movilizar a las personas hacia el logro de objetivos.',
                        'descripcion': 'Comportamiento esperado: Define metas claras para su equipo, hace seguimiento sistemático y reconoce los logros alcanzados.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'PENSAMIENTO ESTRATÉGICO: Habilidad para comprender el entorno, identificar oportunidades y amenazas, y diseñar respuestas estratégicas.',
                        'descripcion': 'Comportamiento esperado: Elabora planes que permiten anticipar riesgos y aprovechar oportunidades del mercado o del entorno interno.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'TOMA DE DECISIONES BAJO PRESIÓN: Capacidad para analizar información, evaluar alternativas y tomar decisiones acertadas en condiciones de incertidumbre.',
                        'descripcion': 'Comportamiento esperado: Resuelve situaciones críticas con criterio y velocidad, asumiendo la responsabilidad de sus decisiones.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'DESARROLLO DE PERSONAS: Capacidad para identificar el potencial del equipo, brindar retroalimentación constructiva y promover el crecimiento.',
                        'descripcion': 'Comportamiento esperado: Realiza acompañamiento continuo a su equipo y promueve planes de desarrollo individual para las personas a cargo.',
                        'peso': 6.25
                    }
                ]

                for item in preguntas_interpersonales:
                    pregunta = PreguntaEvaluacion.objects.create(
                        evaluacion=evaluacion,
                        pregunta=item['pregunta'],
                        descripcion=item.get('descripcion', ''),
                        tipo_pregunta=tipo_pregunta_escala5,
                        categoria='Competencias Interpersonales - El Ser',
                        orden=orden_global,
                        peso_porcentual=item['peso'],
                        obligatoria=True
                    )

                    for valor, texto in opciones:
                        OpcionEvaluacion.objects.create(
                            pregunta=pregunta,
                            opcion=texto,
                            valor_numerico=valor,
                            orden=valor
                        )

                    self.stdout.write(f'      [OK] Pregunta {orden_global}: {item["pregunta"][:60]}... ({item["peso"]}%)')
                    orden_global += 1

                # === COMPETENCIAS TÉCNICAS - EL SABER (25% total) ===
                self.stdout.write('\n  === COMPETENCIAS TECNICAS - EL SABER (25%) ===')

                preguntas_tecnicas = [
                    {
                        'pregunta': 'GESTIÓN FINANCIERA Y PRESUPUESTAL: Capacidad para elaborar, controlar y optimizar presupuestos, tomar decisiones con base en indicadores.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'PLANIFICACIÓN ESTRATÉGICA Y OPERATIVA: Habilidad para definir objetivos, indicadores y planes de acción de corto, mediano y largo plazo.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'GESTIÓN DE INDICADORES Y REPORTING: Capacidad para diseñar, monitorear y presentar tableros de control con indicadores clave del área.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'MANEJO AVANZADO DE HERRAMIENTAS DE GESTIÓN: Dominio de herramientas ofimáticas avanzadas, ERP, sistemas de información y metodologías de gestión de proyectos.',
                        'peso': 6.25
                    }
                ]

                for item in preguntas_tecnicas:
                    pregunta = PreguntaEvaluacion.objects.create(
                        evaluacion=evaluacion,
                        pregunta=item['pregunta'],
                        tipo_pregunta=tipo_pregunta_escala5,
                        categoria='Competencias Técnicas - El Saber',
                        orden=orden_global,
                        peso_porcentual=item['peso'],
                        obligatoria=True
                    )

                    for valor, texto in opciones:
                        OpcionEvaluacion.objects.create(
                            pregunta=pregunta,
                            opcion=texto,
                            valor_numerico=valor,
                            orden=valor
                        )

                    self.stdout.write(f'      [OK] Pregunta {orden_global}: {item["pregunta"][:60]}... ({item["peso"]}%)')
                    orden_global += 1

                # === OBSERVACIÓN SST (no afecta puntaje) ===
                self.stdout.write('\n  === OBSERVACION DE SEGURIDAD Y SALUD EN EL TRABAJO (SST) ===')
                self.stdout.write('  Nota: Esta observacion es independiente y NO afecta el puntaje')

                pregunta_sst = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='¿El empleado utiliza adecuadamente los Elementos de Protección Personal (EPP) y promueve su uso?',
                    descripcion='Observación sobre el cumplimiento de normas de seguridad y uso de EPP. Esta pregunta no afecta la calificación de desempeño.',
                    tipo_pregunta=tipo_pregunta_escala5,
                    categoria='Observación SST',
                    orden=orden_global,
                    peso_porcentual=0,  # No afecta el puntaje
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

                self.stdout.write(f'      [OK] Pregunta {orden_global}: Observacion SST - Uso de EPP')

                # Resumen final
                self.stdout.write('\n' + '='*80)
                self.stdout.write(self.style.SUCCESS('[OK] CONFIGURACION COMPLETADA'))
                self.stdout.write('='*80)
                self.stdout.write(f'Evaluacion: {evaluacion.nombre}')
                self.stdout.write(f'Codigo: {evaluacion.codigo}')
                self.stdout.write(f'Total de preguntas: {orden_global} (12 evaluadas + 1 SST)')
                self.stdout.write(f'Distribucion:')
                self.stdout.write(f'  - Competencias Organizacionales: 10% (3 preguntas)')
                self.stdout.write(f'  - Objetivos - El Hacer: 40% (1 pregunta)')
                self.stdout.write(f'  - Competencias Interpersonales: 25% (4 preguntas)')
                self.stdout.write(f'  - Competencias Tecnicas: 25% (4 preguntas)')
                self.stdout.write(f'  - Observacion SST: 0% (1 pregunta)')
                self.stdout.write('='*80)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la configuracion: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise
