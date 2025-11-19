# =============================================================================
# apps/evaluations/management/commands/asignar_evaluaciones_periodo_prueba.py
# Comando para asignar automáticamente evaluaciones de período de prueba
# =============================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta

from apps.employees.models import Empleado
from apps.evaluations.models import (
    EvaluacionDesempeño, AsignacionEvaluacion, TipoEvaluacion
)
from apps.authentication.models import Usuario


class Command(BaseCommand):
    help = 'Asigna evaluaciones de período de prueba a empleados que cumplan 30 días'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula las asignaciones sin guardar en la base de datos',
        )
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de días para asignar evaluación (default: 30)',
        )
        parser.add_argument(
            '--empleado-id',
            type=int,
            help='ID específico de empleado para asignar (opcional)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        dias_servicio = options['dias']
        empleado_id = options['empleado_id']
        
        self.stdout.write(
            self.style.SUCCESS(f'🎯 Asignando Evaluaciones de Período de Prueba - {dias_servicio} días')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🧪 MODO SIMULACIÓN - No se guardará nada'))
        
        # 1. Obtener evaluación de período de prueba
        evaluacion = self._obtener_evaluacion_periodo_prueba()
        if not evaluacion:
            return
        
        # 2. Buscar empleados elegibles
        empleados_elegibles = self._buscar_empleados_elegibles(dias_servicio, empleado_id)
        
        # 3. Procesar asignaciones
        total_asignados = self._procesar_asignaciones(evaluacion, empleados_elegibles, dry_run)
        
        # 4. Resumen final
        self._mostrar_resumen(total_asignados, dry_run)
            f'🎯 Buscando empleados para evaluación de periodo de prueba (>= {dias_alerta} días)...'
        )

        # Obtener configuración necesaria
        try:
            estado_prueba = EstadoEmpleado.objects.get(codigo='p-prue')
            tipo_evaluacion = TipoEvaluacion.objects.get(codigo='PERIODO_PRUEBA')
            evaluacion = EvaluacionDesempeño.objects.filter(
                tipo_evaluacion=tipo_evaluacion,
                activa=True
            ).first()
            usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
            
        except (EstadoEmpleado.DoesNotExist, TipoEvaluacion.DoesNotExist) as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )
            return
        
        if not evaluacion:
            self.stdout.write(
                self.style.ERROR('❌ Error: No se encontró evaluación activa para periodo de prueba')
            )
            return
        
        if not usuario_sistema:
            self.stdout.write(
                self.style.ERROR('❌ Error: No se encontró usuario del sistema')
            )
            return

        # Calcular fecha límite
        fecha_hoy = timezone.now().date()
        fecha_limite = fecha_hoy - timedelta(days=dias_alerta)
        fecha_maxima = fecha_hoy - timedelta(days=90)  # No evaluar muy tarde (máximo 3 meses)

        self.stdout.write(
            f'📅 Empleados con ingreso entre {fecha_maxima} y {fecha_limite}'
        )

        # Buscar empleados candidatos
        empleados_candidatos = Empleado.objects.filter(
            estado=estado_prueba,
            fecha_ingreso__lte=fecha_limite,
            fecha_ingreso__gte=fecha_maxima
        ).select_related('usuario', 'sede')

        self.stdout.write(
            f'👥 Encontrados {empleados_candidatos.count()} empleados candidatos'
        )

        if not empleados_candidatos:
            self.stdout.write(
                self.style.SUCCESS('✅ No hay empleados que requieran evaluación en este momento')
            )
            return

        # Procesar cada empleado
        asignaciones_creadas = 0
        asignaciones_existentes = 0
        errores = 0

        with transaction.atomic():
            for empleado in empleados_candidatos:
                try:
                    dias_transcurridos = (fecha_hoy - empleado.fecha_ingreso).days
                    periodo_evaluacion = f"{empleado.fecha_ingreso.year}-PP"  # Año-Periodo Prueba
                    
                    # Verificar si ya tiene asignación
                    existe_asignacion = AsignacionEvaluacion.objects.filter(
                        empleado_evaluado=empleado,
                        evaluacion=evaluacion,
                        periodo_evaluacion=periodo_evaluacion
                    ).exists()
                    
                    if existe_asignacion and not force:
                        self.stdout.write(
                            f'  ⚠️  {empleado.nombre_completo} - Ya tiene evaluación asignada'
                        )
                        asignaciones_existentes += 1
                        continue
                    
                    # Buscar supervisor (jefe inmediato)
                    evaluador = self._buscar_supervisor(empleado)
                    
                    if not evaluador:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠️  {empleado.nombre_completo} - No se encontró supervisor'
                            )
                        )
                        continue

                    # Calcular fecha de vencimiento (5 días después de los 30)
                    fecha_vencimiento = empleado.fecha_ingreso + timedelta(days=35)
                    
                    if not dry_run:
                        # Crear o actualizar asignación
                        asignacion, created = AsignacionEvaluacion.objects.get_or_create(
                            empleado_evaluado=empleado,
                            evaluacion=evaluacion,
                            periodo_evaluacion=periodo_evaluacion,
                            defaults={
                                'evaluador': evaluador,
                                'fecha_vencimiento': fecha_vencimiento,
                                'estado': 'pendiente',
                                'es_autoevaluacion': False,
                                'asignado_por': usuario_sistema,
                            }
                        )
                        
                        if force and not created:
                            # Actualizar si se forzó
                            asignacion.evaluador = evaluador
                            asignacion.fecha_vencimiento = fecha_vencimiento
                            asignacion.estado = 'pendiente'
                            asignacion.save()
                            created = True
                    
                    else:
                        created = True  # En dry-run simular creación
                    
                    if created:
                        self.stdout.write(
                            f'  ✅ {empleado.nombre_completo} ({dias_transcurridos} días) - '
                            f'Evaluador: {evaluador.nombre_completo} - '
                            f'Vence: {fecha_vencimiento}'
                        )
                        asignaciones_creadas += 1
                    else:
                        asignaciones_existentes += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ❌ Error procesando {empleado.nombre_completo}: {e}'
                        )
                    )
                    errores += 1

        # Resumen final
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📊 RESUMEN DE ASIGNACIONES:')
        self.stdout.write(f'  ✅ Asignaciones creadas: {asignaciones_creadas}')
        self.stdout.write(f'  ⚠️  Ya existían: {asignaciones_existentes}')
        self.stdout.write(f'  ❌ Errores: {errores}')
        self.stdout.write('='*60)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 Esto fue una simulación - Use sin --dry-run para aplicar cambios')
            )
        elif asignaciones_creadas > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 ¡Proceso completado! {asignaciones_creadas} evaluaciones asignadas')
            )

    def _buscar_supervisor(self, empleado):
        """Buscar el supervisor del empleado"""
        # Estrategia 1: Buscar por jefe del cargo actual
        historial_cargo = empleado.cargo_actual
        if historial_cargo and historial_cargo.cargo.jefe_inmediato:
            # Buscar empleado que tenga ese cargo de jefe
            supervisor = Empleado.objects.filter(
                historialcargo__cargo=historial_cargo.cargo.jefe_inmediato,
                historialcargo__activo=True,
                estado__codigo__in=['999', 'ACTIVO', 'Activo']  # Empleado activo
            ).first()
            if supervisor:
                return supervisor
        
        # Estrategia 2: Buscar por sede - Jefe de Recursos Humanos o similar
        if empleado.sede:
            supervisor = Empleado.objects.filter(
                sede=empleado.sede,
                historialcargo__cargo__nombre__icontains='recursos humanos',
                historialcargo__activo=True,
                estado__codigo__in=['999', 'ACTIVO', 'Activo']
            ).first()
            if supervisor:
                return supervisor
        
        # Estrategia 3: Buscar cualquier supervisor en la sede
        if empleado.sede:
            supervisor = Empleado.objects.filter(
                sede=empleado.sede,
                historialcargo__cargo__nombre__icontains='supervisor',
                historialcargo__activo=True,
                estado__codigo__in=['999', 'ACTIVO', 'Activo']
            ).first()
            if supervisor:
                return supervisor
        
        # Estrategia 4: Buscar por usuario con permisos de staff
        supervisor = Empleado.objects.filter(
            usuario__is_staff=True,
            estado__codigo__in=['999', 'ACTIVO', 'Activo']
        ).first()
        
        return supervisor