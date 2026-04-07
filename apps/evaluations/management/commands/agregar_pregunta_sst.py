"""
Comando para agregar la pregunta de Observación SST a todas las evaluaciones anuales que no la tengan
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.evaluations.models import (
    PreguntaEvaluacion,
    TipoPregunta,
    OpcionEvaluacion,
    EvaluacionDesempeño
)


class Command(BaseCommand):
    help = 'Agrega pregunta de Observación SST a evaluaciones anuales que no la tengan'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Agregando pregunta SST a evaluaciones anuales...'))
        self.stdout.write('')

        try:
            with transaction.atomic():
                # Obtener tipo de pregunta ESCALA_5
                tipo_pregunta_escala5 = TipoPregunta.objects.get(codigo='ESCALA_5')

                # Obtener todas las evaluaciones anuales activas (buscar por tipo_evaluacion)
                evaluaciones_anuales = EvaluacionDesempeño.objects.filter(
                    activa=True,
                    tipo_evaluacion__codigo__contains='ANUAL'
                )

                evaluaciones_procesadas = 0
                evaluaciones_ya_tenian = 0

                for evaluacion in evaluaciones_anuales:
                    # Verificar si ya tiene la pregunta SST
                    tiene_sst = PreguntaEvaluacion.objects.filter(
                        evaluacion=evaluacion,
                        categoria='Observación SST'
                    ).exists()

                    if tiene_sst:
                        self.stdout.write(f'  [OK] {evaluacion.nombre}: Ya tiene pregunta SST')
                        evaluaciones_ya_tenian += 1
                        continue

                    # Obtener el siguiente número de orden
                    ultima_pregunta = PreguntaEvaluacion.objects.filter(
                        evaluacion=evaluacion
                    ).order_by('-orden').first()

                    siguiente_orden = (ultima_pregunta.orden + 1) if ultima_pregunta else 1

                    # Crear pregunta SST
                    pregunta_sst = PreguntaEvaluacion.objects.create(
                        evaluacion=evaluacion,
                        pregunta='¿El empleado utiliza adecuadamente los Elementos de Protección Personal (EPP) y promueve su uso?',
                        descripcion='Observación sobre el cumplimiento de normas de seguridad y uso de EPP. Esta pregunta no afecta la calificación de desempeño.',
                        tipo_pregunta=tipo_pregunta_escala5,
                        categoria='Observación SST',
                        orden=siguiente_orden,
                        peso_porcentual=0,  # No afecta el puntaje
                        obligatoria=True
                    )

                    # Crear 3 opciones específicas para SST
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

                    self.stdout.write(self.style.SUCCESS(
                        f'  [+] {evaluacion.nombre}: Pregunta SST agregada (orden {siguiente_orden})'
                    ))
                    evaluaciones_procesadas += 1

                # Resumen
                self.stdout.write('')
                self.stdout.write('=' * 80)
                self.stdout.write(self.style.SUCCESS('[OK] PROCESO COMPLETADO'))
                self.stdout.write('=' * 80)
                self.stdout.write(f'Evaluaciones procesadas: {evaluaciones_procesadas}')
                self.stdout.write(f'Evaluaciones que ya tenian SST: {evaluaciones_ya_tenian}')
                self.stdout.write(f'Total de evaluaciones: {evaluaciones_anuales.count()}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Error: {str(e)}'))
            raise
