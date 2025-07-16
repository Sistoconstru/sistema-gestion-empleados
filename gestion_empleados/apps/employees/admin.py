# =============================================================================
# apps/employees/admin.py - CON CREACIÓN AUTOMÁTICA DE USUARIOS
# =============================================================================

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib import messages
from .models import TipoDocumento, Escolaridad, EstadoEmpleado, Empleado, HistorialCargo

Usuario = get_user_model()

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'requiere_numero', 'longitud_minima', 'longitud_maxima', 'activo')
    list_filter = ('activo', 'requiere_numero')
    search_fields = ('codigo', 'nombre')

@admin.register(Escolaridad)
class EscolaridadAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nivel', 'orden')
    ordering = ('orden',)

@admin.register(EstadoEmpleado)
class EstadoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'permite_acceso_sistema')
    list_filter = ('permite_acceso_sistema',)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'nombres', 'apellidos', 'usuario_username', 'sede', 'estado', 'fecha_ingreso')
    list_filter = ('estado', 'sede', 'escolaridad', 'fecha_ingreso')
    search_fields = ('numero_documento', 'nombres', 'apellidos', 'usuario__username')
    
    fieldsets = (
        ('Identificación', {
            'fields': ('tipo_documento', 'numero_documento')
        }),
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'fecha_nacimiento', 'ciudad_nacimiento', 'escolaridad')
        }),
        ('Información Laboral', {
            'fields': ('fecha_ingreso', 'sede', 'estado')
        }),
        ('Contacto', {
            'fields': ('telefono_contacto', 'correo_electronico')
        }),
        ('Contacto de Emergencia', {
            'fields': ('contacto_emergencia_nombre', 'contacto_emergencia_telefono')
        }),
    )
    
    # EXCLUIR el campo usuario del formulario (se crea automáticamente)
    exclude = ('usuario', 'creado_por')
    
    def usuario_username(self, obj):
        """Mostrar el username del usuario asociado"""
        return obj.usuario.username if obj.usuario else 'Sin usuario'
    usuario_username.short_description = 'Usuario del Sistema'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'usuario', 'tipo_documento', 'sede', 'estado', 'escolaridad'
        )
    
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        """Crear usuario automáticamente al crear empleado"""
        if not change:  # Solo en creación, no en edición
            try:
                # Preparar datos del usuario
                username = self.generar_username(obj.nombres)
                password = obj.numero_documento
                email = obj.correo_electronico or f"{username}@empresa.com"
                
                # Crear el usuario
                usuario = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=obj.nombres,
                    last_name=obj.apellidos,
                    telefono=obj.telefono_contacto
                )
                
                # Asignar el usuario al empleado
                obj.usuario = usuario
                obj.creado_por = request.user
                
                # Mensaje de éxito
                messages.success(request, 
                    f'Usuario creado exitosamente:\n'
                    f'Username: {username}\n'
                    f'Password: {password}\n'
                    f'(El empleado debe cambiar la contraseña en el primer acceso)'
                )
                
            except Exception as e:
                messages.error(request, f'Error al crear usuario: {str(e)}')
                return
        
        super().save_model(request, obj, form, change)
    
    def generar_username(self, nombres):
        """Generar username único basado en el nombre"""
        # Limpiar el nombre (quitar espacios y caracteres especiales)
        base_username = nombres.lower().replace(' ', '').replace('ñ', 'n')
        
        # Eliminar acentos
        import unicodedata
        base_username = unicodedata.normalize('NFD', base_username)
        base_username = ''.join(c for c in base_username if unicodedata.category(c) != 'Mn')
        
        # Verificar si el username ya existe
        username = base_username
        counter = 1
        
        while Usuario.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username

@admin.register(HistorialCargo)
class HistorialCargoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'cargo', 'fecha_inicio', 'fecha_fin', 'salario', 'activo')
    list_filter = ('activo', 'fecha_inicio', 'cargo__area')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'cargo__nombre')
    
    exclude = ('creado_por',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)