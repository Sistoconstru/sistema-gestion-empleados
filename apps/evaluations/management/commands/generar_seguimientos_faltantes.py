"""
Comando para generar seguimientos bimensuales faltantes en planes de mejora aprobados
que tienen al menos una competencia con calificación ≤ 4
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import PlanMejoraPredefinido, RespuestaEvaluacion, SeguimientoBimensual
from apps.evaluations.utils.respuestas_predefinidas import crear_seguimientos_bimensuales


class Command(BaseCommand):
    help = 'Genera seguimientos bimensuales para planes que los requieren pero no los tienen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ejecutar',
            action='store_true',
            help='Ejecutar la creación de seguimientos (sin este flag solo muestra reporte)',
        )

    def handle(self, *args, **options):
        ejecutar = options['ejecutar']

        self.stdout.write(self.style.WARNING('Analizando planes de mejora aprobados...'))

        # Obtener todos los planes aprobados o en seguimiento
        planes = PlanMejoraPredefinido.objects.filter(
            estado__in=['aprobado', 'en_seguimiento', 'completado']
        ).select_related('asignacion_evaluacion', 'asignacion_evaluacion__empleado_evaluado')

        self.stdout.write(f'Total de planes aprobados/en_seguimiento/completados: {planes.count()}')

        planes_sin_seguimiento = []
        planes_con_seguimiento = []

        for plan in planes:
            # Verificar si ya tiene seguimientos
            seguimientos_count = SeguimientoBimensual.objects.filter(plan_mejora=plan).count()

            # Obtener respuestas de la evaluación
            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion=plan.asignacion_evaluacion
            ).select_related('opcion_seleccionada')

            # Verificar si tiene al menos una respuesta con valor ≤ 4
            tiene_calificacion_baja = respuestas.filter(
                opcion_seleccionada__valor_numerico__lte=4
            ).exists()

            preguntas_con_mejora = respuestas.filter(
                opcion_seleccionada__valor_numerico__lte=4
            ).count()

            if tiene_calificacion_baja and seguimientos_count == 0:
                planes_sin_seguimiento.append({
                    'plan': plan,
                    'empleado': plan.asignacion_evaluacion.empleado_evaluado.nombre_completo,
                    'tipo_eval': plan.asignacion_evaluacion.evaluacion.tipo_evaluacion.codigo,
                    'puntaje': plan.asignacion_evaluacion.puntaje_total,
                    'preguntas_mejora': preguntas_con_mejora
                })
            elif tiene_calificacion_baja and seguimientos_count > 0:
                planes_con_seguimiento.append({
                    'empleado': plan.asignacion_evaluacion.empleado_evaluado.nombre_completo,
                    'seguimientos': seguimientos_count,
                    'preguntas_mejora': preguntas_con_mejora
                })

        # Reporte
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('REPORTE DE SEGUIMIENTOS'))
        self.stdout.write('='*80)
        self.stdout.write(f'Planes que YA tienen seguimientos: {len(planes_con_seguimiento)}')
        self.stdout.write(f'Planes que NECESITAN seguimientos: {len(planes_sin_seguimiento)}')

        if planes_sin_seguimiento:
            self.stdout.write('\n' + '-'*80)
            self.stdout.write(self.style.WARNING('PLANES SIN SEGUIMIENTOS (requieren creación):'))
            self.stdout.write('-'*80)
            for idx, info in enumerate(planes_sin_seguimiento, 1):
                self.stdout.write(
                    f"{idx}. {info['empleado']} - {info['tipo_eval']} - "
                    f"Puntaje: {info['puntaje']} - "
                    f"Competencias con mejora: {info['preguntas_mejora']}"
                )

        # Ejecutar creación de seguimientos si se especificó el flag
        if ejecutar and planes_sin_seguimiento:
            self.stdout.write('\n' + '='*80)
            self.stdout.write(self.style.WARNING('CREANDO SEGUIMIENTOS BIMENSUALES...'))
            self.stdout.write('='*80)

            creados = 0
            for info in planes_sin_seguimiento:
                plan = info['plan']
                try:
                    crear_seguimientos_bimensuales(plan)

                    # Cambiar estado del plan a 'en_seguimiento' si estaba en 'aprobado'
                    if plan.estado == 'aprobado':
                        plan.estado = 'en_seguimiento'
                        plan.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[OK] Seguimientos creados para: {info['empleado']} "
                            f"({info['preguntas_mejora']} competencias con mejora)"
                        )
                    )
                    creados += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[ERROR] Error al crear seguimientos para {info['empleado']}: {e}"
                        )
                    )

            self.stdout.write('\n' + '='*80)
            self.stdout.write(
                self.style.SUCCESS(
                    f'COMPLETADO: Se crearon seguimientos para {creados} plan(es) de mejora'
                )
            )
            self.stdout.write('='*80)

        elif not ejecutar and planes_sin_seguimiento:
            self.stdout.write('\n' + '='*80)
            self.stdout.write(
                self.style.WARNING(
                    'Para crear los seguimientos, ejecute:\n'
                    'python manage.py generar_seguimientos_faltantes --ejecutar'
                )
            )
            self.stdout.write('='*80)
        else:
            self.stdout.write('\n' + '='*80)
            self.stdout.write(self.style.SUCCESS('No hay seguimientos pendientes de crear.'))
            self.stdout.write('='*80)
