"""
Comando para diagnosticar el estado de una evaluación específica
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import AsignacionEvaluacion, PlanMejoraPredefinido
from apps.employees.models import Empleado


class Command(BaseCommand):
    help = 'Diagnostica el estado de evaluaciones de un empleado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nombre',
            type=str,
            help='Nombre o parte del nombre del empleado',
            default='Gaviria'
        )

    def handle(self, *args, **options):
        nombre = options['nombre']

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.WARNING(f"DIAGNÓSTICO DE EVALUACIONES - {nombre.upper()}"))
        self.stdout.write("=" * 80)

        # Buscar empleados por nombres o apellidos
        empleados = Empleado.objects.filter(
            nombres__icontains=nombre
        ) | Empleado.objects.filter(
            apellidos__icontains=nombre
        )

        self.stdout.write(f"\nEmpleados encontrados: {empleados.count()}\n")

        if empleados.count() == 0:
            self.stdout.write(self.style.ERROR(f"No se encontraron empleados con '{nombre}' en su nombre"))
            return

        for empleado in empleados:
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write(self.style.SUCCESS(f"EMPLEADO: {empleado.nombres} {empleado.apellidos}"))
            self.stdout.write(f"CC: {empleado.numero_documento}")
            self.stdout.write("=" * 80)

            # Buscar evaluaciones
            evaluaciones = AsignacionEvaluacion.objects.filter(
                empleado_evaluado=empleado
            ).select_related(
                'evaluacion__tipo_evaluacion',
                'aprobada_por'
            ).order_by('-fecha_asignacion')

            self.stdout.write(f"\nTotal de evaluaciones: {evaluaciones.count()}\n")

            for i, ev in enumerate(evaluaciones, 1):
                self.stdout.write(f"\n--- EVALUACIÓN #{i} ---")
                self.stdout.write(f"ID: {ev.id}")
                self.stdout.write(f"Tipo: {ev.evaluacion.tipo_evaluacion.nombre}")
                self.stdout.write(f"Periodo: {ev.periodo_evaluacion}")
                self.stdout.write(f"Fecha asignación: {ev.fecha_asignacion}")

                # CAMPOS CRÍTICOS
                self.stdout.write(self.style.WARNING(f"ESTADO: {ev.estado}"))
                self.stdout.write(self.style.WARNING(f"ESTADO APROBACIÓN: {ev.estado_aprobacion or 'NULL'}"))

                self.stdout.write(f"Aprobada por: {ev.aprobada_por.get_full_name() if ev.aprobada_por else 'N/A'}")
                self.stdout.write(f"Fecha aprobación: {ev.fecha_aprobacion or 'N/A'}")

                if ev.comentarios_aprobacion:
                    self.stdout.write(f"Comentarios RRHH: {ev.comentarios_aprobacion[:150]}")
                else:
                    self.stdout.write("Comentarios RRHH: Sin comentarios")

                # Verificar si tiene plan
                try:
                    plan = PlanMejoraPredefinido.objects.get(asignacion_evaluacion=ev)
                    self.stdout.write(self.style.SUCCESS("\n✓ TIENE PLAN DE MEJORA:"))
                    self.stdout.write(f"  - ID Plan: {plan.id}")
                    self.stdout.write(f"  - Estado Plan: {plan.estado}")
                    self.stdout.write(f"  - Aceptado por empleado: {plan.aceptado_por_empleado}")
                    self.stdout.write(f"  - Rechazado por empleado: {plan.rechazado_por_empleado}")
                except PlanMejoraPredefinido.DoesNotExist:
                    self.stdout.write(self.style.ERROR("\n✗ NO TIENE PLAN DE MEJORA"))

                # Análisis del problema
                if ev.estado_aprobacion == 'desaprobada' and ev.estado == 'completada':
                    self.stdout.write(self.style.ERROR(
                        "\n⚠ PROBLEMA DETECTADO: Estado='completada' pero estado_aprobacion='desaprobada'"
                    ))
                    self.stdout.write(self.style.ERROR(
                        "   DEBERÍA SER: estado='requiere_correccion'"
                    ))
                elif ev.estado_aprobacion == 'desaprobada' and ev.estado == 'finalizada':
                    self.stdout.write(self.style.ERROR(
                        "\n⚠ PROBLEMA DETECTADO: Estado='finalizada' pero estado_aprobacion='desaprobada'"
                    ))
                    self.stdout.write(self.style.ERROR(
                        "   DEBERÍA SER: estado='requiere_correccion'"
                    ))

                self.stdout.write("\n" + "-" * 40)

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("FIN DEL DIAGNÓSTICO"))
        self.stdout.write("=" * 80 + "\n")
