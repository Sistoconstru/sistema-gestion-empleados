# apps/recognition/management/commands/crear_tipos_actividad.py

from django.core.management.base import BaseCommand
from apps.recognition.models import TipoActividad


class Command(BaseCommand):
    help = 'Crea los tipos de actividad predefinidos para el sistema automático'

    def handle(self, *args, **options):
        tipos_actividad = [
            {
                'codigo': 'CAP_COMPLETADA',
                'nombre': 'Capacitación Completada',
                'descripcion': 'Puntos otorgados automáticamente al completar una capacitación',
                'puntos_base': 10,
                'multiplicador_complejidad': 1.0,
                'activo': True
            },
            {
                'codigo': 'EVAL_EXCELENTE',
                'nombre': 'Evaluación Excelente',
                'descripcion': 'Puntos por obtener calificación excelente en evaluación',
                'puntos_base': 25,
                'multiplicador_complejidad': 1.0,
                'activo': True
            },
            {
                'codigo': 'EVAL_BUENA',
                'nombre': 'Evaluación Buena',
                'descripcion': 'Puntos por obtener calificación buena en evaluación',
                'puntos_base': 15,
                'multiplicador_complejidad': 1.0,
                'activo': True
            },
            {
                'codigo': 'EVAL_SATISFACTORIA',
                'nombre': 'Evaluación Satisfactoria',
                'descripcion': 'Puntos por obtener calificación satisfactoria en evaluación',
                'puntos_base': 10,
                'multiplicador_complejidad': 1.0,
                'activo': True
            },
            {
                'codigo': 'ENCUESTA_RESP',
                'nombre': 'Encuesta Respondida',
                'descripcion': 'Puntos por responder encuestas del sistema',
                'puntos_base': 5,
                'multiplicador_complejidad': 1.0,
                'activo': True
            },
            {
                'codigo': 'OBJETIVO_CUMPLIDO',
                'nombre': 'Objetivo Cumplido',
                'descripcion': 'Puntos por cumplir objetivos establecidos',
                'puntos_base': 20,
                'multiplicador_complejidad': 1.0,
                'activo': True
            },
            {
                'codigo': 'MANUAL_ADMIN',
                'nombre': 'Asignación Manual',
                'descripcion': 'Puntos asignados manualmente por administrador',
                'puntos_base': 0,  # Los puntos se especifican manualmente
                'multiplicador_complejidad': 1.0,
                'activo': True
            },
            {
                'codigo': 'RECONOC_PARES',
                'nombre': 'Reconocimiento de Pares',
                'descripcion': 'Puntos por recibir reconocimiento de compañeros',
                'puntos_base': 8,
                'multiplicador_complejidad': 1.0,
                'activo': True
            }
        ]

        for tipo_data in tipos_actividad:
            tipo_actividad, created = TipoActividad.objects.get_or_create(
                codigo=tipo_data['codigo'],
                defaults=tipo_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Creado: {tipo_actividad.nombre}')
                )
            else:
                # Actualizar campos si ya existe
                for key, value in tipo_data.items():
                    if key != 'codigo':  # No actualizar el código
                        setattr(tipo_actividad, key, value)
                tipo_actividad.save()
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Actualizado: {tipo_actividad.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n🎯 Tipos de actividad configurados correctamente!')
        )
        self.stdout.write(
            'Los administradores pueden modificar los puntos desde el admin de Django.'
        )