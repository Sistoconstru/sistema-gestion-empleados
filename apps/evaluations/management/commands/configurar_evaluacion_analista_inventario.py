"""
Comando para configurar la evaluación anual de Analista de Inventario
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
    help = 'Configura la evaluación anual de Analista de Inventario con sistema ponderado'

    def handle(self, *args, **options):
        self.stdout.write('='*80)
        self.stdout.write('CONFIGURACION DE EVALUACION ANUAL - ANALISTA DE INVENTARIO')
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
                    codigo='ANUAL_ANALISTA_INV',
                    defaults={
                        'nombre': 'Evaluación Anual - Analista de Inventario',
                        'descripcion': 'Evaluación anual de desempeño para Analista de Inventario con sistema ponderado por categorías',
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
                    codigo='EVAL_ANALISTA_INVENT_2025',
                    defaults={
                        'tipo_evaluacion': tipo_eval,
                        'nombre': 'Evaluacion Anual Analista de Inventario 2025',
                        'descripcion': 'Evaluación anual de desempeño para Analista de Inventario - Sistema ponderado',
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

                # Opciones 1-5
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
                    pregunta='Gestionar el ciclo completo de inventarios de Construmuniza: control de órdenes de pedido pendientes, asignación de madera producida, carga y ajuste de producto terminado en el sistema, preparación y toma del inventario trimestral, compras de comercialización garantizando la disponibilidad y confiabilidad del stock para la operación comercial y productiva.',
                    descripcion='Comportamiento esperado: Sus informes no presentan errores y reflejan fielmente la realidad de los inventarios de la empresa.',
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

                self.stdout.write(f'      [OK] Pregunta {orden_global}: Objetivos - Gestion completa de inventarios (40%)')
                orden_global += 1

                # === COMPETENCIAS INTERPERSONALES - EL SER (25% total) ===
                self.stdout.write('\n  === COMPETENCIAS INTERPERSONALES - EL SER (25%) ===')

                preguntas_interpersonales = [
                    {
                        'pregunta': 'CALIDAD EN EL TRABAJO: Amplios conocimientos del área bajo su responsabilidad. Capacidad para analizar aspectos complejos y discernir con equilibrio.',
                        'descripcion': 'Comportamiento esperado: Sus informes no presentan errores y reflejan fielmente la realidad de los inventarios de la empresa.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'ATENCIÓN AL DETALLE: Detecta diferencias entre lo físico y el sistema antes de cerrar el inventario. Revisa consecutivos de movimientos diariamente sin omitir registros.',
                        'descripcion': 'Comportamiento esperado: Identifica y reporta incongruencias antes de que generen problemas operativos.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'CAPACIDAD DE PLANEACIÓN Y PROGRAMACIÓN: Organiza la secuencia de asignaciones, compras de comercialización y preparación del inventario trimestral con anticipación suficiente.',
                        'descripcion': 'Comportamiento esperado: Las tareas críticas del área se ejecutan sin contratiempos por falta de preparación previa.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'COMUNICACIÓN EFECTIVA: Capacidad para coordinar con producción y ventas sobre la disponibilidad de materiales.',
                        'descripcion': 'Comportamiento esperado: Informa oportunamente sobre faltantes o excesos de stock para evitar paros.',
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
                        'pregunta': 'ERP AVANZADO: Dominio de OPs, remisiones, ajustes, carga de producción, traslados entre sedes, consultas de inventario en tiempo real y resolución de negativos en el sistema.',
                        'descripcion': 'Comportamiento esperado: Opera el sistema con autonomía total sin requerir soporte para las funciones del cargo.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'GESTIÓN DE INVENTARIOS - SECTOR MADERERO: Metodologías de toma física, valorización por costo promedio, política de asignación y control de diferencias en un entorno de producto natural con variabilidad de volumen.',
                        'descripcion': 'Comportamiento esperado: Aplica criterio para diferenciar entre errores del sistema y variaciones propias del producto natural.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'MANEJO AVANZADO DEL SOFTWARE CONTABLE: Dominio del sistema contable para generación de estados financieros, informes de gestión y reportes fiscales.',
                        'peso': 6.25
                    },
                    {
                        'pregunta': 'CONOCIMIENTO DE PLATAFORMAS DIAN, BANCOS Y PARAFISCALES: Dominio de los portales de la DIAN, entidades bancarias, ARUS, SENA, ICBF y Caja de Compensación para trámites en línea.',
                        'peso': 6.25
                    }
                ]

                for item in preguntas_tecnicas:
                    pregunta = PreguntaEvaluacion.objects.create(
                        evaluacion=evaluacion,
                        pregunta=item['pregunta'],
                        descripcion=item.get('descripcion', ''),
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
