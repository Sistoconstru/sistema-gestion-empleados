
# =============================================================================
# apps/documents/management/commands/populate_document_types.py
# =============================================================================


from django.core.management.base import BaseCommand
from apps.documents.models import TipoDocumentoEmpleado, TipoDocumentoCargo
from apps.organizational.models import Cargo

class Command(BaseCommand):
    help = 'Poblar tipos de documentos iniciales'

    def handle(self, *args, **options):
        """Crear tipos de documentos según requerimientos"""
        
        # DOCUMENTOS OBLIGATORIOS
        documentos_obligatorios = [
            {
                'codigo': 'CEDULA',
                'nombre': 'Cédula de Ciudadanía',
                'descripcion': 'Documento de identidad (frente y reverso)',
                'obligatorio': True,
                'tiene_vencimiento': False,
                'formatos_permitidos': 'PDF,JPG,PNG',
                'tamaño_maximo_mb': 5,
                'requiere_aprobacion': True
            },
            {
                'codigo': 'EPS',
                'nombre': 'Certificado EPS',
                'descripcion': 'Certificado de afiliación a EPS vigente',
                'obligatorio': True,
                'tiene_vencimiento': True,
                'dias_notificacion_vencimiento': 30,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 5,
                'requiere_aprobacion': True
            },
            {
                'codigo': 'AFP',
                'nombre': 'Certificado AFP',
                'descripcion': 'Certificado de afiliación a AFP vigente',
                'obligatorio': True,
                'tiene_vencimiento': True,
                'dias_notificacion_vencimiento': 30,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 5,
                'requiere_aprobacion': True
            }
        ]
        
        # DOCUMENTOS OPCIONALES
        documentos_opcionales = [
            {
                'codigo': 'CERT_LABORAL',
                'nombre': 'Certificados Laborales',
                'descripcion': 'Mínimo 2 certificados laborales (recomendado)',
                'obligatorio': False,
                'tiene_vencimiento': False,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 10,
                'requiere_aprobacion': False
            },
            {
                'codigo': 'REF_PERSONAL',
                'nombre': 'Referencias Personales',
                'descripcion': 'Carta con información de contacto del referente',
                'obligatorio': False,
                'tiene_vencimiento': False,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 5,
                'requiere_aprobacion': False
            },
            {
                'codigo': 'CESANTIAS',
                'nombre': 'Certificado de Cesantías',
                'descripcion': 'Certificado de cesantías',
                'obligatorio': False,
                'tiene_vencimiento': False,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 5,
                'requiere_aprobacion': False
            },
            {
                'codigo': 'ESTUDIOS',
                'nombre': 'Certificados de Estudios',
                'descripcion': 'Diplomas, certificados académicos',
                'obligatorio': False,
                'tiene_vencimiento': False,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 10,
                'requiere_aprobacion': False
            }
        ]
        
        # DOCUMENTOS ESPECÍFICOS POR CARGO
        documentos_especificos = [
            {
                'codigo': 'LIC_CONDUCIR',
                'nombre': 'Licencia de Conducción',
                'descripcion': 'Solo para conductores',
                'obligatorio': False,  # Será obligatorio solo para conductores
                'tiene_vencimiento': True,
                'dias_notificacion_vencimiento': 30,
                'formatos_permitidos': 'PDF,JPG,PNG',
                'tamaño_maximo_mb': 5,
                'requiere_aprobacion': True,
                'cargos_requeridos': ['CONDUCTOR', 'MENSAJERO']  # Códigos de cargos
            },
            {
                'codigo': 'CERT_ALTURAS',
                'nombre': 'Certificado de Alturas',
                'descripcion': 'Certificado de trabajo en alturas',
                'obligatorio': False,  # Será obligatorio solo para ciertos cargos
                'tiene_vencimiento': True,
                'dias_notificacion_vencimiento': 30,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 5,
                'requiere_aprobacion': True,
                'cargos_requeridos': ['TECNICO', 'MANTENIMIENTO', 'CONSTRUCCION']
            }
        ]
        
        # DOCUMENTOS ADMINISTRATIVOS (Solo administrador)
        documentos_administrativos = [
            {
                'codigo': 'HOJA_VIDA',
                'nombre': 'Hoja de Vida',
                'descripcion': 'Hoja de vida formato estándar empresa',
                'obligatorio': False,
                'tiene_vencimiento': False,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 5,
                'requiere_aprobacion': False,
                'solo_administrador': True
            },
            {
                'codigo': 'CONTRATO',
                'nombre': 'Contrato Laboral',
                'descripcion': 'Contrato laboral firmado',
                'obligatorio': False,
                'tiene_vencimiento': False,
                'formatos_permitidos': 'PDF',
                'tamaño_maximo_mb': 10,
                'requiere_aprobacion': False,
                'solo_administrador': True
            }
        ]
        
        # Crear documentos obligatorios
        self.stdout.write(self.style.SUCCESS('Creando documentos obligatorios...'))
        for doc_data in documentos_obligatorios:
            doc, created = TipoDocumentoEmpleado.objects.get_or_create(
                codigo=doc_data['codigo'],
                defaults=doc_data
            )
            if created:
                self.stdout.write(f'✅ Creado: {doc.nombre}')
            else:
                self.stdout.write(f'⚡ Ya existe: {doc.nombre}')
        
        # Crear documentos opcionales
        self.stdout.write(self.style.SUCCESS('Creando documentos opcionales...'))
        for doc_data in documentos_opcionales:
            doc, created = TipoDocumentoEmpleado.objects.get_or_create(
                codigo=doc_data['codigo'],
                defaults=doc_data
            )
            if created:
                self.stdout.write(f'✅ Creado: {doc.nombre}')
            else:
                self.stdout.write(f'⚡ Ya existe: {doc.nombre}')
        
        # Crear documentos específicos por cargo
        self.stdout.write(self.style.SUCCESS('Creando documentos específicos por cargo...'))
        for doc_data in documentos_especificos:
            cargos_requeridos = doc_data.pop('cargos_requeridos', [])
            
            doc, created = TipoDocumentoEmpleado.objects.get_or_create(
                codigo=doc_data['codigo'],
                defaults=doc_data
            )
            
            if created:
                self.stdout.write(f'✅ Creado: {doc.nombre}')
            else:
                self.stdout.write(f'⚡ Ya existe: {doc.nombre}')
            
            # Asignar a cargos específicos
            for cargo_codigo in cargos_requeridos:
                try:
                    cargo = Cargo.objects.get(codigo=cargo_codigo)
                    relacion, created = TipoDocumentoCargo.objects.get_or_create(
                        tipo_documento=doc,
                        cargo=cargo
                    )
                    if created:
                        self.stdout.write(f'  🔗 Asignado a cargo: {cargo.nombre}')
                except Cargo.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️ Cargo {cargo_codigo} no encontrado')
                    )
        
        # Crear documentos administrativos
        self.stdout.write(self.style.SUCCESS('Creando documentos administrativos...'))
        for doc_data in documentos_administrativos:
            doc_data.pop('solo_administrador', None)  # Remover campo custom
            
            doc, created = TipoDocumentoEmpleado.objects.get_or_create(
                codigo=doc_data['codigo'],
                defaults=doc_data
            )
            if created:
                self.stdout.write(f'✅ Creado: {doc.nombre}')
            else:
                self.stdout.write(f'⚡ Ya existe: {doc.nombre}')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Tipos de documentos poblados exitosamente!')
        )