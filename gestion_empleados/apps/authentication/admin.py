

# Register your models here.
# =============================================================================
# apps/authentication/admin.py
# =============================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Rol, ModuloSistema, Permiso, RolPermiso, UsuarioRol

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'fecha_creacion')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'fecha_creacion')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'telefono')
    ordering = ('username',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('telefono', 'ultimo_acceso')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('email', 'first_name', 'last_name', 'telefono')
        }),
    )

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'nivel_jerarquico', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'nivel_jerarquico')
    search_fields = ('nombre', 'codigo', 'descripcion')
    ordering = ('nivel_jerarquico', 'nombre')

@admin.register(ModuloSistema)
class ModuloSistemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'codigo')

@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'modulo', 'accion')
    list_filter = ('modulo', 'accion')
    search_fields = ('nombre', 'codigo')

@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
    list_display = ('rol', 'permiso', 'fecha_asignacion', 'asignado_por')
    list_filter = ('fecha_asignacion',)

@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'activo', 'fecha_asignacion', 'fecha_expiracion')
    list_filter = ('activo', 'fecha_asignacion', 'fecha_expiracion')
    search_fields = ('usuario__username', 'rol__nombre')