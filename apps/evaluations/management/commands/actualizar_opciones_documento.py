from django.core.management.base import BaseCommand
from apps.evaluations.models import OpcionEvaluacion, PreguntaEvaluacion


class Command(BaseCommand):
    help = 'Actualiza las opciones de evaluación con el contenido del documento'

    def handle(self, *args, **options):
        # Datos del documento completo
        respuestas_documento = {
            'Trabajo en equipo': {
                1: {'observacion': 'Se presentan dificultades para integrarse plenamente con el equipo. En algunas ocasiones surgen desacuerdos debido a la falta de escucha activa o a una disposición limitada para colaborar.', 'recomendacion': 'Fortalecer la comunicación y la participación dentro del equipo, solicitando apoyo cuando sea necesario y brindándolo igualmente. Involucrarse de manera más activa en actividades grupales contribuirá a un mejor clima laboral.', 'ejemplo': 'Iniciar ofreciendo apoyo en tareas sencillas para generar confianza y mejorar la relación con los compañeros'},
                2: {'observacion': 'Participa en el trabajo en equipo, aunque a veces resulta difícil mantener una actitud conciliadora o abierta frente a diferentes puntos de vista.', 'recomendacion': 'Trabajar en una actitud más constante y equilibrada, especialmente en situaciones de presión, fomentando el diálogo y el respeto mutuo.', 'ejemplo': 'Antes de responder en una discusión laboral, tomar un momento para escuchar plenamente la opinión del compañero y reflexionar antes de intervenir.'},
                3: {'observacion': 'Se integra adecuadamente al equipo, respeta las diferencias y contribuye a un ambiente armonioso.', 'recomendacion': 'Mantener esta actitud colaborativa y continuar siendo un referente positivo y un apoyo para los compañeros.', 'ejemplo': 'Mantener esta actitud colaborativa'}
            },
            'Compromiso': {
                1: {'observacion': 'Actualmente no se evidencia disposición para asumir tareas adicionales ni un compromiso claro con los objetivos del área.', 'recomendacion': 'Desarrollar mayor iniciativa y asumir responsabilidades acordes al cargo. Es importante actuar de manera proactiva, sin esperar instrucciones para realizar tareas necesarias.', 'ejemplo': 'Puede empezar completando tareas sin necesidad de recordatorios constantes.'},
                2: {'observacion': 'Muestra compromiso en algunas ocasiones, pero este no es constante y requiere acompañamiento para asumir determinadas actividades.', 'recomendacion': 'Fortalecer la constancia y demostrar mayor autonomía en las labores diarias. Atender con diligencia aquellas tareas no contempladas explícitamente en las funciones, pero que surgen de manera cotidiana y son importantes para garantizar la calidad del trabajo.', 'ejemplo': 'Identificar tareas pendientes y gestionarlas de manera autónoma, sin esperar instrucciones directas.'},
                3: {'observacion': 'Demuestra compromiso constante, disposición al esfuerzo adicional y autonomía para asumir actividades que aportan al logro de objetivos.', 'recomendacion': 'Continuar manteniendo esta actitud proactiva, siendo referente de compromiso para el equipo.', 'ejemplo': 'Continuar manteniendo esta actitud proactiva'}
            },
            'Comunicación': {
                1: {'observacion': 'La información que proporciona no siempre es clara o precisa, y en algunas ocasiones interrumpe o no escucha activamente a los demás', 'recomendacion': 'Fortalecer la capacidad de escuchar y comunicar de manera clara y oportuna, asegurando que la información requerida llegue correctamente a los demás para alcanzar los objetivos del equipo.', 'ejemplo': 'Antes de actuar, repetir brevemente lo entendido para confirmar la información y evitar errores'},
                2: {'observacion': 'Se comunica adecuadamente en la mayoría de las situaciones, aunque en ocasiones surgen malentendidos por falta de claridad o retroalimentación.', 'recomendacion': 'Promover un intercambio de información constante y efectivo, asegurando que todos los miembros del equipo estén correctamente informados', 'ejemplo': 'Organizar las ideas antes de explicar un proceso o procedimiento.'},
                3: {'observacion': 'Se comunica de forma clara, escucha activamente y facilita la resolución de acuerdos.', 'recomendacion': 'Mantener y fortalecer esta habilidad, continuando como un referente de comunicación efectiva.', 'ejemplo': 'Mantener esta habilidad de comunicación'}
            },
            'Atención al detalle': {
                1: {'observacion': 'Se han identificado oportunidades de mejora en la revisión de tareas, ya que en ocasiones algunos detalles pasan inadvertidos y pueden influir en la calidad final del trabajo.', 'recomendacion': 'Se sugiere revisar cuidadosamente el trabajo antes de su entrega y apoyarse en herramientas como listas de verificación o recordatorios para asegurar que no se omitan aspectos relevantes.', 'ejemplo': 'Tomar 2 minutos para revisar documentos antes de enviarlos o contar con una lista de verificación.'},
                2: {'observacion': 'Suele mostrar una buena atención en sus tareas; sin embargo, en algunas ocasiones ciertos detalles pueden pasar desapercibidos.', 'recomendacion': 'Se sugiere fortalecer la concentración, especialmente en tareas críticas, para asegurar que todos los elementos relevantes sean considerados.', 'ejemplo': 'Subrayar o marcar los puntos importantes de cada actividad antes de ejecutarla.'},
                3: {'observacion': 'Tiene una actitud constante de observación y cuidado del detalle.', 'recomendacion': 'Se recomienda mantener este buen nivel de precisión en sus tareas.', 'ejemplo': 'Mantener este nivel de precisión'}
            },
            'Cumplimiento de las normas y procedimientos': {
                1: {'observacion': 'Actualmente tiene dificultades para seguir los procedimientos establecidos y requiere recordatorios frecuentes para completar las tareas de acuerdo con los protocolos.', 'recomendacion': 'Se sugiere revisar nuevamente los protocolos del área y practicarlos de forma constante para lograr una aplicación más segura y uniforme', 'ejemplo': 'Revisar el manual del área antes de realizar procedimientos clave.'},
                2: {'observacion': 'En general sigue las normas y procedimientos; sin embargo, se han presentado algunas inconsistencias puntuales. Mejorar la consistencia en la ejecución contribuirá a resultados más confiables.', 'recomendacion': 'Se recomienda reforzar la disciplina en el cumplimiento de procesos para mantener un desempeño estable y sin omisiones.', 'ejemplo': 'Crear un paso a paso personal para evitar saltarse etapas.'},
                3: {'observacion': 'Cumple de forma eficiente todas las normas y procedimientos establecidos.', 'recomendacion': 'Continuar siendo referente de cumplimiento y orden.', 'ejemplo': 'Continuar con este nivel de cumplimiento'}
            },
            'Actitud respecto al trabajo': {
                1: {'observacion': 'En algunas tareas se ha notado poca disposición o actitudes que pueden afectar el desarrollo del trabajo.', 'recomendacion': 'Fomentar una actitud más abierta y receptiva que permita aprovechar mejor las oportunidades de aprendizaje y colaboración.', 'ejemplo': 'Antes de rechazar una tarea, consultar sobre su propósito o impacto para comprender mejor su importancia.'},
                2: {'observacion': 'Generalmente muestra buena actitud, pero en situaciones de presión se ve afectada su disposición.', 'recomendacion': 'Fortalecer su manejo emocional en situaciones de alta demanda para mantener la estabilidad y el enfoque.', 'ejemplo': 'Aplicar técnicas breves de respiración o pausas conscientes cuando surja el estrés.'},
                3: {'observacion': 'Mantiene una actitud positiva, colaborativa y dispuesta.', 'recomendacion': 'seguir impulsando esta actitud, ya que genera un ambiente laboral favorable y motiva al equipo.', 'ejemplo': 'Continuar con esta actitud positiva'}
            },
            'Calidad': {
                1: {'observacion': 'Se han identificado errores recurrentes en las tareas o falta de una revisión final antes de entregarlas.', 'recomendacion': 'Fortalecer el control de calidad para asegurar resultados más precisos y completos.', 'ejemplo': 'Antes de finalizar, revisar tres aspectos clave: formato, exactitud de la información y coherencia del contenido.'},
                2: {'observacion': 'La calidad del trabajo suele ser buena, aunque ocasionalmente se presentan fallas por descuidos puntuales.', 'recomendacion': 'Incrementar la atención en actividades repetitivas o que requieren mayor detalle para evitar errores menores.', 'ejemplo': 'Solicitar retroalimentación sobre las entregas para identificar oportunidades de mejora continua.'},
                3: {'observacion': 'Entregas de excelente calidad, sin errores y con evidente cuidado.', 'recomendacion': 'Mantener este nivel de dedicación y precisión en todas las tareas asignadas, ya que aporta significativamente a la calidad del trabajo del equipo.', 'ejemplo': 'Mantener este nivel de calidad'}
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
