"""
Comando para configurar la evaluación anual de Asesor Comercial
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
    help = 'Configura la evaluación anual de Asesor Comercial con sistema ponderado'

    def handle(self, *args, **options):
        self.stdout.write('='*80)
        self.stdout.write('CONFIGURACION DE EVALUACION ANUAL - ASESOR COMERCIAL')
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
                    codigo='ANUAL_ASESOR_COMER',
                    defaults={
                        'nombre': 'Evaluación Anual - Asesor Comercial',
                        'descripcion': 'Evaluación anual de desempeño para Asesor Comercial con sistema ponderado por categorías',
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
                    codigo='EVAL_ASESOR_COMER_2025',
                    defaults={
                        'tipo_evaluacion': tipo_eval,
                        'nombre': 'Evaluacion Anual Asesor Comercial 2025',
                        'descripcion': 'Evaluación anual de desempeño para Asesor Comercial - Sistema ponderado',
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

                    self.stdout.write(f'      [OK] Pregunta {orden_global}: {item["pregunta"][:60]}... ({item["peso"]}%)')
                    orden_global += 1

                # === OBJETIVOS - EL HACER (40%) ===
                self.stdout.write('\n  === OBJETIVOS - EL HACER (40%) ===')

                pregunta_objetivo = PreguntaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta='Gestionar y ampliar la cartera de clientes mediante la asesoría comercial, seguimiento de cotizaciones, cierre de negocios y fidelización, alcanzando las metas de ventas asignadas, garantizando la satisfacción del cliente y contribuyendo al crecimiento comercial de la organización.',
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

                self.stdout.write(f'      [OK] Pregunta {orden_global}: Objetivos - Gestion comercial (40%)')
                orden_global += 1

                # === COMPETENCIAS INTERPERSONALES - EL SER (25% total) ===
                self.stdout.write('\n  === COMPETENCIAS INTERPERSONALES - EL SER (25%) ===')

                preguntas_interpersonales = [
                    {
                        'pregunta': 'ORIENTACIÓN AL CLIENTE: Actitud permanente por detectar, anticipar y satisfacer las necesidades de los clientes.',
                        'descripcion': 'Comportamiento esperado: Hace seguimiento post-venta y anticipa las necesidades del cliente antes de que las manifieste.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'PERSUASIÓN E INFLUENCIA: Capacidad para convencer y generar confianza en los clientes a través de argumentos sólidos y escucha activa.',
                        'descripcion': 'Comportamiento esperado: Cierra negociaciones generando valor para el cliente sin comprometer los márgenes de la empresa.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'ORIENTACIÓN A RESULTADOS: Capacidad para encaminar todos los actos al logro de las metas comerciales con sentido de urgencia.',
                        'descripcion': 'Comportamiento esperado: Cumple o supera la meta de ventas mensual y mantiene actualizado la diferentes oportunidades de negocio.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'INICIATIVA Y PROACTIVIDAD: Capacidad para actuar proactivamente, identificar nuevas oportunidades y proponer soluciones.',
                        'descripcion': 'Comportamiento esperado: Prospera nuevos clientes sin esperar instrucciones y propone estrategias de fidelización al equipo.',
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
                        'pregunta': 'CONOCIMIENTO DEL PRODUCTO / SERVICIO: Dominio profundo de las características, beneficios, aplicaciones y ventajas competitivas del portafolio de la empresa.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'TÉCNICAS DE VENTAS Y NEGOCIACIÓN: Manejo de metodologías de venta consultiva, manejo de objeciones y cierre efectivo de negocios.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'CUMPLIMIENTO DE PRESUPUESTO DE VENTAS Y GESTIÓN DE CARTERA: Valor total de ventas realizadas frente al presupuesto asignado y Porcentaje de facturas recaudadas dentro de los días de crédito pactados.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'MANEJO DE OFFICE Y ELABORACIÓN DE COTIZACIONES: Dominio de Excel, Word y PowerPoint para elaborar propuestas comerciales, cotizaciones e informes de gestión.',
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
