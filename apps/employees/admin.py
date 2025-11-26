# =============================================================================
# apps/employees/admin.py
# =============================================================================

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Q
from datetime import date

from .models import (
    TipoDocumento, Escolaridad, EstadoEmpleado, 
    Empleado, HistorialCargo
)

# Registro del modelo TipoDocumento en el admin de Django
@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'longitud_minima', 'longitud_maxima', 'activo')
    list_filter = ('activo', 'requiere_numero')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)

# Registro del modelo Escolaridad en el admin de Django
@admin.register(Escolaridad)
class EscolaridadAdmin(admin.ModelAdmin):
    list_display = ('orden', 'codigo', 'nivel')
    ordering = ('orden',)

# Registro del modelo EstadoEmpleado en el admin de Django
@admin.register(EstadoEmpleado)
class EstadoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'permite_acceso_sistema')
    list_filter = ('permite_acceso_sistema',)
    ordering = ('codigo',)

# Inline para historial de cargos en el formulario de empleado
class HistorialCargoInline(admin.TabularInline):
    model = HistorialCargo
    fk_name = 'empleado'  # Especificar cuál ForeignKey usar (hay dos: empleado y jefe_directo)
    extra = 1
    fields = ('cargo', 'jefe_directo', 'fecha_inicio', 'fecha_fin', 'activo', 'motivo_cambio')
    readonly_fields = ('fecha_creacion', 'creado_por')
    ordering = ('-fecha_inicio',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cargo__area', 'jefe_directo')

# Registro del modelo Empleado en el admin de Django
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_completo', 'numero_documento', 'get_cargo_actual', 
        'get_area_actual', 'estado', 'fecha_ingreso', 'get_estado_badge'
    )
    list_filter = (
        'estado', 'tipo_documento', 'sede', 'fecha_ingreso',
        'historialcargo__cargo__area', 'escolaridad'
    )
    search_fields = (
        'nombres', 'apellidos', 'numero_documento', 
        'correo_electronico', 'telefono_contacto'
    )
    readonly_fields = (
        'id', 'fecha_creacion', 'fecha_actualizacion', 'creado_por',
        'get_antiguedad', 'get_cargo_actual', 'get_area_actual',
    )
    exclude = ('usuario',)  # Excluir campo usuario del formulario
    
    # Agrupación de campos en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'tipo_documento', 'numero_documento', 'nombres', 'apellidos',
                'telefono_contacto', 'fecha_ingreso', 'sede', 'estado'
            )
        }),
        ('Información Personal', {
            'fields': (
                'fecha_nacimiento', 'ciudad_nacimiento', 'escolaridad',
                'contacto_emergencia_nombre', 'contacto_emergencia_telefono',
                'correo_electronico'
            ),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': (
                'id', 'fecha_creacion', 'fecha_actualizacion', 
                'creado_por', 'get_antiguedad', 'get_cargo_actual', 'get_area_actual'
            ),
            'classes': ('collapse',),
            'description': 'El usuario se crea automáticamente al guardar el empleado .'
        }),
    )
    
    inlines = [HistorialCargoInline]
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'fecha_ingreso'
    ordering = ('apellidos', 'nombres')
    actions = ['marcar_como_activo', 'marcar_como_inactivo', 'export_to_excel']
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'tipo_documento', 'estado', 'sede', 'escolaridad', 'usuario', 'creado_por'
        ).prefetch_related('historialcargo_set__cargo__area')
    
    def get_cargo_actual(self, obj):
        """Obtener cargo actual del empleado"""
        try:
            historial = obj.historialcargo_set.filter(activo=True).first()
            if historial:
                return historial.cargo.nombre
            return "Sin cargo asignado"
        except:
            return "Sin cargo asignado"
    get_cargo_actual.short_description = 'Cargo Actual'
    get_cargo_actual.admin_order_field = 'historialcargo__cargo__nombre'
    
    def get_area_actual(self, obj):
        """Obtener área actual del empleado"""
        try:
            historial = obj.historialcargo_set.filter(activo=True).first()
            if historial:
                return historial.cargo.area.nombre
            return "Sin área asignada"
        except:
            return "Sin área asignada"
    get_area_actual.short_description = 'Área Actual'
    get_area_actual.admin_order_field = 'historialcargo__cargo__area__nombre'
    
    def get_estado_badge(self, obj):
        """Badge colorido para el estado"""
        colors = {
            'ACTIVO': '#28a745',
            'PRUEBA': '#ffc107',
            'INACTIVO': '#dc3545',
            'VACACIONES': '#17a2b8'
        }
        color = colors.get(obj.estado.codigo, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.estado.nombre
        )
    get_estado_badge.short_description = 'Estado'
    get_estado_badge.admin_order_field = 'estado__nombre'
    
    def get_antiguedad(self, obj):
        """Calcular antigüedad en la empresa"""
        if obj.fecha_ingreso:
            delta = date.today() - obj.fecha_ingreso
            years = delta.days // 365
            months = (delta.days % 365) // 30
            
            if years > 0:
                return f"{years} año{'s' if years > 1 else ''}, {months} mes{'es' if months != 1 else ''}"
            elif months > 0:
                return f"{months} mes{'es' if months != 1 else ''}"
            else:
                return f"{delta.days} días"
        return "No disponible"
    get_antiguedad.short_description = 'Antigüedad'
    
    def save_model(self, request, obj, form, change):
        """Configurar usuario creador y generar credenciales automáticamente"""
        if not change:  # Solo en creación
            obj.creado_por = request.user
            
            # Generar usuario del sistema automáticamente
            if not obj.usuario:
                obj.usuario = self.crear_usuario_automatico(request, obj)
        
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Guardar el formset de historial de cargos con usuario creador"""
        instances = formset.save(commit=False)
        
        for instance in instances:
            if isinstance(instance, HistorialCargo):
                if not instance.creado_por_id:
                    instance.creado_por = request.user
                instance.save()
        
        formset.save_m2m()
    
    def crear_usuario_automatico(self, request, empleado):
        """Mostrar mensaje si el usuario ya existe, pero no crear usuario aquí (solo lo hace el signal)."""
        from django.contrib import messages
        if empleado.usuario:
            messages.success(
                request,
                f"✅ Usuario ya existe para el empleado:\n"
                f"👤 Usuario: {empleado.usuario.username}\n"
                f" Email: {empleado.usuario.email}\n"
                f"(Comunicar estas credenciales al empleado)"
            )
            return empleado.usuario
        else:
            messages.warning(
                request,
                f"⚠️ No se pudo crear usuario automáticamente."
            )
            return None
    
    # Acciones personalizadas
    def marcar_como_activo(self, request, queryset):
        """Marcar empleados seleccionados como activos"""
        try:
            estado_activo = EstadoEmpleado.objects.get(codigo='ACTIVO')
            updated = queryset.update(estado=estado_activo)
            self.message_user(
                request, 
                f'{updated} empleado(s) marcado(s) como activo(s).'
            )
        except EstadoEmpleado.DoesNotExist:
            self.message_user(
                request, 
                'Error: No existe el estado ACTIVO en el sistema.',
                level='ERROR'
            )
    marcar_como_activo.short_description = "Marcar como activo"
    
    def marcar_como_inactivo(self, request, queryset):
        """Marcar empleados seleccionados como inactivos"""
        try:
            estado_inactivo = EstadoEmpleado.objects.get(codigo='INACTIVO')
            updated = queryset.update(estado=estado_inactivo)
            self.message_user(
                request, 
                f'{updated} empleado(s) marcado(s) como inactivo(s).'
            )
        except EstadoEmpleado.DoesNotExist:
            self.message_user(
                request, 
                'Error: No existe el estado INACTIVO en el sistema.',
                level='ERROR'
            )
    marcar_como_inactivo.short_description = "Marcar como inactivo"
    
    def export_to_excel(self, request, queryset):
        """Exportar empleados seleccionados a Excel"""
        from django.http import HttpResponse
        import openpyxl
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Empleados'
        
        # Encabezados
        headers = [
            'Documento', 'Nombres', 'Apellidos', 'Email', 'Teléfono',
            'Cargo', 'Área', 'Estado', 'Fecha Ingreso'
        ]
        
        for col, header in enumerate(headers, 1):
            worksheet.cell(row=1, column=col, value=header)
        
        # Datos
        for row, empleado in enumerate(queryset.select_related('estado').prefetch_related('historialcargo_set__cargo__area'), 2):
            cargo_actual = empleado.historialcargo_set.filter(activo=True).first()
            
            worksheet.cell(row=row, column=1, value=empleado.numero_documento)
            worksheet.cell(row=row, column=2, value=empleado.nombres)
            worksheet.cell(row=row, column=3, value=empleado.apellidos)
            worksheet.cell(row=row, column=4, value=empleado.correo_electronico)
            worksheet.cell(row=row, column=5, value=empleado.telefono_contacto)
            worksheet.cell(row=row, column=6, value=cargo_actual.cargo.nombre if cargo_actual else '')
            worksheet.cell(row=row, column=7, value=cargo_actual.cargo.area.nombre if cargo_actual else '')
            worksheet.cell(row=row, column=8, value=empleado.estado.nombre)
            worksheet.cell(row=row, column=9, value=empleado.fecha_ingreso.strftime('%d/%m/%Y'))
        
        # Respuesta
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="empleados_seleccionados.xlsx"'
        
        workbook.save(response)
        return response
    export_to_excel.short_description = "Exportar a Excel"

# Registro del modelo HistorialCargo en el admin de Django
@admin.register(HistorialCargo)
class HistorialCargoAdmin(admin.ModelAdmin):
    list_display = (
        'empleado', 'cargo', 'get_area', 'jefe_directo',
        'fecha_inicio', 'fecha_fin', 'activo', 'get_duracion'
    )
    list_filter = (
        'activo', 'cargo__area', 'fecha_inicio', 'fecha_fin'
    )
    search_fields = (
        'empleado__nombres', 'empleado__apellidos',
        'cargo__nombre', 'cargo__area__nombre',
        'jefe_directo__nombres', 'jefe_directo__apellidos'
    )
    date_hierarchy = 'fecha_inicio'
    ordering = ('-fecha_inicio',)
    
    fieldsets = (
        ('Información del Cargo', {
            'fields': ('empleado', 'cargo', 'jefe_directo', 'fecha_inicio', 'fecha_fin', 'activo')
        }),
        ('Detalles', {
            'fields': ('salario', 'motivo_cambio', 'observaciones'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'creado_por'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'creado_por', 'get_duracion')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'empleado', 'cargo__area', 'creado_por', 'jefe_directo'
        )
    
    def get_area(self, obj):
        """Obtener área del cargo"""
        return obj.cargo.area.nombre if obj.cargo and obj.cargo.area else ''
    get_area.short_description = 'Área'
    get_area.admin_order_field = 'cargo__area__nombre'
    
    def get_duracion(self, obj):
        """Calcular duración en el cargo"""
        inicio = obj.fecha_inicio
        fin = obj.fecha_fin or date.today()
        
        if inicio:
            delta = fin - inicio
            years = delta.days // 365
            months = (delta.days % 365) // 30
            days = delta.days % 30
            
            partes = []
            if years > 0:
                partes.append(f"{years} año{'s' if years > 1 else ''}")
            if months > 0:
                partes.append(f"{months} mes{'es' if months != 1 else ''}")
            if not partes and days > 0:
                partes.append(f"{days} días")
            
            duracion = ", ".join(partes) if partes else "Menos de un mes"
            
            if obj.activo:
                return f"{duracion} (actual)"
            return duracion
        
        return "No disponible"
    get_duracion.short_description = 'Duración'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

# Personalización del sitio admin
admin.site.site_header = "RRHH Pro - Administración"
admin.site.site_title = "RRHH Pro Admin"
admin.site.index_title = "Panel de Administración"