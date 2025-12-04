from django.core.management.base import BaseCommand
from apps.evaluations.models import OpcionEvaluacion, PreguntaEvaluacion


class Command(BaseCommand):
    help = 'Actualiza las opciones de evaluación con el contenido del documento'

    def handle(self, *args, **options):
        # Datos del documento
        respuestas_documento = {
            'Trabajo en equipo': {
                1: {
                    'observacion': 'Se presentan dificultades para integrarse plenamente con el equipo. En algunas ocasiones surgen desacuerdos debido a la falta de escucha activa o a una disposición limitada para colaborar.',
                    'recomendacion': 'Fortalecer la comunicación y la participación dentro del equipo, solicitando apoyo cuando sea necesario y brindándolo igualmente. Involucrarse de manera más activa en actividades grupales contribuirá a un mejor clima laboral.',
                    'ejemplo': 'Iniciar ofreciendo apoyo en tareas sencillas para generar confianza y mejorar la relación con los compañeros'
                },
                2: {
                    'observacion': 'Participa en el trabajo en equipo, aunque a veces resulta difícil mantener una actitud conciliadora o abierta frente a diferentes puntos de vista.',
                    'recomendacion': 'Trabajar en una actitud más constante y equilibrada, especialmente en situaciones de presión, fomentando el diálogo y el respeto mutuo.',
                    'ejemplo': 'Antes de responder en una discusión laboral, tomar un momento para escuchar plenamente la opinión del compañero y reflexionar antes de intervenir.'
                },
                3: {
                    'observacion': 'Se integra adecuadamente al equipo, respeta las diferencias y contribuye a un ambiente armonioso.',
                    'recomendacion': 'Mantener esta actitud colaborativa y continuar siendo un referente positivo y un apoyo para los compañeros.',
                    'ejemplo': 'Mantener esta actitud colaborativa'
                }
            }
        }

        etiquetas = {1: 'No cumple', 2: 'Cumple parcialmente', 3: 'Cumple totalmente'}
        valores = {1: 1.0, 2: 2.0, 3: 3.0}

        actualizadas = 0
        for pregunta_nombre, respuestas_por_calificacion in respuestas_documento.items():
            pregunta = PreguntaEvaluacion.objects.filter(pregunta__contains=pregunta_nombre).first()

            if pregunta:
                for calificacion, datos in respuestas_por_calificacion.items():
                    # Crear texto completo
                    texto = f"{etiquetas[calificacion]}\n\nObservación:\n{datos['observacion']}\n\nRecomendación:\n{datos['recomendacion']}\n\nEjemplo:\n{datos['ejemplo']}"

                    # Actualizar opción
                    opcion = OpcionEvaluacion.objects.filter(
                        pregunta=pregunta,
                        valor_numerico=valores[calificacion]
                    ).first()

                    if opcion:
                        opcion.opcion = texto
                        opcion.save()
                        self.stdout.write(f'✓ Actualizada: {pregunta_nombre} - Calificación {calificacion}')
                        actualizadas += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Total actualizadas: {actualizadas}'))
