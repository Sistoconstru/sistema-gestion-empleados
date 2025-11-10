"""
Management command para probar la subida de insignias a S3
Uso: python manage.py test_insignias_upload
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from apps.recognition.models import TipoInsignia

class Command(BaseCommand):
    help = 'Probar subida de archivos de insignias a S3'

    def handle(self, *args, **options):
        self.stdout.write("=== Test de subida de insignias ===")
        
        # 1. Verificar configuración actual
        self.stdout.write(f"Storage backend: {default_storage.__class__}")
        
        # 2. Probar subida directa a carpeta insignias
        try:
            test_content = ContentFile(b"Test insignia file")
            test_path = "insignias/test_file.txt"
            
            saved_name = default_storage.save(test_path, test_content)
            self.stdout.write(self.style.SUCCESS(f"✅ Archivo subido: {saved_name}"))
            
            # Verificar URL
            url = default_storage.url(saved_name)
            self.stdout.write(f"📄 URL: {url}")
            
            # Limpiar
            default_storage.delete(saved_name)
            self.stdout.write("🗑️ Archivo de prueba eliminado")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
        
        # 3. Verificar insignias existentes
        insignias_con_imagen = TipoInsignia.objects.exclude(icono='')
        self.stdout.write(f"📊 Insignias con imagen en DB: {insignias_con_imagen.count()}")
        
        for insignia in insignias_con_imagen[:5]:  # Solo primeras 5
            self.stdout.write(f"🏆 {insignia.nombre}: {insignia.icono.name}")
            try:
                url = insignia.icono.url
                self.stdout.write(f"   URL: {url}")
            except Exception as e:
                self.stdout.write(f"   ❌ Error URL: {e}")