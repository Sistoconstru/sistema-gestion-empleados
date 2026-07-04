"""Recalcula `puntaje_final` y `fecha_finalizacion` en inscripciones aprobadas
con esos campos vacíos.

Pasaba por versiones viejas del flujo que cambiaban a estado='aprobado' sin
guardar el promedio. Esto deja el campo None, lo que en la UI mostraba la
alerta engañosa "Debes completar todas las valoraciones de aprendizaje" en
inscripciones ya aprobadas.

Por defecto es dry-run; pasar --apply para escribir.
"""
from django.core.management.base import BaseCommand
from django.db.models import Max
from django.utils import timezone

from apps.training.models import InscripcionCapacitacion, IntentoQuiz, QuizLeccion


class Command(BaseCommand):
    help = 'Recalcula puntaje_final y fecha_finalizacion en inscripciones aprobadas que los tengan vacíos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Aplica los cambios. Sin esta bandera solo muestra lo que haría.',
        )

    def handle(self, *args, **options):
        aplicar = options['apply']
        modo = 'APLICAR' if aplicar else 'DRY-RUN'
        self.stdout.write(self.style.WARNING(f'Modo: {modo}'))

        candidatas = InscripcionCapacitacion.objects.filter(
            estado='aprobado'
        ).filter(puntaje_final__isnull=True) | InscripcionCapacitacion.objects.filter(
            estado='aprobado', fecha_finalizacion__isnull=True
        )
        candidatas = candidatas.distinct().select_related('empleado', 'capacitacion')

        if not candidatas.exists():
            self.stdout.write(self.style.SUCCESS('Nada que recalcular.'))
            return

        actualizadas = 0
        sin_datos = 0
        for insc in candidatas:
            quizzes_ids = list(QuizLeccion.objects.filter(
                leccion__modulo__capacitacion=insc.capacitacion,
                leccion__modulo__activo=True,
                leccion__activa=True,
            ).values_list('id', flat=True))

            if not insc.empleado.usuario_id or not quizzes_ids:
                sin_datos += 1
                self.stdout.write(
                    f'  - {insc.empleado.nombre_completo} / {insc.capacitacion.codigo}: '
                    f'sin usuario o sin quizzes activos, no se puede recalcular'
                )
                continue

            # Tomar el MEJOR puntaje aprobado por cada quiz, luego promediar.
            mejores_por_quiz = list(IntentoQuiz.objects.filter(
                quiz_id__in=quizzes_ids,
                usuario_id=insc.empleado.usuario_id,
                aprobado=True,
            ).values('quiz_id').annotate(mejor=Max('puntaje_obtenido')))

            if not mejores_por_quiz:
                sin_datos += 1
                self.stdout.write(
                    f'  - {insc.empleado.nombre_completo} / {insc.capacitacion.codigo}: '
                    f'no hay intentos aprobados — no se puede calcular promedio'
                )
                continue

            promedio = round(
                sum([float(r['mejor']) for r in mejores_por_quiz]) / len(mejores_por_quiz),
                2,
            )
            update_fields = []
            if insc.puntaje_final is None:
                insc.puntaje_final = promedio
                update_fields.append('puntaje_final')
            if insc.fecha_finalizacion is None:
                # Usar la fecha del último intento aprobado como aproximación
                ultimo = IntentoQuiz.objects.filter(
                    quiz_id__in=quizzes_ids,
                    usuario_id=insc.empleado.usuario_id,
                    aprobado=True,
                ).order_by('-fecha_inicio').first()
                insc.fecha_finalizacion = ultimo.fecha_inicio if ultimo else timezone.now()
                update_fields.append('fecha_finalizacion')

            self.stdout.write(
                f'  + {insc.empleado.nombre_completo} / {insc.capacitacion.codigo}: '
                f'puntaje_final={promedio} ({len(mejores_por_quiz)} quiz(zes)), '
                f'fecha_fin={insc.fecha_finalizacion.strftime("%Y-%m-%d") if insc.fecha_finalizacion else "—"}'
            )
            if aplicar:
                insc.save(update_fields=update_fields)
            actualizadas += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'{actualizadas} inscripción(es) {"actualizada(s)" if aplicar else "se actualizarían"}.'
        ))
        if sin_datos:
            self.stdout.write(self.style.WARNING(
                f'{sin_datos} inscripción(es) sin datos suficientes para recalcular.'
            ))
        if not aplicar:
            self.stdout.write(self.style.WARNING('DRY-RUN: no se escribió nada. Usa --apply para aplicar.'))
