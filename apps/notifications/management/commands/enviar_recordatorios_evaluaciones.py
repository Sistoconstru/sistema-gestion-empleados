# =============================================================================
# apps/notifications/management/commands/enviar_recordatorios_evaluaciones.py
# Comando para enviar recordatorios automáticos de evaluaciones pendientes
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.evaluations.models import AsignacionEvaluacion
from apps.notifications.models import TipoNotificacion, Notificacion


class Command(BaseCommand):
    help = 'Envía recordatorios automáticos para evaluaciones que llevan varios días sin iniciarse'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=3,
            help='Número de días de inactividad antes de enviar recordatorio (default: 3)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular sin enviar notificaciones reales',
        )

    def handle(self, *args, **options):
        dias_umbral = options.get('dias', 3)
        dry_run = options.get('dry_run', False)

        self.stdout.write(self.style.SUCCESS(f'\n=== Enviando Recordatorios de Evaluaciones Pendientes ==='))
        self.stdout.write(f'Umbral de días sin actividad: {dias_umbral} días')
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO SIMULACIÓN - No se enviarán notificaciones reales\n'))
        else:
            self.stdout.write('')

        # Obtener tipo de notificación de recordatorio
        try:
            tipo_recordatorio = TipoNotificacion.objects.get(
                codigo='recordatorio_evaluacion',
                activo=True
            )
        except TipoNotificacion.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                '\nERROR: Tipo de notificación "recordatorio_evaluacion" no existe.'
                '\nEjecute: python manage.py configurar_notificaciones_evaluaciones\n'
            ))
            return

        # Fecha límite: hace X días
        fecha_limite = timezone.now() - timedelta(days=dias_umbral)

        # Obtener evaluaciones pendientes
        evaluaciones_pendientes = AsignacionEvaluacion.objects.filter(
            estado='pendiente'
        ).select_related(
            'empleado_evaluado',
            'empleado_evaluado__usuario',
            'evaluador',
            'evaluador__usuario',
            'evaluacion'
        )

        total_evaluaciones = evaluaciones_pendientes.count()
        self.stdout.write(f'Evaluaciones en estado PENDIENTE: {total_evaluaciones}\n')

        if total_evaluaciones == 0:
            self.stdout.write(self.style.SUCCESS('No hay evaluaciones pendientes. Nada que hacer.\n'))
            return

        recordatorios_empleados = 0
        recordatorios_evaluadores = 0
        omitidas_por_notificacion_reciente = 0
        omitidas_sin_usuario = 0
        errores = 0

        for asignacion in evaluaciones_pendientes:
            empleado = asignacion.empleado_evaluado
            evaluador = asignacion.evaluador
            evaluacion = asignacion.evaluacion

            # Validaciones básicas
            if not empleado.usuario:
                self.stdout.write(self.style.WARNING(
                    f'  [!] {empleado.nombre_completo} no tiene usuario. Se omite.'
                ))
                omitidas_sin_usuario += 1
                continue

            if not evaluador or not evaluador.usuario:
                self.stdout.write(self.style.WARNING(
                    f'  [!] Evaluador inválido para {empleado.nombre_completo}. Se omite.'
                ))
                omitidas_sin_usuario += 1
                continue

            # ========== VERIFICAR ÚLTIMA NOTIFICACIÓN ==========
            # Buscar la notificación más reciente relacionada con esta evaluación y empleado
            ultima_notificacion = Notificacion.objects.filter(
                usuario=empleado.usuario,
                tipo_notificacion__codigo__in=[
                    'evaluacion_asignada',
                    'recordatorio_evaluacion'
                ],
                datos_adicionales__nombre_evaluacion=evaluacion.nombre,
                datos_adicionales__periodo=asignacion.periodo_evaluacion
            ).order_by('-fecha_creacion').first()

            # Determinar la fecha de referencia
            if ultima_notificacion:
                fecha_referencia = ultima_notificacion.fecha_creacion
                tipo_ultima = "recordatorio" if ultima_notificacion.tipo_notificacion.codigo == 'recordatorio_evaluacion_pendiente' else "inicial"
            else:
                # Si no hay notificación, usar la fecha de asignación
                fecha_referencia = asignacion.fecha_asignacion
                tipo_ultima = "asignación"

            # Calcular días transcurridos
            dias_transcurridos = (timezone.now() - fecha_referencia).days

            # Si no ha pasado suficiente tiempo, omitir
            if dias_transcurridos < dias_umbral:
                omitidas_por_notificacion_reciente += 1
                continue

            # ========== ENVIAR RECORDATORIO ==========
            self.stdout.write(f'\n  [{empleado.nombre_completo}] - {evaluacion.nombre}')
            self.stdout.write(f'    Última actividad: hace {dias_transcurridos} días ({tipo_ultima})')

            # Calcular días desde asignación original
            dias_desde_asignacion = (timezone.now() - asignacion.fecha_asignacion).days

            # Preparar datos para la notificación
            datos_notificacion = {
                'nombre_evaluacion': evaluacion.nombre,
                'dias_pendiente': dias_desde_asignacion,
                'fecha_vencimiento': asignacion.fecha_vencimiento.strftime('%d/%m/%Y') if asignacion.fecha_vencimiento else 'N/A',
            }

            if not dry_run:
                # Recordatorio al EMPLEADO
                try:
                    Notificacion.objects.create(
                        usuario=empleado.usuario,
                        tipo_notificacion=tipo_recordatorio,
                        titulo=tipo_recordatorio.plantilla_titulo.format(**datos_notificacion),
                        mensaje=tipo_recordatorio.plantilla_mensaje.format(**datos_notificacion),
                        datos_adicionales={
                            **datos_notificacion,
                            'periodo': asignacion.periodo_evaluacion,
                            'nombre_evaluador': evaluador.nombre_completo,
                        }
                    )
                    recordatorios_empleados += 1
                    self.stdout.write(self.style.SUCCESS(f'    [+] Recordatorio enviado al empleado'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    [X] Error al enviar a empleado: {e}'))
                    errores += 1

                # Recordatorio al EVALUADOR
                try:
                    datos_evaluador = {
                        'nombre_evaluacion': evaluacion.nombre,
                        'dias_pendiente': dias_desde_asignacion,
                        'fecha_vencimiento': asignacion.fecha_vencimiento.strftime('%d/%m/%Y') if asignacion.fecha_vencimiento else 'N/A',
                    }

                    Notificacion.objects.create(
                        usuario=evaluador.usuario,
                        tipo_notificacion=tipo_recordatorio,
                        titulo=f'Recordatorio: Evaluar a {empleado.nombre_completo}',
                        mensaje=f'Recuerda completar la evaluación "{evaluacion.nombre}" para {empleado.nombre_completo}. Lleva {dias_desde_asignacion} días pendiente. Fecha límite: {datos_evaluador["fecha_vencimiento"]}.',
                        datos_adicionales={
                            **datos_evaluador,
                            'nombre_empleado': empleado.nombre_completo,
                            'periodo': asignacion.periodo_evaluacion,
                        }
                    )
                    recordatorios_evaluadores += 1
                    self.stdout.write(self.style.SUCCESS(f'    [+] Recordatorio enviado al evaluador'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    [X] Error al enviar a evaluador: {e}'))
                    errores += 1
            else:
                # Modo dry-run
                self.stdout.write(self.style.WARNING(f'    [SIMULADO] Recordatorio al empleado'))
                self.stdout.write(self.style.WARNING(f'    [SIMULADO] Recordatorio al evaluador'))
                recordatorios_empleados += 1
                recordatorios_evaluadores += 1

        # Resumen final
        self.stdout.write(self.style.SUCCESS(f'\n=== Proceso Completado ==='))
        self.stdout.write(f'  - Evaluaciones pendientes: {total_evaluaciones}')
        self.stdout.write(self.style.SUCCESS(f'  - Recordatorios a empleados: {recordatorios_empleados}'))
        self.stdout.write(self.style.SUCCESS(f'  - Recordatorios a evaluadores: {recordatorios_evaluadores}'))
        self.stdout.write(f'  - Omitidas (notificación reciente): {omitidas_por_notificacion_reciente}')
        self.stdout.write(f'  - Omitidas (sin usuario): {omitidas_sin_usuario}')

        if errores > 0:
            self.stdout.write(self.style.WARNING(f'  - Errores: {errores}'))

        total_recordatorios = recordatorios_empleados + recordatorios_evaluadores
        self.stdout.write(self.style.SUCCESS(f'\n  TOTAL RECORDATORIOS ENVIADOS: {total_recordatorios}\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('  ** MODO SIMULACIÓN - No se enviaron notificaciones reales **\n'))
