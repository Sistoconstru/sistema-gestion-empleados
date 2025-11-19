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

    def _obtener_evaluacion_periodo_prueba(self):
        """Obtener la evaluación de período de prueba configurada"""
        try:
            evaluacion = EvaluacionDesempeño.objects.get(
                codigo='EVAL_PERIODO_PRUEBA_2024',
                activa=True
            )
            self.stdout.write(f'✓ Evaluación encontrada: {evaluacion.nombre}')
            return evaluacion
        except EvaluacionDesempeño.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ No se encontró evaluación EVAL_PERIODO_PRUEBA_2024 activa')
            )
            self.stdout.write(
                self.style.WARNING('   Ejecuta: python manage.py configurar_evaluacion_periodo_prueba')
            )
            return None

    def _buscar_empleados_elegibles(self, dias_servicio, empleado_id=None):
        """Buscar empleados elegibles para evaluación de período de prueba"""
        
        fecha_corte = date.today() - timedelta(days=dias_servicio)
        
        # Query base para empleados activos (usar estado activo)
        query = Q(estado__codigo='999')  # Código para empleados activos
        
        # Si se especifica un empleado específico
        if empleado_id:
            query &= Q(id=empleado_id)
        else:
            # Empleados que cumplan al menos los días especificados (fecha anterior o igual)
            query &= Q(fecha_ingreso__lte=fecha_corte)
        
        empleados = Empleado.objects.filter(query).select_related(
            'estado', 'sede', 'usuario'
        )
        
        self.stdout.write(f'📋 Empleados encontrados: {empleados.count()}')
        
        # Filtrar empleados que ya tienen evaluación asignada
        empleados_elegibles = []
        for empleado in empleados:
            # Verificar si ya tiene evaluación de período de prueba
            tiene_evaluacion = AsignacionEvaluacion.objects.filter(
                empleado_evaluado=empleado,
                evaluacion__tipo_evaluacion__codigo='PERIODO_PRUEBA'
            ).exists()
            
            if not tiene_evaluacion:
                empleados_elegibles.append(empleado)
                self.stdout.write(f'  ✓ {empleado.nombre_completo} - {empleado.sede} - Ingreso: {empleado.fecha_ingreso}')
            else:
                self.stdout.write(f'  ⚠️ {empleado.nombre_completo} - Ya tiene evaluación asignada')
        
        self.stdout.write(f'✅ Empleados elegibles para asignar: {len(empleados_elegibles)}')
        return empleados_elegibles

    def _procesar_asignaciones(self, evaluacion, empleados_elegibles, dry_run):
        """Procesar las asignaciones de evaluación"""
        
        if not empleados_elegibles:
            self.stdout.write(self.style.WARNING('⚠️ No hay empleados elegibles para asignar'))
            return 0
        
        total_asignados = 0
        
        for empleado in empleados_elegibles:
            try:
                # Buscar supervisor (evaluador)
                supervisor = self._buscar_supervisor(empleado)
                
                if not supervisor:
                    self.stdout.write(
                        self.style.ERROR(f'❌ {empleado.nombre_completo} - No tiene supervisor asignado')
                    )
                    continue
                
                # Crear asignación
                if not dry_run:
                    asignacion = self._crear_asignacion(evaluacion, empleado, supervisor)
                    if asignacion:
                        total_asignados += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✅ Asignado a {empleado.nombre_completo} '
                                f'(Evaluador: {supervisor.nombre_completo})'
                            )
                        )
                else:
                    # Modo simulación
                    total_asignados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'🧪 SIMULARÍA: Asignar a {empleado.nombre_completo} '
                            f'(Evaluador: {supervisor.nombre_completo})'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error procesando {empleado.nombre_completo}: {e}')
                )
        
        return total_asignados

    def _buscar_supervisor(self, empleado):
        """Buscar el supervisor directo del empleado"""
        
        # Para empleados de prueba, buscar cualquier usuario que sea administrador
        supervisor = Empleado.objects.filter(
            usuario__is_superuser=True
        ).first()
        
        if supervisor:
            return supervisor
        
        # Si no hay admin, buscar cualquier otro empleado activo
        supervisor_general = Empleado.objects.filter(
            estado__codigo='999'
        ).exclude(id=empleado.id).first()
        
        return supervisor_general

    def _crear_asignacion(self, evaluacion, empleado, supervisor):
        """Crear la asignación de evaluación"""
        try:
            # Fechas de la evaluación
            fecha_asignacion = date.today()
            fecha_limite = fecha_asignacion + timedelta(days=7)  # 7 días para completar
            
            asignacion = AsignacionEvaluacion.objects.create(
                empleado_evaluado=empleado,
                evaluacion=evaluacion,
                evaluador=supervisor,  # Campo correcto
                fecha_asignacion=fecha_asignacion,
                fecha_vencimiento=fecha_limite,
                estado='pendiente',
                observaciones=f'Evaluación de período de prueba - {empleado.fecha_ingreso.strftime("%d/%m/%Y")} (30 días)',
                asignado_por=self._obtener_usuario_sistema()
            )
            
            return asignacion
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creando asignación para {empleado.nombre_completo}: {e}')
            )
            return None

    def _obtener_usuario_sistema(self):
        """Obtener usuario del sistema para auditoría"""
        return Usuario.objects.filter(is_superuser=True).first()

    def _mostrar_resumen(self, total_asignados, dry_run):
        """Mostrar resumen de la operación"""
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'🧪 SIMULACIÓN COMPLETADA: {total_asignados} asignaciones simuladas')
            )
            self.stdout.write(
                self.style.WARNING('   Ejecuta sin --dry-run para aplicar los cambios')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ PROCESO COMPLETADO: {total_asignados} evaluaciones asignadas')
            )
            
        self.stdout.write('\n📋 PRÓXIMOS PASOS:')
        self.stdout.write('   1. Los supervisores recibirán notificación de las evaluaciones asignadas')
        self.stdout.write('   2. Las evaluaciones deben completarse en un plazo de 7 días')
        self.stdout.write('   3. Los resultados requieren aprobación administrativa')
        
        if total_asignados > 0:
            self.stdout.write('\n🔗 ENLACES ÚTILES:')
            self.stdout.write('   - Dashboard evaluaciones: /evaluaciones/')
            self.stdout.write('   - Admin panel: /admin/evaluations/asignacionevaluacion/')