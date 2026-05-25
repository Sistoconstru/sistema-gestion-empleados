from django.core.management.base import BaseCommand
from apps.evaluations.models import EvaluacionDesempeño, AsignacionEvaluacion
from apps.employees.models import Empleado
from apps.authentication.models import Usuario
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Asigna evaluaciones generales (del SER) a todos los empleados activos para el periodo actual.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta el comando sin hacer cambios reales, solo muestra qué se haría',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        periodo_actual = timezone.now().strftime('%Y')  # Ajusta según tu lógica de periodos

        # Obtener usuario sistema para asignado_por
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(self.style.ERROR('Error: No se encontró un usuario administrador del sistema'))
            return

        # Filtra evaluaciones generales (no asociadas a cargo)
        evaluaciones_generales = EvaluacionDesempeño.objects.filter(
            tipo_evaluacion__es_autoevaluacion=True,
            activa=True
        ).select_related('tipo_evaluacion')

        # CORRECCIÓN CRÍTICA: Usar estado__codigo='999' en lugar de activo=True
        # El campo activo es booleano y no refleja el estado real del empleado
        empleados = Empleado.objects.filter(
            estado__codigo='999'  # Solo empleados ACTIVOS, no en periodo de prueba
        ).select_related('estado')

        total_asignadas = 0
        total_existentes = 0
        empleados_rechazados = 0
        empleados_antiguedad_insuficiente = 0

        # Constante: Meses mínimos de antigüedad para evaluación de desempeño
        MESES_MINIMOS_DESEMPEÑO = 5

        self.stdout.write(f'\n{self.style.WARNING("="*60)}')
        self.stdout.write(f'Asignando evaluaciones generales para el periodo {periodo_actual}')
        self.stdout.write(f'Evaluaciones a asignar: {evaluaciones_generales.count()}')
        self.stdout.write(f'Empleados activos: {empleados.count()}')
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: No se crearán asignaciones reales'))
        self.stdout.write(f'{self.style.WARNING("="*60)}\n')

        for evaluacion in evaluaciones_generales:
            self.stdout.write(f'\nProcesando evaluación: {evaluacion.nombre}')

            for empleado in empleados:
                # VALIDACIÓN CRÍTICA: Verificar compatibilidad entre estado del empleado y tipo de evaluación
                estado_empleado = empleado.estado.codigo if empleado.estado else None
                tipo_evaluacion = evaluacion.tipo_evaluacion.codigo if evaluacion.tipo_evaluacion else None

                if estado_empleado and tipo_evaluacion:
                    es_periodo_prueba = tipo_evaluacion == 'PERIODO_PRUEBA'
                    empleado_en_prueba = estado_empleado == 'p-prue'

                    # Validar reglas de negocio
                    if es_periodo_prueba and not empleado_en_prueba:
                        # Intentando asignar evaluación de periodo de prueba a empleado activo - OMITIR
                        self.stdout.write(f'  ⚠ OMITIDO: {empleado.nombre_completo} (no está en periodo de prueba)')
                        empleados_rechazados += 1
                        continue
                    elif not es_periodo_prueba and empleado_en_prueba:
                        # Intentando asignar evaluación de desempeño a empleado en periodo de prueba - OMITIR
                        self.stdout.write(f'  ⚠ OMITIDO: {empleado.nombre_completo} (está en periodo de prueba)')
                        empleados_rechazados += 1
                        continue

                    # VALIDACIÓN DE ANTIGÜEDAD: Para evaluaciones de desempeño (NO periodo de prueba),
                    # el empleado debe tener al menos 5 meses de antigüedad
                    if not es_periodo_prueba and empleado.fecha_ingreso:
                        fecha_actual = timezone.now().date()
                        antigüedad_dias = (fecha_actual - empleado.fecha_ingreso).days
                        antigüedad_meses = antigüedad_dias / 30.44  # Promedio de días por mes

                        if antigüedad_meses < MESES_MINIMOS_DESEMPEÑO:
                            self.stdout.write(f'  ⚠ OMITIDO: {empleado.nombre_completo} (antigüedad {antigüedad_meses:.1f} meses, mínimo {MESES_MINIMOS_DESEMPEÑO})')
                            empleados_antiguedad_insuficiente += 1
                            continue

                # Verificar si ya existe asignación
                existe = AsignacionEvaluacion.objects.filter(
                    empleado_evaluado=empleado,
                    evaluacion=evaluacion,
                    periodo_evaluacion=periodo_actual
                ).exists()

                if existe:
                    total_existentes += 1
                    continue

                if not dry_run:
                    # Calcular fecha de vencimiento (30 días por defecto)
                    fecha_vencimiento = timezone.now().date() + timedelta(days=30)

                    AsignacionEvaluacion.objects.create(
                        empleado_evaluado=empleado,
                        evaluacion=evaluacion,
                        periodo_evaluacion=periodo_actual,
                        fecha_vencimiento=fecha_vencimiento,
                        estado='pendiente',
                        es_autoevaluacion=True,
                        asignado_por=usuario_sistema
                    )
                    self.stdout.write(f'  ✓ Asignada a {empleado.nombre_completo}')
                else:
                    self.stdout.write(f'  [DRY-RUN] Se asignaría a {empleado.nombre_completo}')

                total_asignadas += 1

        # Resumen
        self.stdout.write(f'\n{self.style.WARNING("="*60)}')
        self.stdout.write(f'{self.style.SUCCESS("RESUMEN:")}')
        self.stdout.write(f'  - Asignaciones creadas: {total_asignadas}')
        self.stdout.write(f'  - Asignaciones ya existentes: {total_existentes}')
        self.stdout.write(f'  - Empleados rechazados por incompatibilidad de tipo: {empleados_rechazados}')
        self.stdout.write(f'  - Empleados rechazados por antigüedad insuficiente: {empleados_antiguedad_insuficiente}')
        self.stdout.write(f'{self.style.WARNING("="*60)}\n')
