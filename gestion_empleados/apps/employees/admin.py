# =============================================================================
# apps/employees/admin.py - CON CREACIÓN AUTOMÁTICA DE USUARIOS
# =============================================================================
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib import messages
from .models import TipoDocumento, Escolaridad, EstadoEmpleado, Empleado, HistorialCargo
from .forms import EmpleadoForm

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
    form = EmpleadoForm
    list_display = ('numero_documento', 'nombre_completo', 'usuario_username', 'cargo_actual', 'rol_actual', 'sede', 'estado')
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
            'fields': ('cargo_inicial', 'fecha_ingreso', 'sede', 'estado')
        }),
        ('Contacto', {
            'fields': ('telefono_contacto', 'correo_electronico')
        }),
        ('Contacto de Emergencia', {
            'fields': ('contacto_emergencia_nombre', 'contacto_emergencia_telefono')
        }),
    )
    
    exclude = ('usuario', 'creado_por')
    
    def usuario_username(self, obj):
        """Mostrar el username del usuario asociado"""
        return obj.usuario.username if obj.usuario else 'Sin usuario'
    usuario_username.short_description = 'Usuario'
    
    def cargo_actual(self, obj):
        """Mostrar el cargo actual del empleado"""
        historial = obj.historialcargo_set.filter(activo=True).first()
        if historial:
            return f"{historial.cargo.nombre} ({historial.cargo.area.nombre})"
        return 'Sin cargo asignado'
    cargo_actual.short_description = 'Cargo Actual'
    
    def rol_actual(self, obj):
        """Mostrar el rol actual del empleado"""
        usuario_rol = obj.usuario.usuariorol_set.filter(activo=True).first() if obj.usuario else None
        if usuario_rol:
            return f"{usuario_rol.rol.nombre} (Nivel {usuario_rol.rol.nivel_jerarquico})"
        return 'Sin rol asignado'
    rol_actual.short_description = 'Rol Actual'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'usuario', 'tipo_documento', 'sede', 'estado', 'escolaridad'
        ).prefetch_related('historialcargo_set', 'usuario__usuariorol_set')
    
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        """Crear usuario y asignar rol automáticamente"""
        if not change:  # Solo en creación
            try:
                # 1. Crear usuario automáticamente
                username = self.generar_username(obj.nombres)
                password = obj.numero_documento
                email = obj.correo_electronico or f"{username}@empresa.com"
                
                usuario = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=obj.nombres,
                    last_name=obj.apellidos,
                    telefono=obj.telefono_contacto
                )
                
                obj.usuario = usuario
                obj.creado_por = request.user
                
                # 2. Guardar el empleado primero
                super().save_model(request, obj, form, change)
                
                # 3. Crear historial de cargo
                cargo_inicial = form.cleaned_data.get('cargo_inicial')
                if cargo_inicial:
                    self.crear_historial_cargo(obj, cargo_inicial, request.user)
                    
                    # 4. Asignar rol automático según cargo
                    if cargo_inicial.rol_automatico:
                        self.asignar_rol_empleado(obj, cargo_inicial.rol_automatico, request.user)
                        rol_info = f"Rol asignado: {cargo_inicial.rol_automatico.nombre}"
                    else:
                        rol_info = "⚠️ Cargo sin rol definido - asignar manualmente"
                else:
                    rol_info = "⚠️ Sin cargo asignado"
                
                # 5. Mensaje de éxito
                messages.success(request, 
                    f'✅ Empleado creado exitosamente:\n'
                    f'👤 Usuario: {username}\n'
                    f'🔑 Contraseña: {password}\n'
                    f'💼 Cargo: {cargo_inicial.nombre if cargo_inicial else "Sin asignar"}\n'
                    f'🎯 {rol_info}'
                )
                
            except Exception as e:
                messages.error(request, f'❌ Error al crear empleado: {str(e)}')
                return
        else:
            super().save_model(request, obj, form, change)
    
    def crear_historial_cargo(self, empleado, cargo, creado_por):
        """Crear historial de cargo para el empleado"""
        HistorialCargo.objects.create(
            empleado=empleado,
            cargo=cargo,
            fecha_inicio=empleado.fecha_ingreso,
            activo=True,
            creado_por=creado_por
        )
    
    def asignar_rol_empleado(self, empleado, rol, asignado_por):
        """Asignar rol al empleado"""
        from apps.authentication.models import UsuarioRol
        
        # Desactivar roles anteriores
        UsuarioRol.objects.filter(usuario=empleado.usuario, activo=True).update(activo=False)
        
        # Asignar nuevo rol
        UsuarioRol.objects.create(
            usuario=empleado.usuario,
            rol=rol,
            asignado_por=asignado_por,
            activo=True
        )
    
    def generar_username(self, nombres):
        """Generar username único basado en el nombre"""
        import unicodedata
        
        # Limpiar el nombre
        base_username = nombres.lower().replace(' ', '').replace('ñ', 'n')
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

