"""
Comando para asignar evaluaciones anuales a empleados según su cargo
El administrador ejecuta este comando cuando desea iniciar el período de evaluaciones
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from apps.employees.models import Empleado, HistorialCargo
from apps.evaluations.models import AsignacionEvaluacion, EvaluacionDesempeño, TipoEvaluacion, EvaluacionCargo
from apps.authentication.models import Usuario


class Command(BaseCommand):
    help = '''
    Asigna evaluaciones anuales a todos los empleados activos según su cargo.
    El administrador ejecuta este comando cuando desea iniciar el período de evaluaciones.

    Ejemplos:
      python manage.py asignar_evaluaciones_anuales --fecha-vencimiento 2026-03-16
      python manage.py asignar_evaluaciones_anuales --fecha-vencimiento 2026-03-16 --tipo ANUAL_OPERARIOS_PROD
      python manage.py asignar_evaluaciones_anuales --fecha-vencimiento 2026-03-16 --dry-run
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--fecha-vencimiento',
            type=str,
            help='Fecha de vencimiento en formato YYYY-MM-DD (ej: 2026-03-16)',
            required=False
        )
        parser.add_argument(
            '--dias-vencimiento',
            type=int,
            default=30,
            help='Días desde hoy para vencimiento si no se especifica fecha (por defecto 30 días)'
        )
        parser.add_argument(
            '--tipo',
            type=str,
            help='Código del tipo de evaluación específico (ej: ANUAL_OPERARIOS_PROD). Si no se especifica, asigna todas las anuales.',
            required=False
        )
        parser.add_argument(
            '--periodo',
            type=str,
            help='Período de evaluación (por defecto: año actual, ej: 2026)',
            required=False
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se haría sin crear asignaciones realmente'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        tipo_especifico = options.get('tipo')
        periodo = options.get('periodo') or str(timezone.now().year)

        # Calcular fecha de vencimiento
        if options.get('fecha_vencimiento'):
            try:
                fecha_vencimiento = datetime.strptime(options['fecha_vencimiento'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Error: Formato de fecha incorrecto. Use YYYY-MM-DD (ej: 2026-03-16)')
                )
                return
        else:
            fecha_vencimiento = timezone.now().date() + timedelta(days=options['dias_vencimiento'])

        self.stdout.write('='*80)
        self.stdout.write(self.style.WARNING('ASIGNACIÓN DE EVALUACIONES ANUALES'))
        self.stdout.write('='*80)
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: No se crearán asignaciones reales\n'))

        self.stdout.write(f'Período de evaluación: {periodo}')
        self.stdout.write(f'Fecha de vencimiento: {fecha_vencimiento.strftime("%d/%m/%Y")}')

        # Obtener usuario del sistema para asignado_por
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        if not usuario_sistema:
            self.stdout.write(self.style.ERROR('Error: No se encontró un usuario administrador'))
            return

        # Determinar qué tipos de evaluación procesar
        if tipo_especifico:
            tipos_evaluacion = TipoEvaluacion.objects.filter(
                codigo=tipo_especifico,
                activo=True
            )
            if not tipos_evaluacion.exists():
                self.stdout.write(
                    self.style.ERROR(f'Error: No se encontró el tipo de evaluación "{tipo_especifico}"')
                )
                return
        else:
            # Obtener todos los tipos anuales (excluir PERIODO_PRUEBA)
            tipos_evaluacion = TipoEvaluacion.objects.filter(
                activo=True
            ).exclude(
                codigo='PERIODO_PRUEBA'
            )

        self.stdout.write(f'\nTipos de evaluación a procesar: {tipos_evaluacion.count()}')
        for tipo in tipos_evaluacion:
            self.stdout.write(f'  • {tipo.codigo} - {tipo.nombre}')

        # Estadísticas
        total_asignaciones_creadas = 0
        total_asignaciones_existentes = 0
        empleados_sin_jefe = 0
        empleados_sin_evaluacion = 0
        errores = []

        # Obtener todos los empleados activos con cargo
        empleados_activos = Empleado.objects.filter(
            estado__codigo='999',  # ACTIVO
            historialcargo__activo=True
        ).distinct().select_related('sede')

        self.stdout.write(f'\nEmpleados activos encontrados: {empleados_activos.count()}')
        self.stdout.write('\nProcesando asignaciones...\n')

        for empleado in empleados_activos:
            # Obtener historial de cargo activo
            try:
                historial = HistorialCargo.objects.get(
                    empleado=empleado,
                    activo=True
                )
                cargo = historial.cargo
                jefe_directo = historial.jefe_directo

                if not jefe_directo:
                    empleados_sin_jefe += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ {empleado.nombre_completo} ({cargo.nombre}) - Sin jefe directo asignado. '
                            f'NO se asignará evaluación. Debe asignar jefe manualmente desde el admin.'
                        )
                    )
                    continue

                # Buscar evaluaciones asignadas a este cargo
                evaluaciones_cargo = EvaluacionCargo.objects.filter(
                    cargo=cargo
                ).select_related('evaluacion', 'evaluacion__tipo_evaluacion')

                # Filtrar por tipo si se especificó
                if tipo_especifico:
                    evaluaciones_cargo = evaluaciones_cargo.filter(
                        evaluacion__tipo_evaluacion__codigo=tipo_especifico
                    )

                if not evaluaciones_cargo.exists():
                    empleados_sin_evaluacion += 1
                    continue

                # Crear asignaciones para cada evaluación del cargo
                for ec in evaluaciones_cargo:
                    evaluacion = ec.evaluacion

                    # Verificar si ya existe asignación
                    existe = AsignacionEvaluacion.objects.filter(
                        empleado_evaluado=empleado,
                        evaluacion=evaluacion,
                        periodo_evaluacion=periodo
                    ).exists()

                    if existe:
                        total_asignaciones_existentes += 1
                        self.stdout.write(
                            f'  ○ {empleado.nombre_completo} - {evaluacion.tipo_evaluacion.codigo} - Ya existe'
                        )
                        continue

                    if not dry_run:
                        # Crear la asignación
                        AsignacionEvaluacion.objects.create(
                            empleado_evaluado=empleado,
                            evaluacion=evaluacion,
                            evaluador=jefe_directo,
                            periodo_evaluacion=periodo,
                            fecha_vencimiento=fecha_vencimiento,
                            estado='pendiente',
                            es_autoevaluacion=False,
                            asignado_por=usuario_sistema,
                            observaciones=f'Evaluación anual {periodo} - Asignada masivamente'
                        )

                    total_asignaciones_creadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ {empleado.nombre_completo} ({cargo.nombre}) - '
                            f'{evaluacion.tipo_evaluacion.codigo} - Evaluador: {jefe_directo.nombre_completo}'
                        )
                    )

            except HistorialCargo.DoesNotExist:
                empleados_sin_evaluacion += 1
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ {empleado.nombre_completo} - Sin historial de cargo activo')
                )
                continue
            except Exception as e:
                errores.append(f'{empleado.nombre_completo}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'  ✗ {empleado.nombre_completo} - Error: {str(e)}')
                )

        # Resumen final
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('RESUMEN DE ASIGNACIONES'))
        self.stdout.write('='*80)

        if dry_run:
            self.stdout.write(self.style.WARNING('(MODO DRY-RUN - No se crearon asignaciones reales)\n'))

        self.stdout.write(f'Asignaciones que se crearían/creadas: {total_asignaciones_creadas}')
        self.stdout.write(f'Asignaciones ya existentes (omitidas): {total_asignaciones_existentes}')
        self.stdout.write(f'Empleados sin evaluación para su cargo: {empleados_sin_evaluacion}')

        if empleados_sin_jefe > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ ATENCIÓN: {empleados_sin_jefe} empleados NO tienen jefe directo asignado'
                )
            )
            self.stdout.write(
                self.style.NOTICE(
                    'Estos empleados NO recibirán evaluaciones hasta que se les asigne un jefe directo.'
                )
            )
            self.stdout.write(
                self.style.NOTICE(
                    '\nPara verificar qué empleados necesitan jefe directo:'
                )
            )
            self.stdout.write('  python manage.py verificar_jefes_directos --sin-jefe')
            self.stdout.write(
                self.style.NOTICE(
                    '\nPara asignar jefes automáticamente (cuando hay 1 sola opción):'
                )
            )
            self.stdout.write('  python manage.py asignar_jefes_automaticamente')
            self.stdout.write(
                self.style.NOTICE(
                    '\nPara casos con múltiples opciones, asigne el jefe manualmente desde:'
                )
            )
            self.stdout.write('  Admin Django → Empleados → Historial de Cargo → Campo "Jefe directo"')
        else:
            self.stdout.write(f'Empleados sin jefe directo: {empleados_sin_jefe}')

        if errores:
            self.stdout.write(f'\nErrores encontrados: {len(errores)}')
            for error in errores:
                self.stdout.write(self.style.ERROR(f'  • {error}'))

        self.stdout.write('\n' + '='*80)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\nPara crear las asignaciones realmente, ejecute el comando sin --dry-run'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Proceso completado. Se crearon {total_asignaciones_creadas} asignaciones.'
                )
            )
