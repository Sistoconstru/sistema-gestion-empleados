"""
Comando para verificar qué empleados activos tienen o no jefe directo asignado
Útil para diagnosticar problemas antes de asignar evaluaciones

Uso:
    python manage.py verificar_jefes_directos
    python manage.py verificar_jefes_directos --sin-jefe  # Solo los que no tienen jefe
    python manage.py verificar_jefes_directos --cargo OPERARIO  # Filtrar por cargo
"""
from django.core.management.base import BaseCommand
from apps.employees.models import Empleado, HistorialCargo
from apps.organizational.models import Cargo
from django.db.models import Count


class Command(BaseCommand):
    help = 'Verifica qué empleados activos tienen jefe directo asignado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sin-jefe',
            action='store_true',
            help='Mostrar solo empleados SIN jefe directo asignado'
        )
        parser.add_argument(
            '--cargo',
            type=str,
            help='Filtrar por código o nombre de cargo',
            required=False
        )
        parser.add_argument(
            '--area',
            type=str,
            help='Filtrar por nombre de área',
            required=False
        )

    def handle(self, *args, **options):
        solo_sin_jefe = options['sin_jefe']
        cargo_filtro = options.get('cargo')
        area_filtro = options.get('area')

        self.stdout.write('='*80)
        self.stdout.write(self.style.WARNING('VERIFICACIÓN DE JEFES DIRECTOS'))
        self.stdout.write('='*80)

        # Obtener empleados activos con historial de cargo activo
        query = HistorialCargo.objects.filter(
            empleado__estado__codigo='999',  # ACTIVO
            activo=True
        ).select_related(
            'empleado',
            'cargo',
            'cargo__area',
            'jefe_directo'
        ).order_by('cargo__area__nombre', 'cargo__nombre', 'empleado__apellidos')

        # Aplicar filtros
        if cargo_filtro:
            query = query.filter(
                cargo__codigo__icontains=cargo_filtro
            ) | query.filter(
                cargo__nombre__icontains=cargo_filtro
            )

        if area_filtro:
            query = query.filter(cargo__area__nombre__icontains=area_filtro)

        total = query.count()
        self.stdout.write(f'\nEmpleados activos encontrados: {total}\n')

        # Contadores
        con_jefe = 0
        sin_jefe = 0
        sin_cargo_jefe = 0

        area_actual = None
        cargo_actual = None

        for historial in query:
            empleado = historial.empleado
            cargo = historial.cargo
            jefe = historial.jefe_directo

            # Agrupar por área y cargo
            if area_actual != cargo.area.nombre:
                area_actual = cargo.area.nombre
                self.stdout.write(f'\n{"="*80}')
                self.stdout.write(self.style.SUCCESS(f'ÁREA: {area_actual}'))
                self.stdout.write(f'{"="*80}')

            if cargo_actual != cargo.nombre:
                cargo_actual = cargo.nombre
                cargo_jefe_texto = cargo.cargo_jefe.nombre if cargo.cargo_jefe else 'N/A'
                self.stdout.write(f'\n  Cargo: {cargo.nombre} (Jefe esperado: {cargo_jefe_texto})')
                self.stdout.write(f'  {"-"*76}')

            # Determinar estado
            if jefe:
                con_jefe += 1
                if not solo_sin_jefe:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    ✓ {empleado.nombre_completo:<40} → {jefe.nombre_completo}'
                        )
                    )
            else:
                sin_jefe += 1
                if not cargo.cargo_jefe:
                    sin_cargo_jefe += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'    ⊘ {empleado.nombre_completo:<40} → SIN JEFE '
                            f'(El cargo no tiene cargo_jefe definido)'
                        )
                    )
                else:
                    # Verificar cuántos empleados hay en el cargo jefe
                    jefes_disponibles = HistorialCargo.objects.filter(
                        cargo=cargo.cargo_jefe,
                        activo=True
                    ).select_related('empleado')

                    cantidad_jefes = jefes_disponibles.count()

                    if cantidad_jefes == 0:
                        self.stdout.write(
                            self.style.ERROR(
                                f'    ✗ {empleado.nombre_completo:<40} → SIN JEFE '
                                f'(No hay empleados activos en "{cargo.cargo_jefe.nombre}")'
                            )
                        )
                    elif cantidad_jefes == 1:
                        jefe_disponible = jefes_disponibles.first().empleado
                        self.stdout.write(
                            self.style.WARNING(
                                f'    ! {empleado.nombre_completo:<40} → SIN JEFE ASIGNADO '
                                f'(Podría ser: {jefe_disponible.nombre_completo})'
                            )
                        )
                    else:
                        jefes_nombres = ', '.join([h.empleado.nombre_completo for h in jefes_disponibles[:2]])
                        if cantidad_jefes > 2:
                            jefes_nombres += f' y {cantidad_jefes - 2} más'
                        self.stdout.write(
                            self.style.WARNING(
                                f'    ! {empleado.nombre_completo:<40} → SIN JEFE ASIGNADO '
                                f'(Hay {cantidad_jefes} opciones: {jefes_nombres}) - REQUIERE ASIGNACIÓN MANUAL'
                            )
                        )

        # Resumen final
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('RESUMEN'))
        self.stdout.write('='*80)
        self.stdout.write(f'Total empleados activos: {total}')
        self.stdout.write(f'  ✓ Con jefe directo asignado: {con_jefe} ({con_jefe*100//total if total > 0 else 0}%)')
        self.stdout.write(f'  ✗ Sin jefe directo asignado: {sin_jefe} ({sin_jefe*100//total if total > 0 else 0}%)')
        if sin_cargo_jefe > 0:
            self.stdout.write(f'  ⊘ Sin cargo_jefe en jerarquía: {sin_cargo_jefe}')

        self.stdout.write('\n' + '='*80)

        if sin_jefe > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ ATENCIÓN: Hay {sin_jefe} empleados sin jefe directo asignado.'
                )
            )
            self.stdout.write(
                self.style.NOTICE(
                    'Estos empleados NO recibirán evaluaciones automáticas hasta que se les asigne un jefe.'
                )
            )
            self.stdout.write(
                self.style.NOTICE(
                    '\nPara asignar jefes automáticamente (solo cuando hay 1 opción):'
                )
            )
            self.stdout.write('  python manage.py asignar_jefes_automaticamente')
            self.stdout.write(
                self.style.NOTICE(
                    '\nPara los casos con múltiples opciones, debe asignarlos manualmente desde el admin.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ Todos los empleados tienen jefe directo asignado.'
                )
            )
