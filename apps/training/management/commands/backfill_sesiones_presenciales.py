"""Repara inscripciones a capacitaciones presenciales/mixtas que quedaron
con `sesion=None`. Aplica la misma lógica de auto-asignación que ahora
usa `InscripcionCapacitacion.save()`, pero sobre inscripciones ya existentes
creadas antes del fix.

Adicionalmente crea plantillas de certificado stub (opcional con --stub-plantillas)
para capacitaciones marcadas como emite_certificado=True que aún no la tengan.
Los textos son genéricos: RRHH después ajusta títulos, firmas, logo, fondo.

Por defecto es dry-run; pasar --apply para escribir.
"""
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError

from apps.training.models import (
    Capacitacion, CertificadoPlantilla, InscripcionCapacitacion, SesionCapacitacion,
)


class Command(BaseCommand):
    help = (
        'Asigna la próxima sesión disponible a inscripciones huérfanas de '
        'capacitaciones presenciales/mixtas. Deduplica primero por (empleado, '
        'capacitación) conservando la más antigua. Opcional: crea plantillas '
        'de certificado stub.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Aplica los cambios. Sin esta bandera solo muestra lo que haría.',
        )
        parser.add_argument(
            '--stub-plantillas',
            action='store_true',
            help='Crea plantillas de certificado stub para cursos que emiten cert sin plantilla.',
        )

    def handle(self, *args, **options):
        aplicar = options['apply']
        crear_stubs = options['stub_plantillas']
        modo = 'APLICAR' if aplicar else 'DRY-RUN'
        self.stdout.write(self.style.HTTP_INFO(f'Modo: {modo}'))
        self.stdout.write('=' * 60)

        total_asignadas = 0
        total_borradas = 0
        total_sin_sesion = 0
        total_plantillas = 0

        with transaction.atomic():
            for cap in Capacitacion.objects.filter(modalidad__in=('presencial', 'mixta')):
                sin_sesion = list(
                    InscripcionCapacitacion.objects.filter(capacitacion=cap, sesion__isnull=True)
                    .select_related('empleado')
                    .order_by('empleado_id', 'fecha_inscripcion')
                )
                if not sin_sesion:
                    continue

                # Dedup por empleado — conservar la más antigua
                vistos = set()
                a_asignar = []
                a_borrar = []
                for insc in sin_sesion:
                    if insc.empleado_id in vistos:
                        a_borrar.append(insc)
                    else:
                        vistos.add(insc.empleado_id)
                        a_asignar.append(insc)

                proxima = SesionCapacitacion.proxima_disponible_para(cap)
                self.stdout.write('')
                self.stdout.write(
                    f'  {cap.codigo} → sesión objetivo: '
                    f'{proxima.codigo if proxima else "(NINGUNA disponible)"}'
                )

                for insc in a_borrar:
                    self.stdout.write(self.style.WARNING(
                        f'    ✗ duplicado: {insc.empleado.nombre_completo} [{insc.estado}]'
                    ))
                    if aplicar:
                        insc.delete()
                    total_borradas += 1

                if proxima is None:
                    self.stdout.write(self.style.WARNING(
                        f'    (sin sesión disponible — {len(a_asignar)} quedan sin asignar)'
                    ))
                    total_sin_sesion += len(a_asignar)
                    continue

                for insc in a_asignar:
                    self.stdout.write(
                        f'    ✓ {insc.empleado.nombre_completo} [{insc.estado}] → {proxima.codigo}'
                    )
                    if aplicar:
                        insc.sesion = proxima
                        try:
                            insc.save(update_fields=['sesion'])
                        except IntegrityError as e:
                            self.stdout.write(self.style.ERROR(f'      IntegrityError: {e}'))
                            continue
                    total_asignadas += 1

            if crear_stubs:
                self.stdout.write('')
                self.stdout.write('Plantillas de certificado stub:')
                for cap in Capacitacion.objects.filter(emite_certificado=True, activa=True):
                    if hasattr(cap, 'plantilla_certificado') and cap.plantilla_certificado is not None:
                        continue
                    self.stdout.write(f'  + {cap.codigo} — {cap.nombre}')
                    if aplicar:
                        CertificadoPlantilla.objects.create(
                            capacitacion=cap,
                            titulo_certificado=f'Certificado de aprobación — {cap.nombre}',
                            texto_superior='Se otorga el presente certificado a:',
                            texto_inferior=f'Por haber cumplido satisfactoriamente el curso "{cap.nombre}".',
                            nombre_responsable='Responsable de la capacitación',
                            cargo_responsable='Encargado',
                            nombre_rrhh='',
                            cargo_rrhh='Director de Recursos Humanos',
                            incluir_calificacion=True,
                            incluir_duracion=True,
                            nota_minima_certificado=cap.puntaje_aprobacion,
                        )
                    total_plantillas += 1

            if not aplicar:
                transaction.set_rollback(True)

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'{modo}: {total_asignadas} asignadas · {total_borradas} duplicados · '
            f'{total_sin_sesion} sin sesión disponible · {total_plantillas} plantillas stub'
        ))
        if not aplicar:
            self.stdout.write(self.style.WARNING(
                'Nada persistido. Vuelve a correr con --apply para aplicar.'
            ))
