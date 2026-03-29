"""
Comando para configurar la evaluación anual de Auxiliar de Tesorería con sistema ponderado
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
    help = 'Configura la evaluación anual para Auxiliar de Tesorería (escala 1-5 ponderada)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando evaluacion anual para Auxiliar de Tesorería...'))

        try:
            with transaction.atomic():
                # Obtener usuario del sistema
                usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
                if not usuario_sistema:
                    self.stdout.write(self.style.ERROR('No hay usuarios superusuarios en el sistema'))
                    return

                # 1. Obtener o crear tipo de evaluación
                tipo_eval, created = TipoEvaluacion.objects.get_or_create(
                    codigo='ANUAL_AUX_TESORERIA',
                    defaults={
                        'nombre': 'Evaluación Anual - Auxiliar de Tesorería',
                        'descripcion': 'Evaluación anual de desempeño para auxiliar de tesorería con sistema ponderado',
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
                    codigo='EVAL_ANUAL_AUX_TESORERIA_2025',
                    defaults={
                        'tipo_evaluacion': tipo_eval,
                        'nombre': 'Evaluacion Anual Auxiliar de Tesoreria 2025',
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
                            ('Ejecutar procesos de recaudo, pagos, consignaciones y conciliaciones bancarias', 'Ejecutar los procesos de recaudo, pagos, consignaciones y conciliaciones bancarias de la empresa, garantizando el registro oportuno y exacto de los movimientos de caja y bancos, el cumplimiento de obligaciones de pago en las fechas establecidas y la custodia adecuada de los recursos financieros.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Interpersonales',
                        'ponderacion': 25,
                        'preguntas': [
                            ('Compromiso y responsabilidad', 'Cumplir a cabalidad con los compromisos adquiridos, actuando con integridad en el manejo de recursos económicos. → Comportamiento esperado: Realiza consignaciones, pagos y cierres de caja en los horarios y fechas establecidos sin necesidad de recordatorios.'),
                            ('Atención al detalle', 'Habilidad para revisar y procesar información financiera y bancaria con exactitud, detectando errores antes de que se materialicen. → Comportamiento esperado: Verifica que cada comprobante de pago coincida con el soporte, la orden y el valor autorizado antes de ejecutar la transacción.'),
                            ('Orientación al cliente interno', 'Actitud proactiva para atender con eficiencia las solicitudes de pago, reembolsos y consultas del personal interno. → Comportamiento esperado: Responde oportunamente las solicitudes de pagos a proveedores y anticipa las fechas de vencimiento para no generar mora.')
                        ]
                    },
                    {
                        'nombre': 'Competencias Técnicas',
                        'ponderacion': 25,
                        'preguntas': [
                            ('Manejo de plataformas bancarias', 'Operación de portales bancarios en línea para pagos, transferencias, consultas de saldo y descarga de extractos (ARUS, COMFAMA, PSE, bancos).'),
                            ('Conciliaciones bancarias', 'Capacidad para cruzar movimientos del extracto bancario con los registros contables e identificar y resolver diferencias.'),
                            ('Manejo del software contable', 'Registro de ingresos, egresos, causaciones de pagos y recibos de caja en el sistema de información contable de la empresa.'),
                            ('Manejo básico de Office / Excel', 'Uso de Excel para elaborar flujos de caja, control de pagos pendientes, conciliaciones y reportes de movimientos diarios.'),
                            ('Control y custodia de caja menor', 'Procedimientos para apertura, manejo, arqueo y legalización de caja menor conforme a la política interna de la empresa.')
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
