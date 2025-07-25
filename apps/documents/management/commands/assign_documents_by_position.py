# =============================================================================
# apps/documents/management/commands/assign_documents_by_position.py 
# COMANDO PARA ASIGNAR DOCUMENTOS SEGÚN CARGO
# =============================================================================

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.documents.models import TipoDocumentoEmpleado, TipoDocumentoCargo
from apps.employees.models import Empleado
from apps.organizational.models import Cargo

class Command(BaseCommand):
    help = 'Asignar automáticamente documentos requeridos según cargo del empleado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empleado-id',
            type=str,
            help='ID específico del empleado a procesar',
        )
        parser.add_argument(
            '--cargo-codigo',
            type=str,
            help='Código específico del cargo a procesar',
        )

    def handle(self, *args, **options):
        empleado_id = options.get('empleado_id')
        cargo_codigo = options.get('cargo_codigo')
        
        self.stdout.write(self.style.SUCCESS('🔄 Iniciando asignación de documentos por cargo...'))
        
        try:
            with transaction.atomic():
                if empleado_id:
                    # Procesar empleado específico
                    empleado = Empleado.objects.get(pk=empleado_id)
                    self.procesar_empleado(empleado)
                    
                elif cargo_codigo:
                    # Procesar todos los empleados de un cargo específico
                    cargo = Cargo.objects.get(codigo=cargo_codigo)
                    empleados = Empleado.objects.filter(
                        historialcargo__cargo=cargo,
                        historialcargo__activo=True
                    )
                    
                    for empleado in empleados:
                        self.procesar_empleado(empleado)
                        
                else:
                    # Procesar todos los empleados activos
                    empleados = Empleado.objects.filter(
                        historialcargo__activo=True
                    ).distinct()
                    
                    total = empleados.count()
                    procesados = 0
                    
                    for empleado in empleados:
                        try:
                            self.procesar_empleado(empleado)
                            procesados += 1
                            
                            if procesados % 10 == 0:
                                self.stdout.write(f'✅ Procesados: {procesados}/{total}')
                                
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'❌ Error con {empleado.nombre_completo}: {str(e)}')
                            )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'🎉 Proceso completado: {procesados}/{total} empleados procesados')
                    )
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error general: {str(e)}'))

    def procesar_empleado(self, empleado):
        """Procesar documentos requeridos para un empleado específico"""
        # Obtener cargo actual
        historial_actual = empleado.historialcargo_set.filter(activo=True).first()
        if not historial_actual:
            self.stdout.write(
                self.style.WARNING(f'⚠️ {empleado.nombre_completo}: Sin cargo activo')
            )
            return
        
        cargo = historial_actual.cargo
        
        # Obtener documentos específicos del cargo
        documentos_cargo = TipoDocumentoEmpleado.objects.filter(
            tipodocumentocargo__cargo=cargo,
            activo=True
        )
        
        if not documentos_cargo.exists():
            self.stdout.write(f'ℹ️ {empleado.nombre_completo} ({cargo.nombre}): Sin documentos específicos')
            return
        
        # Verificar cuáles faltan
        from apps.documents.models import DocumentoEmpleado
        docs_existentes = DocumentoEmpleado.objects.filter(
            empleado=empleado
        ).values_list('tipo_documento', flat=True)
        
        docs_faltantes = documentos_cargo.exclude(id__in=docs_existentes)
        
        if docs_faltantes.exists():
            self.stdout.write(
                f'📋 {empleado.nombre_completo} ({cargo.nombre}): '
                f'{docs_faltantes.count()} documentos requeridos por cargo'
            )
            
            for doc_tipo in docs_faltantes:
                self.stdout.write(f'   • {doc_tipo.nombre}')
        else:
            self.stdout.write(f'✅ {empleado.nombre_completo}: Todos los documentos del cargo están completos')
