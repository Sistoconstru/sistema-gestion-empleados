# =============================================================================
# apps/notifications/management/commands/generar_notificaciones_evaluaciones_existentes.py
# Comando para generar notificaciones retroactivas de evaluaciones ya asignadas
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.evaluations.models import AsignacionEvaluacion
from apps.notifications.models import TipoNotificacion, Notificacion


class Command(BaseCommand):
    help = 'Genera notificaciones retroactivas para evaluaciones ya asignadas que están pendientes o en progreso'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Generar notificaciones incluso si ya existen para estas asignaciones',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)

        self.stdout.write(self.style.SUCCESS('\n=== Generando Notificaciones Retroactivas ===\n'))

        # Obtener tipos de notificación
        try:
            tipo_empleado = TipoNotificacion.objects.get(codigo='evaluacion_asignada', activo=True)
            tipo_evaluador = TipoNotificacion.objects.get(codigo='evaluacion_para_evaluar', activo=True)
        except TipoNotificacion.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(
                f'\nERROR: No se encontraron los tipos de notificación necesarios.'
                f'\nPor favor ejecute primero: python manage.py configurar_notificaciones_evaluaciones\n'
            ))
            return

        # Obtener evaluaciones pendientes o en progreso
        asignaciones = AsignacionEvaluacion.objects.filter(
            estado__in=['pendiente', 'en_progreso']
        ).select_related(
            'empleado_evaluado',
            'empleado_evaluado__usuario',
            'evaluador',
            'evaluador__usuario',
            'evaluacion'
        )

        total_asignaciones = asignaciones.count()
        self.stdout.write(f'Se encontraron {total_asignaciones} evaluaciones pendientes o en progreso.\n')

        if total_asignaciones == 0:
            self.stdout.write(self.style.WARNING('No hay evaluaciones pendientes. Nada que hacer.\n'))
            return

        notif_empleados_creadas = 0
        notif_empleados_existentes = 0
        notif_evaluadores_creadas = 0
        notif_evaluadores_existentes = 0
        errores = 0

        for asignacion in asignaciones:
            empleado = asignacion.empleado_evaluado
            evaluador = asignacion.evaluador
            evaluacion = asignacion.evaluacion

            # Validaciones
            if not empleado.usuario:
                self.stdout.write(self.style.WARNING(
                    f'  [!] Empleado {empleado.nombre_completo} no tiene usuario asociado. Se omite.'
                ))
                errores += 1
                continue

            if not evaluador or not evaluador.usuario:
                self.stdout.write(self.style.WARNING(
                    f'  [!] Evaluador no válido para {empleado.nombre_completo}. Se omite.'
                ))
                errores += 1
                continue

            # ========== NOTIFICACIÓN AL EMPLEADO ==========
            try:
                # Verificar si ya existe notificación para este empleado y evaluación
                existe_notif_empleado = Notificacion.objects.filter(
                    usuario=empleado.usuario,
                    tipo_notificacion=tipo_empleado,
                    datos_adicionales__nombre_evaluacion=evaluacion.nombre,
                    datos_adicionales__periodo=asignacion.periodo_evaluacion
                ).exists()

                if not existe_notif_empleado or force:
                    datos_empleado = {
                        'nombre_evaluacion': evaluacion.nombre,
                        'periodo': asignacion.periodo_evaluacion,
                        'nombre_evaluador': evaluador.nombre_completo,
                        'fecha_vencimiento': asignacion.fecha_vencimiento.strftime('%d/%m/%Y') if asignacion.fecha_vencimiento else 'N/A',
                    }

                    Notificacion.objects.create(
                        usuario=empleado.usuario,
                        tipo_notificacion=tipo_empleado,
                        titulo=tipo_empleado.plantilla_titulo.format(**datos_empleado),
                        mensaje=tipo_empleado.plantilla_mensaje.format(**datos_empleado),
                        datos_adicionales=datos_empleado
                    )
                    notif_empleados_creadas += 1
                    self.stdout.write(f'  [+] Notificación enviada a empleado: {empleado.nombre_completo}')
                else:
                    notif_empleados_existentes += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'  [X] Error al crear notificación para empleado {empleado.nombre_completo}: {e}'
                ))
                errores += 1

            # ========== NOTIFICACIÓN AL EVALUADOR ==========
            try:
                # Verificar si ya existe notificación para este evaluador y empleado
                existe_notif_evaluador = Notificacion.objects.filter(
                    usuario=evaluador.usuario,
                    tipo_notificacion=tipo_evaluador,
                    datos_adicionales__nombre_empleado=empleado.nombre_completo,
                    datos_adicionales__nombre_evaluacion=evaluacion.nombre
                ).exists()

                if not existe_notif_evaluador or force:
                    datos_evaluador = {
                        'nombre_empleado': empleado.nombre_completo,
                        'nombre_evaluacion': evaluacion.nombre,
                        'fecha_vencimiento': asignacion.fecha_vencimiento.strftime('%d/%m/%Y') if asignacion.fecha_vencimiento else 'N/A',
                    }

                    Notificacion.objects.create(
                        usuario=evaluador.usuario,
                        tipo_notificacion=tipo_evaluador,
                        titulo=tipo_evaluador.plantilla_titulo.format(**datos_evaluador),
                        mensaje=tipo_evaluador.plantilla_mensaje.format(**datos_evaluador),
                        datos_adicionales=datos_evaluador
                    )
                    notif_evaluadores_creadas += 1
                    self.stdout.write(f'  [+] Notificación enviada a evaluador: {evaluador.nombre_completo}')
                else:
                    notif_evaluadores_existentes += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'  [X] Error al crear notificación para evaluador {evaluador.nombre_completo}: {e}'
                ))
                errores += 1

        # Resumen final
        self.stdout.write(self.style.SUCCESS(f'\n=== Proceso Completado ==='))
        self.stdout.write(f'  - Evaluaciones procesadas: {total_asignaciones}')
        self.stdout.write(self.style.SUCCESS(f'  - Notificaciones a empleados creadas: {notif_empleados_creadas}'))
        self.stdout.write(f'  - Notificaciones a empleados ya existentes: {notif_empleados_existentes}')
        self.stdout.write(self.style.SUCCESS(f'  - Notificaciones a evaluadores creadas: {notif_evaluadores_creadas}'))
        self.stdout.write(f'  - Notificaciones a evaluadores ya existentes: {notif_evaluadores_existentes}')

        if errores > 0:
            self.stdout.write(self.style.WARNING(f'  - Errores encontrados: {errores}'))

        total_creadas = notif_empleados_creadas + notif_evaluadores_creadas
        self.stdout.write(self.style.SUCCESS(f'\n  TOTAL NOTIFICACIONES CREADAS: {total_creadas}\n'))

        if force:
            self.stdout.write(self.style.WARNING('  (Modo --force activado: se crearon notificaciones duplicadas)\n'))
