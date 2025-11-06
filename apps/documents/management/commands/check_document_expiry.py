# =============================================================================
# apps/documents/management/commands/check_document_expiry.py - COMANDO PARA VENCIMIENTOS
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date, timedelta
import logging

from apps.documents.models import DocumentoEmpleado
from apps.employees.models import Empleado

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Verificar documentos próximos a vencer y enviar notificaciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin enviar emails (solo mostrar resultados)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días de anticipación para notificar (default: 30)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_ahead = options['days']
        
        self.stdout.write(self.style.SUCCESS(f'🔍 Verificando documentos que vencen en {days_ahead} días...'))
        
        # Fecha límite para notificación
        fecha_limite = date.today() + timedelta(days=days_ahead)
        
        # Obtener documentos que vencen pronto
        documentos_por_vencer = DocumentoEmpleado.objects.filter(
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__lte=fecha_limite,
            estado_aprobacion='aprobado'
        ).select_related('empleado', 'tipo_documento').order_by('fecha_vencimiento')
        
        # Agrupar por empleado
        empleados_notificar = {}
        documentos_vencidos = []
        documentos_proximos = []
        
        for doc in documentos_por_vencer:
            empleado = doc.empleado
            if empleado not in empleados_notificar:
                empleados_notificar[empleado] = []
            
            empleados_notificar[empleado].append(doc)
            
            # Clasificar por urgencia
            if doc.fecha_vencimiento < date.today():
                documentos_vencidos.append(doc)
            elif doc.fecha_vencimiento <= date.today() + timedelta(days=7):
                documentos_proximos.append(doc)
        
        # Mostrar resumen
        self.stdout.write(f'📊 Resumen:')
        self.stdout.write(f'   • Documentos vencidos: {len(documentos_vencidos)}')
        self.stdout.write(f'   • Documentos próximos a vencer (7 días): {len(documentos_proximos)}')
        self.stdout.write(f'   • Total documentos por vencer ({days_ahead} días): {len(documentos_por_vencer)}')
        self.stdout.write(f'   • Empleados a notificar: {len(empleados_notificar)}')
        
        if not empleados_notificar:
            self.stdout.write(self.style.SUCCESS('✅ No hay documentos próximos a vencer'))
            return
        
        # Procesar notificaciones
        emails_enviados = 0
        errores = 0
        
        for empleado, documentos_empleado in empleados_notificar.items():
            try:
                # Enviar notificación al empleado
                if empleado.correo_electronico and not dry_run:
                    self.enviar_notificacion_empleado(empleado, documentos_empleado)
                    emails_enviados += 1
                
                # Mostrar información
                self.stdout.write(f'👤 {empleado.nombre_completo} ({empleado.correo_electronico}):')
                for doc in documentos_empleado:
                    dias_para_vencer = (doc.fecha_vencimiento - date.today()).days
                    if dias_para_vencer < 0:
                        status = self.style.ERROR(f'VENCIDO hace {abs(dias_para_vencer)} días')
                    elif dias_para_vencer <= 7:
                        status = self.style.WARNING(f'Vence en {dias_para_vencer} días')
                    else:
                        status = f'Vence en {dias_para_vencer} días'
                    
                    self.stdout.write(f'   📄 {doc.tipo_documento.nombre}: {doc.fecha_vencimiento.strftime("%d/%m/%Y")} - {status}')
                
                self.stdout.write('')
                
            except Exception as e:
                logger.error(f'Error procesando empleado {empleado.numero_documento}: {str(e)}')
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Error con {empleado.nombre_completo}: {str(e)}')
                )
        
        # Enviar reporte a administradores
        if not dry_run:
            self.enviar_reporte_administradores(empleados_notificar, documentos_vencidos, documentos_proximos)
        
        # Resumen final
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: No se enviaron emails'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Proceso completado:'))
            self.stdout.write(f'   • Emails enviados: {emails_enviados}')
            self.stdout.write(f'   • Errores: {errores}')

    def enviar_notificacion_empleado(self, empleado, documentos):
        """Enviar notificación individual al empleado"""
        try:
            subject = f'🚨 Documentos próximos a vencer - {empleado.nombre_completo}'
            
            # Clasificar documentos por urgencia
            vencidos = [d for d in documentos if d.fecha_vencimiento < date.today()]
            proximos = [d for d in documentos if d.fecha_vencimiento >= date.today()]
            
            context = {
                'empleado': empleado,
                'documentos_vencidos': vencidos,
                'documentos_proximos': proximos,
                'fecha_actual': date.today()
            }
            
            # Renderizar email
            mensaje_html = render_to_string('documents/emails/documento_vencimiento.html', context)
            mensaje_texto = render_to_string('documents/emails/documento_vencimiento.txt', context)
            
            send_mail(
                subject=subject,
                message=mensaje_texto,
                html_message=mensaje_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[empleado.correo_electronico],
                fail_silently=False
            )
            
            logger.info(f'Notificación enviada a {empleado.correo_electronico}')
            
        except Exception as e:
            logger.error(f'Error enviando email a {empleado.correo_electronico}: {str(e)}')
            raise

    def enviar_reporte_administradores(self, empleados_notificar, documentos_vencidos, documentos_proximos):
        """Enviar reporte consolidado a administradores"""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Obtener emails de administradores
            admin_emails = list(User.objects.filter(
                is_staff=True, 
                is_active=True,
                email__isnull=False
            ).exclude(email='').values_list('email', flat=True))
            
            if not admin_emails:
                logger.warning('No hay administradores con email para enviar reporte')
                return
            
            subject = f'📊 Reporte de Documentos por Vencer - {date.today().strftime("%d/%m/%Y")}'
            
            context = {
                'empleados_notificar': empleados_notificar,
                'documentos_vencidos': documentos_vencidos,
                'documentos_proximos': documentos_proximos,
                'total_empleados': len(empleados_notificar),
                'fecha_reporte': date.today()
            }
            
            mensaje_html = render_to_string('documents/emails/reporte_vencimientos_admin.html', context)
            mensaje_texto = render_to_string('documents/emails/reporte_vencimientos_admin.txt', context)
            
            send_mail(
                subject=subject,
                message=mensaje_texto,
                html_message=mensaje_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False
            )
            
            logger.info(f'Reporte enviado a {len(admin_emails)} administradores')
            
        except Exception as e:
            logger.error(f'Error enviando reporte a administradores: {str(e)}')
