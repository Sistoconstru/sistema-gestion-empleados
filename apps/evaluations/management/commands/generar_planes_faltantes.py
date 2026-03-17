"""
Comando para generar planes de mejora que no se generaron automáticamente
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import AsignacionEvaluacion, PlanMejoraPredefinido, RespuestaEvaluacion


class Command(BaseCommand):
    help = 'Genera planes de mejora para evaluaciones completadas que no tienen plan'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se haría sin crear los planes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        # Obtener un usuario del sistema para asignar como generado_por
        from apps.authentication.models import Usuario
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()

        if not usuario_sistema:
            self.stdout.write(self.style.ERROR("ERROR: No se encontró un superusuario en el sistema."))
            self.stdout.write("Cree un superusuario con: python manage.py createsuperuser")
            return

        # Buscar evaluaciones completadas sin plan de mejora
        # IMPORTANTE: El estado correcto es 'completada' no 'completado'
        asignaciones_sin_plan = AsignacionEvaluacion.objects.filter(
            estado='completada',
            estado_aprobacion='pendiente_aprobacion'
        ).exclude(
            id__in=PlanMejoraPredefinido.objects.values_list('asignacion_evaluacion_id', flat=True)
        ).select_related('empleado_evaluado', 'evaluacion', 'evaluacion__tipo_evaluacion')

        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(f"Evaluaciones completadas SIN plan de mejora: {asignaciones_sin_plan.count()}")
        self.stdout.write(f"{'='*80}\n")

        if asignaciones_sin_plan.count() == 0:
            self.stdout.write(self.style.SUCCESS("No hay evaluaciones sin plan de mejora. Todo está en orden."))
            return

        planes_creados = 0
        planes_omitidos = 0

        for asignacion in asignaciones_sin_plan:
            self.stdout.write(f"\n{'-'*80}")
            self.stdout.write(f"ID: {asignacion.id}")
            self.stdout.write(f"Empleado: {asignacion.empleado_evaluado.nombre_completo}")
            self.stdout.write(f"Evaluación: {asignacion.evaluacion.nombre}")
            tipo_codigo = asignacion.evaluacion.tipo_evaluacion.codigo if asignacion.evaluacion.tipo_evaluacion else 'SIN TIPO'
            self.stdout.write(f"Tipo: {tipo_codigo}")
            if tipo_codigo == 'PERIODO_PRUEBA':
                self.stdout.write(f"Puntaje: {asignacion.puntaje_total}/21")
            else:
                self.stdout.write(f"Porcentaje: {asignacion.porcentaje_completado}%")

            # IMPORTANTE:
            # - Período de Prueba: Si puntaje = 21/21 → NO genera plan
            # - Evaluaciones Anuales: SIEMPRE genera plan (mejora o felicitación)
            debe_generar = True
            if tipo_codigo == 'PERIODO_PRUEBA':
                if asignacion.puntaje_total and asignacion.puntaje_total >= 21:
                    self.stdout.write(self.style.WARNING("  → Puntaje perfecto (21/21), NO requiere plan"))
                    debe_generar = False
                    planes_omitidos += 1
            # Para evaluaciones anuales siempre se genera plan (no hay condición)

            if not debe_generar:
                continue

            # Obtener respuestas
            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion=asignacion
            ).select_related('pregunta', 'opcion_seleccionada')

            if not respuestas.exists():
                self.stdout.write(self.style.WARNING("  → Sin respuestas, no se puede generar plan"))
                planes_omitidos += 1
                continue

            # Generar plan según tipo
            plan_texto = None

            try:
                if tipo_codigo == 'PERIODO_PRUEBA':
                    from apps.evaluations.views import _generar_aspectos_mejora_periodo_prueba
                    plan_texto = _generar_aspectos_mejora_periodo_prueba(asignacion)

                elif tipo_codigo == 'ANUAL_AUX_PROCESOS':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliar_procesos import (
                        generar_plan_mejora_auxiliar_procesos,
                        calcular_puntaje_ponderado_auxiliar_procesos
                    )
                    resultado = calcular_puntaje_ponderado_auxiliar_procesos(respuestas)
                    plan_texto = generar_plan_mejora_auxiliar_procesos(respuestas, resultado)

                elif tipo_codigo == 'ANUAL_MANTENIMIENTO':
                    from apps.evaluations.utils.respuestas_predefinidas_mantenimiento import (
                        generar_plan_mejora_mantenimiento,
                        calcular_puntaje_ponderado_mantenimiento
                    )
                    resultado = calcular_puntaje_ponderado_mantenimiento(respuestas)
                    plan_texto = generar_plan_mejora_mantenimiento(respuestas, resultado)

                elif tipo_codigo == 'ANUAL_OPERARIOS_PROD':
                    from apps.evaluations.utils.respuestas_predefinidas_operarios_produccion import (
                        generar_plan_mejora_operarios_produccion,
                        calcular_puntaje_ponderado_operarios_produccion
                    )
                    resultado = calcular_puntaje_ponderado_operarios_produccion(respuestas)
                    plan_texto = generar_plan_mejora_operarios_produccion(respuestas, resultado)

                elif tipo_codigo == 'ANUAL_COORD_PROC':
                    from apps.evaluations.utils.respuestas_predefinidas_coordinadores_procesos import (
                        generar_plan_mejora_coordinadores_procesos,
                        calcular_puntaje_ponderado_coordinadores_procesos
                    )
                    resultado = calcular_puntaje_ponderado_coordinadores_procesos(respuestas)
                    plan_texto = generar_plan_mejora_coordinadores_procesos(respuestas, resultado)

                elif tipo_codigo == 'ANUAL_AFILADORES':
                    from apps.evaluations.utils.respuestas_predefinidas_afiladores import (
                        generar_plan_mejora_afiladores,
                        calcular_puntaje_ponderado_afiladores
                    )
                    resultado = calcular_puntaje_ponderado_afiladores(respuestas)
                    plan_texto = generar_plan_mejora_afiladores(respuestas, resultado)
                else:
                    from apps.evaluations.utils.respuestas_predefinidas import generar_plan_automatico
                    respuestas_para_plan = respuestas.filter(opcion_seleccionada__valor_numerico__in=[1, 2, 3])
                    plan_texto = generar_plan_automatico(respuestas_para_plan)

                if plan_texto:
                    if not dry_run:
                        # Crear plan de mejora
                        plan = PlanMejoraPredefinido.objects.create(
                            asignacion_evaluacion=asignacion,
                            plan_mejora=plan_texto,
                            generado_por=usuario_sistema,
                            estado='pendiente_aprobacion'
                        )
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Plan de mejora generado (ID: {plan.id})"))
                        planes_creados += 1
                    else:
                        self.stdout.write(self.style.WARNING(f"  → [DRY RUN] Se generaría plan de mejora"))
                        self.stdout.write(f"    Primeros 150 caracteres: {plan_texto[:150]}...")
                        planes_creados += 1
                else:
                    self.stdout.write(self.style.ERROR("  ✗ No se pudo generar el plan de mejora"))
                    planes_omitidos += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ ERROR al generar plan: {e}"))
                import traceback
                traceback.print_exc()
                planes_omitidos += 1

        # Resumen
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write("RESUMEN:")
        self.stdout.write(self.style.SUCCESS(f"  Planes creados: {planes_creados}"))
        self.stdout.write(self.style.WARNING(f"  Planes omitidos: {planes_omitidos}"))
        self.stdout.write(f"{'='*80}\n")

        if dry_run:
            self.stdout.write(self.style.WARNING("MODO DRY RUN: No se crearon planes realmente\n"))
