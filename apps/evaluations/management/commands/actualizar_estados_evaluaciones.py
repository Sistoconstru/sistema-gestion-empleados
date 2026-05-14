"""
Comando para actualizar estados de evaluaciones existentes después de implementar
los nuevos estados 'requiere_correccion' y 'finalizada'.

Este comando debe ejecutarse UNA VEZ después del deploy para actualizar:
1. Evaluaciones completadas con plan completado y evaluación final aceptada → 'finalizada'
2. Evaluaciones completadas y desaprobadas → 'requiere_correccion' (ya lo hace la migración 0014)

Uso:
    python manage.py actualizar_estados_evaluaciones
    python manage.py actualizar_estados_evaluaciones --dry-run  # Solo mostrar qué se haría
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import AsignacionEvaluacion, PlanMejoraPredefinido, EvaluacionFinal


class Command(BaseCommand):
    help = 'Actualiza estados de evaluaciones existentes a los nuevos estados (finalizada, requiere_correccion)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se actualizaría sin hacer cambios reales',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] No se harán cambios reales\n'))

        self.stdout.write('='*70)
        self.stdout.write(self.style.WARNING('ACTUALIZANDO ESTADOS DE EVALUACIONES'))
        self.stdout.write('='*70)

        # ========== 1. ACTUALIZAR EVALUACIONES FINALIZADAS ==========
        self.stdout.write('\n[1] Buscando evaluaciones que completaron todo el proceso...')

        evaluaciones_completadas = AsignacionEvaluacion.objects.filter(
            estado='completada'
        ).select_related('empleado_evaluado')

        self.stdout.write(f'    Evaluaciones completadas encontradas: {evaluaciones_completadas.count()}')

        # Contadores de diagnóstico
        sin_plan = 0
        plan_no_completado = 0
        sin_eval_final = 0
        eval_final_no_aceptada = 0

        actualizadas_finalizadas = 0

        for evaluacion in evaluaciones_completadas:
            try:
                # Verificar si tiene plan de mejora completado
                plan = PlanMejoraPredefinido.objects.get(asignacion_evaluacion=evaluacion)

                if plan.estado == 'completado':
                    try:
                        # Verificar si tiene evaluación final aceptada o validada
                        eval_final = EvaluacionFinal.objects.get(plan_mejora=plan)

                        if eval_final.aceptado_por_empleado or eval_final.validado_por_rrhh:
                            # TODO el proceso está completo → FINALIZADA
                            self.stdout.write(
                                f'    -> {evaluacion.empleado_evaluado.nombre_completo}: '
                                f'completada -> finalizada'
                            )

                            if not dry_run:
                                evaluacion.estado = 'finalizada'
                                evaluacion.save()

                            actualizadas_finalizadas += 1
                        else:
                            eval_final_no_aceptada += 1
                    except EvaluacionFinal.DoesNotExist:
                        sin_eval_final += 1
                else:
                    plan_no_completado += 1
            except PlanMejoraPredefinido.DoesNotExist:
                sin_plan += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] Evaluaciones actualizadas a FINALIZADA: {actualizadas_finalizadas}'
            )
        )

        # Mostrar diagnóstico de por qué no se actualizaron
        if actualizadas_finalizadas == 0 and evaluaciones_completadas.count() > 0:
            self.stdout.write('\n    Diagnostico (por que no se actualizaron):')
            if sin_plan > 0:
                self.stdout.write(f'      - Sin plan de mejora: {sin_plan}')
            if plan_no_completado > 0:
                self.stdout.write(f'      - Plan no completado: {plan_no_completado}')
            if sin_eval_final > 0:
                self.stdout.write(f'      - Sin evaluacion final: {sin_eval_final}')
            if eval_final_no_aceptada > 0:
                self.stdout.write(f'      - Eval final no aceptada/validada: {eval_final_no_aceptada}')

        # ========== 2. ACTUALIZAR EVALUACIONES DESAPROBADAS ==========
        # Nota: Esto ya lo hace la migración 0014, pero lo verificamos por si acaso
        self.stdout.write('\n[2] Verificando evaluaciones desaprobadas...')

        # Primero verificar TODAS las evaluaciones desaprobadas (cualquier estado)
        todas_desaprobadas = AsignacionEvaluacion.objects.filter(
            estado_aprobacion='desaprobada'
        ).select_related('empleado_evaluado')

        if todas_desaprobadas.count() > 0:
            self.stdout.write(f'    Total con estado_aprobacion=desaprobada: {todas_desaprobadas.count()}')
            for ev in todas_desaprobadas[:5]:
                self.stdout.write(
                    f'      - {ev.empleado_evaluado.nombre_completo}: '
                    f'estado={ev.estado}, aprobacion={ev.estado_aprobacion}'
                )

        # Buscar solo las que están en 'completada' Y desaprobadas (para actualizar)
        evaluaciones_desaprobadas = AsignacionEvaluacion.objects.filter(
            estado='completada',
            estado_aprobacion='desaprobada'
        )

        count_desaprobadas = evaluaciones_desaprobadas.count()

        if count_desaprobadas > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'    [!] Encontradas {count_desaprobadas} evaluaciones desaprobadas que no se actualizaron'
                )
            )

            actualizadas_desaprobadas = 0
            for evaluacion in evaluaciones_desaprobadas:
                self.stdout.write(
                    f'    -> {evaluacion.empleado_evaluado.nombre_completo}: '
                    f'completada -> requiere_correccion'
                )

                if not dry_run:
                    evaluacion.estado = 'requiere_correccion'
                    evaluacion.save()

                actualizadas_desaprobadas += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[OK] Evaluaciones actualizadas a REQUIERE_CORRECCION: {actualizadas_desaprobadas}'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('    [OK] No hay evaluaciones desaprobadas pendientes'))

        # ========== 3. ACTUALIZAR EVALUACIONES CON PLANES RECHAZADOS ==========
        # Caso especial: Evaluaciones donde el plan fue rechazado por RRHH
        # pero la evaluación nunca fue marcada como desaprobada
        self.stdout.write('\n[3] Verificando evaluaciones con planes rechazados...')

        planes_rechazados = PlanMejoraPredefinido.objects.filter(
            estado='rechazado'
        ).select_related('asignacion_evaluacion', 'asignacion_evaluacion__empleado_evaluado', 'aprobado_por')

        evaluaciones_con_plan_rechazado = 0
        for plan in planes_rechazados:
            asignacion = plan.asignacion_evaluacion
            # Solo actualizar si la evaluación no está ya en requiere_correccion o desaprobada
            if asignacion.estado != 'requiere_correccion' and asignacion.estado_aprobacion != 'desaprobada':
                self.stdout.write(
                    f'    -> {asignacion.empleado_evaluado.nombres} {asignacion.empleado_evaluado.apellidos}: '
                    f'Plan rechazado pero evaluación en estado={asignacion.estado}, aprobacion={asignacion.estado_aprobacion or "NULL"}'
                )

                if not dry_run:
                    asignacion.estado = 'requiere_correccion'
                    asignacion.estado_aprobacion = 'desaprobada'
                    if plan.aprobado_por:
                        asignacion.aprobada_por = plan.aprobado_por
                    if not asignacion.comentarios_aprobacion:
                        asignacion.comentarios_aprobacion = plan.comentarios_aprobacion or 'Plan de mejora rechazado por RRHH'
                    asignacion.save()

                evaluaciones_con_plan_rechazado += 1

        if evaluaciones_con_plan_rechazado > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[OK] Evaluaciones actualizadas por plan rechazado: {evaluaciones_con_plan_rechazado}'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('    [OK] No hay evaluaciones con planes rechazados que requieran actualización'))

        # ========== RESUMEN ==========
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('RESUMEN'))
        self.stdout.write('='*70)
        self.stdout.write(f'  Actualizadas a FINALIZADA: {actualizadas_finalizadas}')
        self.stdout.write(f'  Actualizadas a REQUIERE_CORRECCION (desaprobadas directamente): {count_desaprobadas}')
        self.stdout.write(f'  Actualizadas a REQUIERE_CORRECCION (plan rechazado): {evaluaciones_con_plan_rechazado}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] No se realizaron cambios reales'))
        else:
            self.stdout.write(self.style.SUCCESS('\n[OK] Actualizacion completada exitosamente'))
