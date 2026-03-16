# =============================================================================
# apps/notifications/management/commands/configurar_notificaciones_evaluaciones.py
# Comando para crear/actualizar tipos de notificación del módulo de evaluaciones
# =============================================================================

from django.core.management.base import BaseCommand
from apps.notifications.models import TipoNotificacion


class Command(BaseCommand):
    help = 'Configura los tipos de notificación necesarios para el módulo de evaluaciones'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Configurando Tipos de Notificación para Evaluaciones ===\n'))

        tipos_notificacion = [
            {
                'codigo': 'evaluacion_asignada',
                'nombre': 'Evaluación Asignada',
                'descripcion': 'Notificación enviada al empleado cuando se le asigna una nueva evaluación',
                'plantilla_titulo': 'Nueva evaluación: {nombre_evaluacion}',
                'plantilla_mensaje': 'Se te ha asignado la evaluación "{nombre_evaluacion}" para el período {periodo}. Tu evaluador será {nombre_evaluador}. Debes completarla antes del {fecha_vencimiento}.',
                'plantilla_email': '',
                'enviar_email': False,
                'enviar_push': True,
                'activo': True,
            },
            {
                'codigo': 'evaluacion_para_evaluar',
                'nombre': 'Evaluación por Realizar',
                'descripcion': 'Notificación enviada al evaluador cuando debe realizar una evaluación',
                'plantilla_titulo': 'Debes evaluar a {nombre_empleado}',
                'plantilla_mensaje': 'Tienes pendiente la evaluación "{nombre_evaluacion}" para {nombre_empleado}. Debes completarla antes del {fecha_vencimiento}.',
                'plantilla_email': '',
                'enviar_email': False,
                'enviar_push': True,
                'activo': True,
            },
            {
                'codigo': 'plan_mejora_asignado',
                'nombre': 'Plan de Mejora Asignado',
                'descripcion': 'Notificación cuando se genera un plan de mejora para el empleado',
                'plantilla_titulo': 'Plan de Mejora Asignado',
                'plantilla_mensaje': 'Se ha generado un plan de mejora basado en tu evaluación "{nombre_evaluacion}". Por favor revisa las áreas a mejorar y las acciones propuestas.',
                'plantilla_email': '',
                'enviar_email': False,
                'enviar_push': True,
                'activo': True,
            },
            {
                'codigo': 'seguimiento_pendiente',
                'nombre': 'Seguimiento Bimensual Pendiente',
                'descripcion': 'Notificación al supervisor sobre seguimiento bimensual pendiente',
                'plantilla_titulo': 'Seguimiento bimensual #{numero_seguimiento} pendiente',
                'plantilla_mensaje': 'Debes realizar el seguimiento bimensual #{numero_seguimiento} del plan de mejora de {nombre_empleado}.',
                'plantilla_email': '',
                'enviar_email': False,
                'enviar_push': True,
                'activo': True,
            },
            {
                'codigo': 'evaluacion_final_pendiente',
                'nombre': 'Evaluación Final Pendiente de Aceptación',
                'descripcion': 'Notificación al empleado cuando debe aceptar o rechazar su evaluación final',
                'plantilla_titulo': 'Evaluación Final Pendiente de Aceptación',
                'plantilla_mensaje': 'Tu evaluación final ha sido completada. Debes revisarla y aceptarla o rechazarla con motivo justificado.',
                'plantilla_email': '',
                'enviar_email': False,
                'enviar_push': True,
                'activo': True,
            },
            {
                'codigo': 'evaluacion_final_rechazada',
                'nombre': 'Evaluación Final Rechazada - Requiere Validación RRHH',
                'descripcion': 'Notificación a RRHH cuando un empleado rechaza su evaluación final',
                'plantilla_titulo': 'Evaluación final rechazada por {nombre_empleado}',
                'plantilla_mensaje': '{nombre_empleado} ha rechazado su evaluación final. Requiere validación de Gestión Humana.',
                'plantilla_email': '',
                'enviar_email': False,
                'enviar_push': True,
                'activo': True,
            },
            {
                'codigo': 'recordatorio_evaluacion',
                'nombre': 'Recordatorio - Evaluación Pendiente',
                'descripcion': 'Recordatorio automático cuando una evaluación lleva varios días sin iniciarse',
                'plantilla_titulo': 'Recordatorio: Evaluación pendiente',
                'plantilla_mensaje': 'Tienes pendiente la evaluación "{nombre_evaluacion}" asignada hace {dias_pendiente} días. Por favor complétala antes del {fecha_vencimiento}.',
                'plantilla_email': '',
                'enviar_email': False,
                'enviar_push': True,
                'activo': True,
            },
        ]

        creados = 0
        actualizados = 0

        for tipo_data in tipos_notificacion:
            tipo, created = TipoNotificacion.objects.update_or_create(
                codigo=tipo_data['codigo'],
                defaults={
                    'nombre': tipo_data['nombre'],
                    'descripcion': tipo_data['descripcion'],
                    'plantilla_titulo': tipo_data['plantilla_titulo'],
                    'plantilla_mensaje': tipo_data['plantilla_mensaje'],
                    'plantilla_email': tipo_data['plantilla_email'],
                    'enviar_email': tipo_data['enviar_email'],
                    'enviar_push': tipo_data['enviar_push'],
                    'activo': tipo_data['activo'],
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'  [+] Creado: {tipo.codigo} - {tipo.nombre}'))
                creados += 1
            else:
                self.stdout.write(self.style.WARNING(f'  [~] Actualizado: {tipo.codigo} - {tipo.nombre}'))
                actualizados += 1

        self.stdout.write(self.style.SUCCESS(f'\n=== Configuración Completada ==='))
        self.stdout.write(self.style.SUCCESS(f'  - Tipos creados: {creados}'))
        self.stdout.write(self.style.SUCCESS(f'  - Tipos actualizados: {actualizados}'))
        self.stdout.write(self.style.SUCCESS(f'  - Total: {len(tipos_notificacion)}\n'))
