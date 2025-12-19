from django.core.management.base import BaseCommand
from apps.training.models import InscripcionCapacitacion, IntentoQuiz
from django.db.models import Q


class Command(BaseCommand):
    help = 'Corrige los estados de las inscripciones que fueron marcadas como aprobadas sin completar todas las valoraciones'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando corrección de estados...'))

        # Obtener todas las inscripciones (en progreso, aprobadas y completadas)
        inscripciones = InscripcionCapacitacion.objects.filter(
            Q(estado='aprobado') | Q(estado='completado') | Q(estado='en_progreso')
        ).select_related('capacitacion', 'empleado__usuario').prefetch_related(
            'capacitacion__modulocapacitacion_set__leccion_set__contenidos'
        )

        corregidas = 0
        total = inscripciones.count()

        self.stdout.write(f'Analizando {total} inscripciones...')

        for insc in inscripciones:
            # Obtener todos los quizzes de la capacitación
            quizzes_ids = []
            for modulo in insc.capacitacion.modulocapacitacion_set.all():
                for leccion in modulo.leccion_set.all():
                    # Quizzes de los contenidos de la lección
                    for contenido in leccion.contenidoleccion_set.all():
                        if hasattr(contenido, 'evaluacion') and contenido.evaluacion:
                            quizzes_ids.append(contenido.evaluacion.id)
                    # Quiz directo de la lección
                    if hasattr(leccion, 'evaluacion') and leccion.evaluacion:
                        quizzes_ids.append(leccion.evaluacion.id)

            # Si no hay quizzes, está bien que esté aprobado
            if not quizzes_ids:
                continue

            # Verificar cuántos quizzes aprobó el empleado
            intentos_aprobados = IntentoQuiz.objects.filter(
                quiz_id__in=quizzes_ids,
                usuario=insc.empleado.usuario,
                aprobado=True
            ).count()

            # Si NO completó todas las valoraciones, cambiar a 'en_progreso'
            if intentos_aprobados < len(quizzes_ids):
                self.stdout.write(
                    self.style.WARNING(
                        f'Inscripción {insc.id}: {insc.empleado.nombre_completo} - {insc.capacitacion.nombre}'
                    )
                )
                self.stdout.write(
                    f'  Valoraciones: {intentos_aprobados}/{len(quizzes_ids)} completadas'
                )
                self.stdout.write(
                    f'  Cambiando estado de "{insc.estado}" a "en_progreso"'
                )

                insc.estado = 'en_progreso'
                insc.puntaje_final = None  # Limpiar puntaje hasta que complete todas
                insc.save()
                corregidas += 1
            elif intentos_aprobados == len(quizzes_ids):
                # Si completó todas las evaluaciones, calcular promedio y verificar si aprueba
                puntajes = IntentoQuiz.objects.filter(
                    quiz_id__in=quizzes_ids,
                    usuario=insc.empleado.usuario,
                    aprobado=True
                ).values_list('puntaje_obtenido', flat=True)

                if puntajes:
                    promedio = round(sum(puntajes) / len(puntajes), 2)
                    estado_correcto = 'aprobado' if promedio >= insc.capacitacion.puntaje_aprobacion else 'en_progreso'

                    # Actualizar puntaje final y estado si cambió
                    if insc.puntaje_final != promedio or insc.estado != estado_correcto:
                        insc.puntaje_final = promedio
                        insc.estado = estado_correcto
                        if estado_correcto == 'aprobado':
                            from django.utils import timezone
                            if not insc.fecha_finalizacion:
                                insc.fecha_finalizacion = timezone.now()
                        insc.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Inscripción {insc.id}: Puntaje {promedio} - Estado: {estado_correcto}'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado: {corregidas} inscripciones corregidas de {total} analizadas'
            )
        )
