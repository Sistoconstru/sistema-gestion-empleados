# =============================================================================
# apps/evaluations/signals.py
# Signals para auto-asignación de evaluaciones
# =============================================================================

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import logging

from .models import EvaluacionCargo, AsignacionEvaluacion
from apps.employees.models import Empleado, HistorialCargo

# Logger para errores
logger = logging.getLogger(__name__)


@receiver(post_save, sender=EvaluacionCargo)
def asignar_evaluacion_a_empleados_cargo(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se ACTIVA una evaluación asignada a un cargo.

    NUEVO FLUJO CON CONTROL DE ACTIVACIÓN:
    1. Admin asigna evaluación a cargo → estado='programada' → NO hace nada
    2. Admin activa la evaluación desde el admin → estado='activa' → Asigna a empleados
    3. Para cada empleado con ese cargo:
       - Crea AsignacionEvaluacion
       - Asigna al jefe_directo como evaluador
       - Usa fecha_vencimiento_planeada del EvaluacionCargo

    IMPORTANTE: Este signal NO se ejecuta al crear (estado='programada')
    Solo se ejecuta cuando se actualiza a estado='activa' desde el admin
    """

    # NO procesar en creación (cuando se asigna al cargo por primera vez)
    if created:
        print(f"[SIGNAL] Evaluación '{instance.evaluacion.nombre}' asignada al cargo '{instance.cargo.nombre}' en estado PROGRAMADA.")
        print(f"[SIGNAL] Para activarla y asignar a empleados, use la acción 'Activar Evaluación' en el admin.\n")
        return

    # Solo procesar si el estado cambió a 'activa'
    if instance.estado != 'activa':
        return

    cargo = instance.cargo
    evaluacion = instance.evaluacion
    asignado_por = instance.asignado_por

    # Verificación de seguridad: asignado_por no puede ser None
    if not asignado_por:
        print(f"[SIGNAL] ERROR: No se puede asignar evaluación sin usuario asignador. Se omite el proceso.")
        return

    print(f"\n[SIGNAL] ACTIVANDO evaluación '{evaluacion.nombre}' para el cargo '{cargo.nombre}'")
    print(f"[SIGNAL] Activada por: {instance.activada_por or 'Sistema'}")

    # Obtener todos los empleados activos con este cargo ACTUALMENTE
    # Importante: Solo considerar el historial ACTIVO del empleado
    empleados_con_cargo = Empleado.objects.filter(
        estado__codigo='999',  # Estado ACTIVO
        historialcargo__cargo=cargo,
        historialcargo__activo=True
    ).distinct()

    # Verificar que realmente tienen este cargo como su historial activo actual
    empleados_con_cargo = [
        emp for emp in empleados_con_cargo
        if HistorialCargo.objects.filter(
            empleado=emp,
            cargo=cargo,
            activo=True
        ).exists()
    ]

    print(f"[SIGNAL] Se encontraron {len(empleados_con_cargo)} empleados activos con el cargo '{cargo.nombre}'")

    # Usar fecha de vencimiento planeada o calcular una por defecto
    if instance.fecha_vencimiento_planeada:
        fecha_vencimiento = instance.fecha_vencimiento_planeada
    else:
        fecha_vencimiento = timezone.now() + timedelta(days=instance.dias_para_completar)

    # Crear periodo de evaluación
    # Usar el período configurado en EvaluacionCargo si está disponible, sino usar año actual
    if instance.periodo_a_evaluar:
        periodo_evaluacion = instance.periodo_a_evaluar
    else:
        año_actual = timezone.now().year
        periodo_evaluacion = f"{año_actual}"

    asignaciones_creadas = 0
    asignaciones_existentes = 0
    empleados_sin_jefe = 0

    for empleado in empleados_con_cargo:
        # Obtener el jefe directo del empleado
        try:
            historial_activo = HistorialCargo.objects.get(
                empleado=empleado,
                activo=True
            )
            jefe_directo = historial_activo.jefe_directo

            if not jefe_directo:
                empleados_sin_jefe += 1
                print(f"[SIGNAL] ADVERTENCIA: El empleado {empleado.nombre_completo} ({historial_activo.cargo.nombre}) no tiene jefe directo asignado.")
                print(f"[SIGNAL]            NO se asignará evaluación. Debe asignar jefe directo manualmente desde el admin.")
                continue

        except HistorialCargo.DoesNotExist:
            print(f"[SIGNAL] ADVERTENCIA: El empleado {empleado.nombre_completo} no tiene historial de cargo activo. Se omite.")
            continue

        # Verificar si ya existe una asignación para este empleado con esta evaluación
        asignacion_existente = AsignacionEvaluacion.objects.filter(
            empleado_evaluado=empleado,
            evaluacion=evaluacion,
            periodo_evaluacion=periodo_evaluacion,
            estado__in=['pendiente', 'en_progreso']  # No crear si ya está pendiente o en progreso
        ).exists()

        if asignacion_existente:
            print(f"[SIGNAL] Ya existe asignación para {empleado.nombre_completo}. Se omite.")
            asignaciones_existentes += 1
            continue

        # Crear AsignacionEvaluacion
        asignacion = AsignacionEvaluacion.objects.create(
            empleado_evaluado=empleado,
            evaluacion=evaluacion,
            evaluador=jefe_directo,
            periodo_evaluacion=periodo_evaluacion,
            fecha_vencimiento=fecha_vencimiento,
            estado='pendiente',
            es_autoevaluacion=False,
            porcentaje_completado=0,
            asignado_por=asignado_por  # Usuario que asignó la evaluación al cargo
        )

        print(f"[SIGNAL] ✓ Asignación creada: {empleado.nombre_completo} será evaluado por {jefe_directo.nombre_completo}")
        asignaciones_creadas += 1

        # ========== CREAR NOTIFICACIONES ==========

        # 1. Notificación al EMPLEADO que será evaluado
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion

            tipo_notif_empleado = TipoNotificacion.objects.get(
                codigo='evaluacion_asignada',
                activo=True
            )

            datos_empleado = {
                'nombre_evaluacion': evaluacion.nombre,
                'periodo': periodo_evaluacion,
                'nombre_evaluador': jefe_directo.nombre_completo,
                'fecha_vencimiento': fecha_vencimiento.strftime('%d/%m/%Y') if fecha_vencimiento else 'N/A',
            }

            Notificacion.objects.create(
                usuario=empleado.usuario,
                tipo_notificacion=tipo_notif_empleado,
                titulo=tipo_notif_empleado.plantilla_titulo.format(**datos_empleado),
                mensaje=tipo_notif_empleado.plantilla_mensaje.format(**datos_empleado),
                datos_adicionales=datos_empleado
            )
            print(f"[SIGNAL]   → Notificación enviada al empleado: {empleado.nombre_completo}")

        except TipoNotificacion.DoesNotExist:
            logger.warning(f"Tipo de notificación 'evaluacion_asignada' no existe. Ejecute: python manage.py configurar_notificaciones_evaluaciones")
        except Exception as e:
            logger.warning(f"Error al crear notificación para empleado {empleado.nombre_completo}: {e}")

        # 2. Notificación al EVALUADOR (jefe directo)
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion

            tipo_notif_evaluador = TipoNotificacion.objects.get(
                codigo='evaluacion_para_evaluar',
                activo=True
            )

            datos_evaluador = {
                'nombre_empleado': empleado.nombre_completo,
                'nombre_evaluacion': evaluacion.nombre,
                'fecha_vencimiento': fecha_vencimiento.strftime('%d/%m/%Y') if fecha_vencimiento else 'N/A',
            }

            Notificacion.objects.create(
                usuario=jefe_directo.usuario,
                tipo_notificacion=tipo_notif_evaluador,
                titulo=tipo_notif_evaluador.plantilla_titulo.format(**datos_evaluador),
                mensaje=tipo_notif_evaluador.plantilla_mensaje.format(**datos_evaluador),
                datos_adicionales=datos_evaluador
            )
            print(f"[SIGNAL]   → Notificación enviada al evaluador: {jefe_directo.nombre_completo}")

        except TipoNotificacion.DoesNotExist:
            logger.warning(f"Tipo de notificación 'evaluacion_para_evaluar' no existe. Ejecute: python manage.py configurar_notificaciones_evaluaciones")
        except Exception as e:
            logger.warning(f"Error al crear notificación para evaluador {jefe_directo.nombre_completo}: {e}")

    print(f"\n[SIGNAL] ✅ EVALUACIÓN ACTIVADA EXITOSAMENTE")
    print(f"[SIGNAL] RESUMEN:")
    print(f"  - Evaluación: {evaluacion.nombre}")
    print(f"  - Cargo: {cargo.nombre}")
    print(f"  - Asignaciones creadas: {asignaciones_creadas}")
    print(f"  - Asignaciones ya existentes (omitidas): {asignaciones_existentes}")
    print(f"  - Empleados sin jefe directo (no asignados): {empleados_sin_jefe}")
    print(f"  - Total empleados procesados: {len(empleados_con_cargo)}")
    print(f"  - Fecha de vencimiento: {fecha_vencimiento}")
    print(f"  - Período: {periodo_evaluacion}")

    if empleados_sin_jefe > 0:
        print(f"\n[SIGNAL] ⚠ ATENCIÓN: {empleados_sin_jefe} empleados no recibieron evaluación por falta de jefe directo.")
        print(f"[SIGNAL] Para verificar: python manage.py verificar_jefes_directos --sin-jefe")
        print(f"[SIGNAL] Para asignar jefes: python manage.py asignar_jefes_automaticamente\n")
    else:
        print()


@receiver(pre_delete, sender=EvaluacionCargo)
def eliminar_asignaciones_pendientes_al_eliminar_evaluacion_cargo(sender, instance, **kwargs):
    """
    Signal que se ejecuta ANTES de eliminar una EvaluacionCargo.

    Elimina automáticamente las asignaciones que están en estado 'pendiente' o 'en_progreso',
    pero PRESERVA las asignaciones completadas (historial importante).

    Esto permite reasignar evaluaciones sin errores de duplicidad.
    """
    evaluacion = instance.evaluacion
    cargo = instance.cargo

    print(f"\n[SIGNAL DELETE] Eliminando EvaluacionCargo: '{evaluacion.nombre}' para cargo '{cargo.nombre}'")

    # Buscar asignaciones pendientes o en progreso asociadas a esta evaluación
    asignaciones_activas = AsignacionEvaluacion.objects.filter(
        evaluacion=evaluacion,
        empleado_evaluado__historialcargo__cargo=cargo,
        empleado_evaluado__historialcargo__activo=True,
        estado__in=['pendiente', 'en_progreso']
    ).distinct()

    count_eliminadas = asignaciones_activas.count()

    if count_eliminadas > 0:
        print(f"[SIGNAL DELETE] Eliminando {count_eliminadas} asignación(es) en estado 'pendiente' o 'en_progreso'...")

        # Mostrar detalles de lo que se eliminará
        for asignacion in asignaciones_activas:
            print(f"[SIGNAL DELETE]   - Empleado: {asignacion.empleado_evaluado.nombre_completo} - Estado: {asignacion.estado}")

        # Eliminar las asignaciones
        asignaciones_activas.delete()
        print(f"[SIGNAL DELETE] ✓ Asignaciones eliminadas exitosamente.")
    else:
        print(f"[SIGNAL DELETE] No hay asignaciones pendientes o en progreso para eliminar.")

    # Verificar si hay asignaciones completadas (solo informativo)
    asignaciones_completadas = AsignacionEvaluacion.objects.filter(
        evaluacion=evaluacion,
        empleado_evaluado__historialcargo__cargo=cargo,
        estado='completada'
    ).distinct().count()

    if asignaciones_completadas > 0:
        print(f"[SIGNAL DELETE] ℹ Se preservan {asignaciones_completadas} asignación(es) completadas (historial).")

    print()
