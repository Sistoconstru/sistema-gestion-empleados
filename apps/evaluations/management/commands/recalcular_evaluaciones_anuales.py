"""
Comando para recalcular el puntaje de evaluaciones anuales con la fórmula corregida
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.evaluations.models import AsignacionEvaluacion, RespuestaEvaluacion
from decimal import Decimal


class Command(BaseCommand):
    help = 'Recalcula el puntaje ponderado de evaluaciones anuales completadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empleado-id',
            type=int,
            help='Recalcular solo para un empleado específico',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar cambios sin guardarlos',
        )

    def handle(self, *args, **options):
        empleado_id = options.get('empleado_id')
        dry_run = options.get('dry_run', False)

        # Obtener evaluaciones anuales completadas
        evaluaciones = AsignacionEvaluacion.objects.filter(
            evaluacion__tipo_evaluacion__codigo__in=['ANUAL_AUX_PROCESOS', 'ANUAL_MANTENIMIENTO'],
            estado='completada'
        ).select_related('empleado_evaluado', 'evaluacion__tipo_evaluacion')

        if empleado_id:
            evaluaciones = evaluaciones.filter(empleado_evaluado_id=empleado_id)

        total = evaluaciones.count()
        self.stdout.write(f"\n{'=' * 80}")
        self.stdout.write(f"Evaluaciones anuales completadas encontradas: {total}")
        self.stdout.write(f"{'=' * 80}\n")

        if total == 0:
            self.stdout.write(self.style.WARNING('No se encontraron evaluaciones para recalcular'))
            return

        actualizadas = 0
        sin_cambios = 0

        with transaction.atomic():
            for asignacion in evaluaciones:
                respuestas = RespuestaEvaluacion.objects.filter(
                    asignacion=asignacion
                ).select_related('pregunta', 'opcion_seleccionada')

                if not respuestas.exists():
                    continue

                # Debug: Mostrar preguntas
                self.stdout.write(f"\n{'-' * 80}")
                self.stdout.write(f"Empleado: {asignacion.empleado_evaluado.nombre_completo}")
                self.stdout.write(f"\nPreguntas y categorías:")
                for r in respuestas:
                    self.stdout.write(f"  P{r.pregunta.orden}: '{r.pregunta.pregunta}' - Cat: {r.pregunta.categoria}")

                tipo_evaluacion_codigo = asignacion.evaluacion.tipo_evaluacion.codigo

                # Recalcular según tipo
                if tipo_evaluacion_codigo == 'ANUAL_AUX_PROCESOS':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliar_procesos import calcular_puntaje_ponderado_auxiliar_procesos
                    resultado_calc = calcular_puntaje_ponderado_auxiliar_procesos(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_MANTENIMIENTO':
                    from apps.evaluations.utils.respuestas_predefinidas_mantenimiento import calcular_puntaje_ponderado_mantenimiento
                    resultado_calc = calcular_puntaje_ponderado_mantenimiento(respuestas)
                else:
                    continue

                # Obtener nuevo puntaje
                nuevo_puntaje = Decimal(str(resultado_calc['puntaje_porcentaje']))
                puntaje_anterior = asignacion.puntaje_total or Decimal('0.00')

                # Mostrar información
                evaluacion = asignacion.evaluacion.nombre

                self.stdout.write(f"Evaluación: {evaluacion}")
                self.stdout.write(f"Puntaje anterior: {puntaje_anterior:.2f}%")
                self.stdout.write(f"Puntaje nuevo: {nuevo_puntaje:.2f}%")

                # Mostrar detalle por categorías
                detalle = resultado_calc.get('detalle_categorias', {})
                if detalle:
                    self.stdout.write("\nDetalle por categorías:")
                    for cat, datos in detalle.items():
                        self.stdout.write(
                            f"  • {cat}: promedio={datos['promedio']}/5 → "
                            f"{datos['porcentaje']:.1f}% × {datos['ponderacion']:.0f}% = "
                            f"{datos['contribucion']:.2f}% de contribución"
                        )

                # Verificar si hay diferencia
                diferencia = abs(nuevo_puntaje - puntaje_anterior)
                if diferencia >= Decimal('0.01'):
                    self.stdout.write(
                        self.style.SUCCESS(f"\n✓ Diferencia: {diferencia:.2f}%")
                    )

                    if not dry_run:
                        # Actualizar puntaje
                        asignacion.puntaje_total = nuevo_puntaje
                        asignacion.porcentaje_completado = nuevo_puntaje
                        asignacion.save()
                        self.stdout.write(self.style.SUCCESS("  → Puntaje actualizado"))
                    else:
                        self.stdout.write(self.style.WARNING("  → DRY RUN: No se guardó"))

                    actualizadas += 1
                else:
                    self.stdout.write(self.style.WARNING("\n→ Sin cambios significativos"))
                    sin_cambios += 1

            if dry_run:
                self.stdout.write(f"\n{'=' * 80}")
                self.stdout.write(self.style.WARNING("DRY RUN: Los cambios NO se guardaron"))
                self.stdout.write(f"{'=' * 80}\n")
                # Rollback si es dry-run
                transaction.set_rollback(True)

        # Resumen
        self.stdout.write(f"\n{'=' * 80}")
        self.stdout.write(self.style.SUCCESS(f"Evaluaciones con cambios: {actualizadas}"))
        self.stdout.write(f"Evaluaciones sin cambios: {sin_cambios}")
        self.stdout.write(f"Total procesadas: {actualizadas + sin_cambios}")
        self.stdout.write(f"{'=' * 80}\n")
