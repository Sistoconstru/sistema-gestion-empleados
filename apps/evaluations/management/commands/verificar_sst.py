from django.core.management.base import BaseCommand
from apps.evaluations.models import EvaluacionDesempeño, PreguntaEvaluacion


class Command(BaseCommand):
    help = 'Verifica qué evaluaciones tienen pregunta SST'

    def handle(self, *args, **options):
        self.stdout.write('=== EVALUACIONES Y PREGUNTA SST ===\n')

        evals = EvaluacionDesempeño.objects.filter(activa=True).order_by('nombre')

        for ev in evals:
            tiene_sst = PreguntaEvaluacion.objects.filter(
                evaluacion=ev,
                categoria='Observación SST'
            ).exists()

            count_preguntas = PreguntaEvaluacion.objects.filter(evaluacion=ev).count()

            if tiene_sst:
                self.stdout.write(self.style.SUCCESS(f'[OK]  {ev.tipo_evaluacion.codigo:30} | {ev.nombre:55} | Total: {count_preguntas}'))
            else:
                self.stdout.write(self.style.ERROR(f'[NO]  {ev.tipo_evaluacion.codigo:30} | {ev.nombre:55} | Total: {count_preguntas}'))

        self.stdout.write('\n=== RESUMEN ===')
        total = evals.count()
        con_sst = sum(1 for ev in evals if PreguntaEvaluacion.objects.filter(evaluacion=ev, categoria='Observación SST').exists())
        sin_sst = total - con_sst

        self.stdout.write(f'Total evaluaciones activas: {total}')
        self.stdout.write(self.style.SUCCESS(f'Con pregunta SST: {con_sst}'))
        self.stdout.write(self.style.ERROR(f'Sin pregunta SST: {sin_sst}'))

        if sin_sst > 0:
            self.stdout.write('\n=== EVALUACIONES SIN SST ===')
            for ev in evals:
                tiene_sst = PreguntaEvaluacion.objects.filter(evaluacion=ev, categoria='Observación SST').exists()
                if not tiene_sst:
                    self.stdout.write(self.style.WARNING(f'  - {ev.tipo_evaluacion.codigo}: {ev.nombre}'))
