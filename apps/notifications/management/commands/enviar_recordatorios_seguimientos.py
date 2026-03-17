# =============================================================================
# apps/notifications/management/commands/enviar_recordatorios_seguimientos.py
# Comando para enviar recordatorios de seguimientos bimensuales próximos a vencer
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.evaluations.models import SeguimientoBimensual
from apps.notifications.models import TipoNotificacion, Notificacion


class Command(BaseCommand):
    help = 'Envía recordatorios automáticos para seguimientos bimensuales próximos a vencer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias-anticipacion',
            type=int,
            default=5,
            help='Días de anticipación para enviar recordatorio antes de fecha límite (default: 5)',
        )
        parser.add_argument(
            '--marcar-atrasados',
            action='store_true',
            help='Marcar como atrasados los seguimientos que pasaron su fecha límite',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular sin enviar notificaciones reales ni actualizar estados',
        )

    def handle(self, *args, **options):
        dias_anticipacion = options.get('dias_anticipacion', 5)
        marcar_atrasados = options.get('marcar_atrasados', False)
        dry_run = options.get('dry_run', False)

        self.stdout.write(self.style.SUCCESS(f'\n=== Recordatorios de Seguimientos Bimensuales ==='))
        self.stdout.write(f'Anticipación: {dias_anticipacion} días antes de fecha límite')
        if marcar_atrasados:
            self.stdout.write('Modo: Enviar recordatorios + Marcar atrasados')
        else:
            self.stdout.write('Modo: Solo enviar recordatorios')

        if dry_run:
            self.stdout.write(self.style.WARNING('MODO SIMULACIÓN - No se harán cambios reales\n'))
        else:
            self.stdout.write('')

        # ==================================================================
        # PARTE 1: ENVIAR RECORDATORIOS DE SEGUIMIENTOS PRÓXIMOS A VENCER
        # ==================================================================

        # Obtener tipo de notificación
        try:
            tipo_seguimiento = TipoNotificacion.objects.get(
                codigo='seguimiento_pendiente',
                activo=True
            )
        except TipoNotificacion.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                '\nERROR: Tipo de notificación "seguimiento_pendiente" no existe.'
                '\nEjecute: python manage.py configurar_notificaciones_evaluaciones\n'
            ))
            return

        # Calcular ventana de fechas para recordatorios
        hoy = timezone.now().date()
        fecha_limite_recordatorio = hoy + timedelta(days=dias_anticipacion)

        # Buscar seguimientos pendientes próximos a vencer
        seguimientos_proximos = SeguimientoBimensual.objects.filter(
            estado='pendiente',
            fecha_limite__lte=fecha_limite_recordatorio,
            fecha_limite__gte=hoy  # Solo los que AÚN no están atrasados
        ).select_related(
            'plan_mejora__asignacion_evaluacion__empleado_evaluado__usuario',
            'plan_mejora__asignacion_evaluacion__evaluador__usuario',
            'plan_mejora__asignacion_evaluacion__evaluacion'
        ).order_by('fecha_limite')

        total_proximos = seguimientos_proximos.count()
        self.stdout.write(f'\nSeguimientos proximos a vencer: {total_proximos}')

        recordatorios_empleados = 0
        recordatorios_supervisores = 0
        omitidos_sin_usuario = 0
        omitidos_notificacion_reciente = 0
        errores = 0

        for seguimiento in seguimientos_proximos:
            plan = seguimiento.plan_mejora
            asignacion = plan.asignacion_evaluacion
            empleado = asignacion.empleado_evaluado
            supervisor = asignacion.evaluador
            evaluacion = asignacion.evaluacion

            # Validaciones
            if not empleado.usuario:
                self.stdout.write(self.style.WARNING(
                    f'  [!] {empleado.nombre_completo} no tiene usuario. Se omite.'
                ))
                omitidos_sin_usuario += 1
                continue

            if not supervisor or not supervisor.usuario:
                self.stdout.write(self.style.WARNING(
                    f'  [!] Supervisor inválido para {empleado.nombre_completo}. Se omite.'
                ))
                omitidos_sin_usuario += 1
                continue

            # Verificar si ya se envió recordatorio recientemente
            ultima_notificacion = Notificacion.objects.filter(
                usuario=supervisor.usuario,
                tipo_notificacion__codigo='seguimiento_pendiente',
                datos_adicionales__numero_bimestre=seguimiento.numero_bimestre,
                datos_adicionales__empleado_id=str(empleado.id)
            ).order_by('-fecha_creacion').first()

            if ultima_notificacion:
                dias_desde_ultima = (timezone.now() - ultima_notificacion.fecha_creacion).days
                if dias_desde_ultima < 2:  # No enviar si se envió hace menos de 2 días
                    omitidos_notificacion_reciente += 1
                    continue

            # Calcular días restantes
            dias_restantes = (seguimiento.fecha_limite - hoy).days

            # Mostrar información
            self.stdout.write(f'\n  [{empleado.nombre_completo}] - Bimestre {seguimiento.numero_bimestre}')
            self.stdout.write(f'    Fecha límite: {seguimiento.fecha_limite.strftime("%d/%m/%Y")} ({dias_restantes} días restantes)')
            self.stdout.write(f'    Evaluación: {evaluacion.nombre}')

            # Preparar datos para notificación
            datos_notificacion = {
                'nombre_empleado': empleado.nombre_completo,
                'numero_bimestre': seguimiento.numero_bimestre,
                'fecha_limite': seguimiento.fecha_limite.strftime('%d/%m/%Y'),
                'dias_restantes': dias_restantes,
                'nombre_evaluacion': evaluacion.nombre,
                'empleado_id': str(empleado.id),
                'seguimiento_id': str(seguimiento.id),
            }

            if not dry_run:
                # Notificación al SUPERVISOR
                try:
                    Notificacion.objects.create(
                        usuario=supervisor.usuario,
                        tipo_notificacion=tipo_seguimiento,
                        titulo=f'Recordatorio: Seguimiento Bimensual {seguimiento.numero_bimestre}° - {empleado.nombre_completo}',
                        mensaje=f'El seguimiento bimensual {seguimiento.numero_bimestre}° de {empleado.nombre_completo} vence el {datos_notificacion["fecha_limite"]} ({dias_restantes} días restantes). Por favor, realiza el seguimiento del plan de mejora.',
                        datos_adicionales=datos_notificacion
                    )
                    recordatorios_supervisores += 1
                    self.stdout.write(self.style.SUCCESS(f'    [+] Recordatorio enviado al supervisor'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    [X] Error al enviar a supervisor: {e}'))
                    errores += 1

                # Notificación al EMPLEADO (informativa)
                try:
                    Notificacion.objects.create(
                        usuario=empleado.usuario,
                        tipo_notificacion=tipo_seguimiento,
                        titulo=f'Próximo Seguimiento Bimensual {seguimiento.numero_bimestre}°',
                        mensaje=f'Tu supervisor realizará el seguimiento bimensual {seguimiento.numero_bimestre}° de tu plan de mejora antes del {datos_notificacion["fecha_limite"]}. Prepárate para mostrar tus avances.',
                        datos_adicionales=datos_notificacion
                    )
                    recordatorios_empleados += 1
                    self.stdout.write(self.style.SUCCESS(f'    [+] Recordatorio enviado al empleado'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    [X] Error al enviar a empleado: {e}'))
                    errores += 1
            else:
                # Modo dry-run
                self.stdout.write(self.style.WARNING(f'    [SIMULADO] Recordatorio al supervisor'))
                self.stdout.write(self.style.WARNING(f'    [SIMULADO] Recordatorio al empleado'))
                recordatorios_supervisores += 1
                recordatorios_empleados += 1

        # ==================================================================
        # PARTE 2: MARCAR SEGUIMIENTOS ATRASADOS
        # ==================================================================

        seguimientos_atrasados_actualizados = 0

        if marcar_atrasados:
            self.stdout.write(f'\n\nBuscando seguimientos atrasados...')

            seguimientos_atrasados = SeguimientoBimensual.objects.filter(
                estado='pendiente',
                fecha_limite__lt=hoy  # Fecha límite ya pasó
            ).select_related(
                'plan_mejora__asignacion_evaluacion__empleado_evaluado'
            )

            total_atrasados = seguimientos_atrasados.count()
            self.stdout.write(f'Seguimientos atrasados encontrados: {total_atrasados}\n')

            for seguimiento in seguimientos_atrasados:
                empleado = seguimiento.plan_mejora.asignacion_evaluacion.empleado_evaluado
                dias_atraso = (hoy - seguimiento.fecha_limite).days

                self.stdout.write(f'  [ATRASADO] {empleado.nombre_completo} - Bimestre {seguimiento.numero_bimestre}')
                self.stdout.write(f'    Fecha límite: {seguimiento.fecha_limite.strftime("%d/%m/%Y")} ({dias_atraso} días de atraso)')

                if not dry_run:
                    seguimiento.estado = 'atrasado'
                    seguimiento.save(update_fields=['estado'])
                    seguimientos_atrasados_actualizados += 1
                    self.stdout.write(self.style.WARNING(f'    → Estado cambiado a ATRASADO'))
                else:
                    self.stdout.write(self.style.WARNING(f'    [SIMULADO] Cambiaría a ATRASADO'))
                    seguimientos_atrasados_actualizados += 1

        # ==================================================================
        # RESUMEN FINAL
        # ==================================================================

        self.stdout.write(self.style.SUCCESS(f'\n\n=== Proceso Completado ==='))

        self.stdout.write(self.style.SUCCESS('\nRECORDATORIOS:'))
        self.stdout.write(f'  - Seguimientos próximos a vencer: {total_proximos}')
        self.stdout.write(self.style.SUCCESS(f'  - Recordatorios a supervisores: {recordatorios_supervisores}'))
        self.stdout.write(self.style.SUCCESS(f'  - Recordatorios a empleados: {recordatorios_empleados}'))
        self.stdout.write(f'  - Omitidos (notificación reciente): {omitidos_notificacion_reciente}')
        self.stdout.write(f'  - Omitidos (sin usuario): {omitidos_sin_usuario}')

        if marcar_atrasados:
            self.stdout.write(self.style.WARNING('\nSEGUIMIENTOS ATRASADOS:'))
            self.stdout.write(f'  - Marcados como atrasados: {seguimientos_atrasados_actualizados}')

        if errores > 0:
            self.stdout.write(self.style.WARNING(f'\nErrores: {errores}'))

        total_recordatorios = recordatorios_empleados + recordatorios_supervisores
        self.stdout.write(self.style.SUCCESS(f'\nTOTAL RECORDATORIOS ENVIADOS: {total_recordatorios}\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('  ** MODO SIMULACIÓN - No se hicieron cambios reales **\n'))
