from django.core.management.base import BaseCommand
from apps.authentication.models import Rol

class Command(BaseCommand):
    help = 'Crear roles básicos del sistema SIGHU'

    def handle(self, *args, **options):
        roles = [
            {
                'codigo': 'ADMIN', 
                'nombre': 'Administrador',
                'nivel': 1,
                'descripcion': 'Acceso completo al sistema, gestiona todo'
            },
            {
                'codigo': 'RRHH', 
                'nombre': 'Recursos Humanos',
                'nivel': 2,
                'descripcion': 'Gestiona empleados, evaluaciones y procesos de RRHH'
            },
            {
                'codigo': 'DIR', 
                'nombre': 'Director',
                'nivel': 2,
                'descripcion': 'Dirige áreas, evalúa coordinadores, reportes de área'
            },
            {
                'codigo': 'COORD', 
                'nombre': 'Coordinador',
                'nivel': 3,
                'descripcion': 'Coordina equipos, evalúa colaboradores, reportes de equipo'
            },
            {
                'codigo': 'COLAB', 
                'nombre': 'Colaborador',
                'nivel': 4,
                'descripcion': 'Empleado base, ejecuta tareas, se evalúa y es evaluado'
            }
        ]
        
        self.stdout.write(self.style.SUCCESS('🚀 Creando roles del sistema SIGHU...'))
        
        for rol_data in roles:
            rol, created = Rol.objects.get_or_create(
                codigo=rol_data['codigo'],
                defaults={
                    'nombre': rol_data['nombre'],
                    'nivel_jerarquico': rol_data['nivel'],
                    'descripcion': rol_data['descripcion'],
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Rol creado: {rol.nombre} (Nivel {rol.nivel_jerarquico})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Rol ya existe: {rol.nombre}')
                )
        
        self.stdout.write(self.style.SUCCESS('\n🎯 Roles del sistema creados exitosamente!'))
        self.stdout.write('📋 Próximo paso: Asignar roles a los cargos en el admin')