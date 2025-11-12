from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.employees.models import Empleado, EstadoEmpleado
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Activa automáticamente empleados que han completado su periodo de prueba de 3 meses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta el comando sin hacer cambios reales, solo muestra qué se haría',
        )
        parser.add_argument(
            '--dias-periodo',
            type=int,
            default=60,
            help='Número de días del periodo de prueba (por defecto 60 días = 2 meses)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        dias_periodo = options['dias_periodo']
        
        # Obtener estados
        try:
            estado_prueba = EstadoEmpleado.objects.get(codigo='p-prue')
            
            # Buscar estado activo entre diferentes códigos posibles
            estado_activo = None
            codigos_activo = ['999', 'ACTIVO', 'Activo', 'activo']
            for codigo in codigos_activo:
                try:
                    estado_activo = EstadoEmpleado.objects.get(codigo=codigo)
                    break
                except EstadoEmpleado.DoesNotExist:
                    continue
                    
            if not estado_activo:
                raise EstadoEmpleado.DoesNotExist("No se encontró ningún estado activo válido")
                
        except EstadoEmpleado.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f'Error: No se encontraron los estados necesarios: {e}')
            )
            return

        # Calcular fecha límite (hace 2 meses)
        fecha_limite = timezone.now().date() - timedelta(days=dias_periodo)
        
        # Buscar empleados en periodo de prueba que cumplen el tiempo
        empleados_a_activar = Empleado.objects.filter(
            estado=estado_prueba,
            fecha_ingreso__lte=fecha_limite
        ).select_related('estado', 'sede')
        
        total_empleados = empleados_a_activar.count()
        
        if total_empleados == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay empleados en periodo de prueba que cumplan los 2 meses.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Encontrados {total_empleados} empleados para activar:')
        )
        
        empleados_activados = []
        empleados_con_error = []
        
        for empleado in empleados_a_activar:
            dias_transcurridos = (timezone.now().date() - empleado.fecha_ingreso).days
            
            self.stdout.write(
                f'- {empleado.nombre_completo} (Doc: {empleado.numero_documento})'
            )
            self.stdout.write(
                f'  Fecha ingreso: {empleado.fecha_ingreso} '
                f'({dias_transcurridos} días transcurridos)'
            )
            self.stdout.write(
                f'  Sede: {empleado.sede}'
            )
            
            if not dry_run:
                try:
                    # Cambiar estado a activo
                    empleado.estado = estado_activo
                    empleado.save()
                    
                    empleados_activados.append(empleado)
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Activado exitosamente')
                    )
                    
                    # Log para auditoría
                    logger.info(
                        f'Empleado {empleado.numero_documento} '
                        f'({empleado.nombre_completo}) activado automáticamente '
                        f'después de {dias_transcurridos} días en periodo de prueba'
                    )
                    
                except Exception as e:
                    empleados_con_error.append((empleado, str(e)))
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Error al activar: {e}')
                    )
                    logger.error(
                        f'Error al activar empleado {empleado.numero_documento}: {e}'
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  → Se activaría (DRY RUN)')
                )
            
            self.stdout.write('')  # Línea en blanco para separar
        
        # Resumen final
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN completado. Se activarían {total_empleados} empleados.'
                )
            )
        else:
            activados = len(empleados_activados)
            errores = len(empleados_con_error)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Proceso completado: {activados} empleados activados exitosamente'
                )
            )
            
            if errores > 0:
                self.stdout.write(
                    self.style.ERROR(f'{errores} empleados con errores')
                )
                for empleado, error in empleados_con_error:
                    self.stdout.write(
                        self.style.ERROR(
                            f'- {empleado.nombre_completo}: {error}'
                        )
                    )
        
        # Información adicional sobre configuración
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Configuración utilizada:')
        self.stdout.write(f'- Días de periodo de prueba: {dias_periodo}')
        self.stdout.write(f'- Fecha límite de ingreso: {fecha_limite}')
        self.stdout.write(f'- Estado origen: {estado_prueba.nombre} ({estado_prueba.codigo})')
        self.stdout.write(f'- Estado destino: {estado_activo.nombre} ({estado_activo.codigo})')