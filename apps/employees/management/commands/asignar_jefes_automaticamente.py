"""
Comando de gestión para asignar jefes inmediatos automáticamente
a todos los HistorialCargo activos que no tienen jefe asignado.

Uso:
    python manage.py asignar_jefes_automaticamente
    python manage.py asignar_jefes_automaticamente --dry-run  # Simular sin guardar
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.employees.models import HistorialCargo
from apps.organizational.models import Cargo


class Command(BaseCommand):
    help = 'Asigna jefes inmediatos automáticamente a empleados con cargos activos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular la asignación sin guardar cambios en la base de datos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('=== MODO SIMULACIÓN (DRY RUN) ==='))
            self.stdout.write(self.style.WARNING('No se guardarán cambios en la base de datos\n'))

        self.stdout.write('Buscando empleados con cargos activos sin jefe asignado...\n')

        # Buscar todos los HistorialCargo activos sin jefe_directo
        cargos_sin_jefe = HistorialCargo.objects.filter(
            activo=True,
            jefe_directo__isnull=True
        ).select_related('empleado', 'cargo', 'cargo__cargo_jefe')

        total = cargos_sin_jefe.count()
        self.stdout.write(f'Encontrados: {total} registros sin jefe asignado\n')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('✓ No hay registros que actualizar'))
            return

        # Contadores para el reporte
        asignados = 0
        sin_cargo_jefe = 0
        sin_empleados_en_cargo_jefe = 0
        multiples_empleados_en_cargo_jefe = 0
        errores = 0

        self.stdout.write('Procesando...\n')
        self.stdout.write('-' * 80)

        for historial in cargos_sin_jefe:
            empleado_nombre = historial.empleado.nombre_completo
            cargo_nombre = historial.cargo.nombre

            # Verificar si el cargo tiene un cargo_jefe definido
            if not historial.cargo.cargo_jefe:
                sin_cargo_jefe += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'⊘ {empleado_nombre} ({cargo_nombre}): '
                        f'El cargo no tiene cargo_jefe definido en jerarquía'
                    )
                )
                continue

            cargo_jefe_nombre = historial.cargo.cargo_jefe.nombre

            # Buscar empleados activos en el cargo_jefe
            empleados_en_cargo_jefe = HistorialCargo.objects.filter(
                cargo=historial.cargo.cargo_jefe,
                activo=True
            ).select_related('empleado')

            cantidad_jefes = empleados_en_cargo_jefe.count()

            if cantidad_jefes == 0:
                sin_empleados_en_cargo_jefe += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'⊘ {empleado_nombre} ({cargo_nombre}): '
                        f'No hay empleados activos en cargo jefe "{cargo_jefe_nombre}"'
                    )
                )

            elif cantidad_jefes == 1:
                # ¡Asignar automáticamente!
                jefe = empleados_en_cargo_jefe.first().empleado

                if not dry_run:
                    try:
                        historial.jefe_directo = jefe
                        historial.save()
                        asignados += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ {empleado_nombre} ({cargo_nombre}) → '
                                f'{jefe.nombre_completo} ({cargo_jefe_nombre})'
                            )
                        )
                    except Exception as e:
                        errores += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error asignando jefe a {empleado_nombre}: {str(e)}'
                            )
                        )
                else:
                    asignados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ [SIMULADO] {empleado_nombre} ({cargo_nombre}) → '
                            f'{jefe.nombre_completo} ({cargo_jefe_nombre})'
                        )
                    )

            else:
                # Más de un empleado en el cargo jefe
                multiples_empleados_en_cargo_jefe += 1
                jefes_nombres = ', '.join([h.empleado.nombre_completo for h in empleados_en_cargo_jefe[:3]])
                if cantidad_jefes > 3:
                    jefes_nombres += f' y {cantidad_jefes - 3} más'

                self.stdout.write(
                    self.style.WARNING(
                        f'⊘ {empleado_nombre} ({cargo_nombre}): '
                        f'Hay {cantidad_jefes} empleados en cargo jefe "{cargo_jefe_nombre}" ({jefes_nombres}). '
                        f'Requiere asignación manual.'
                    )
                )

        # Reporte final
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('\nRESUMEN DE EJECUCIÓN:'))
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total procesados: {total}')
        self.stdout.write('')

        if asignados > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Jefes asignados: {asignados}'))
        else:
            self.stdout.write(f'  Jefes asignados: {asignados}')

        if sin_cargo_jefe > 0:
            self.stdout.write(self.style.WARNING(f'⊘ Sin cargo_jefe en jerarquía: {sin_cargo_jefe}'))

        if sin_empleados_en_cargo_jefe > 0:
            self.stdout.write(self.style.WARNING(f'⊘ Sin empleados en cargo jefe: {sin_empleados_en_cargo_jefe}'))

        if multiples_empleados_en_cargo_jefe > 0:
            self.stdout.write(self.style.WARNING(f'⊘ Múltiples jefes (requieren asignación manual): {multiples_empleados_en_cargo_jefe}'))

        if errores > 0:
            self.stdout.write(self.style.ERROR(f'✗ Errores: {errores}'))

        self.stdout.write('=' * 80)

        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠ Modo simulación: No se guardaron cambios'))
            self.stdout.write(self.style.NOTICE('Ejecuta sin --dry-run para aplicar los cambios'))
        elif asignados > 0:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Proceso completado exitosamente: {asignados} jefes asignados'))
        else:
            self.stdout.write(self.style.NOTICE('\n! No se realizaron asignaciones'))
