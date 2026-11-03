# =============================================================================
# apps/documents/admin.py
# =============================================================================

from django import forms
from django.contrib import admin
from django.utils import timezone

from .models import AnexoDocumento, DocumentoEmpleado, TipoDocumentoCargo, TipoDocumentoEmpleado, VersionDocumento


class TipoDocumentoEmpleadoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumentoEmpleado
        fields = '__all__'

    def clean_obligatorio(self):
        """Un tipo asignado a cargos lo exige su cargo. Marcarlo además como
        obligatorio general se lo exigía a todos: así quedaron alturas y
        licencia de conducir, faltándole a 273 de 274 empleados."""
        obligatorio = self.cleaned_data['obligatorio']
        if obligatorio and self.instance.pk and TipoDocumentoCargo.objects.filter(tipo_documento=self.instance).exists():
            raise forms.ValidationError(
                'Este tipo está asignado a cargos y ya es obligatorio para ellos. '
                'Marcarlo aquí lo exigiría a todos los empleados.'
            )
        return obligatorio


@admin.register(TipoDocumentoEmpleado)
class TipoDocumentoEmpleadoAdmin(admin.ModelAdmin):
    form = TipoDocumentoEmpleadoForm
    list_display = ('codigo', 'nombre', 'obligatorio', 'tiene_vencimiento', 'requiere_aprobacion', 'admite_anexos', 'activo')
    list_filter = ('obligatorio', 'tiene_vencimiento', 'requiere_aprobacion', 'admite_anexos', 'activo')
    search_fields = ('codigo', 'nombre')


@admin.register(TipoDocumentoCargo)
class TipoDocumentoCargoAdmin(admin.ModelAdmin):
    list_display = ('tipo_documento', 'cargo')


class AnexoDocumentoInline(admin.TabularInline):
    model = AnexoDocumento
    extra = 0
    fields = ('tipo', 'fecha_vigencia', 'descripcion', 'archivo', 'cargado_por', 'fecha_carga')
    readonly_fields = ('cargado_por', 'fecha_carga')


class VersionDocumentoInline(admin.TabularInline):
    """Historial: solo lectura. Se alimenta al actualizar el documento."""
    model = VersionDocumento
    extra = 0
    can_delete = False
    fields = ('version', 'archivo', 'estado_aprobacion', 'fecha_carga', 'reemplazada_en', 'reemplazada_por', 'motivo')
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(DocumentoEmpleado)
class DocumentoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo_documento', 'nombre_archivo', 'estado_aprobacion', 'version', 'fecha_carga')
    list_filter = ('estado_aprobacion', 'tipo_documento', 'fecha_carga')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'empleado__numero_documento', 'nombre_archivo')
    inlines = [AnexoDocumentoInline, VersionDocumentoInline]

    fieldsets = (
        ('Información del Documento', {
            'fields': ('empleado', 'tipo_documento', 'nombre_archivo', 'archivo')
        }),
        ('Fechas', {
            'fields': ('fecha_documento', 'fecha_vencimiento')
        }),
        ('Aprobación', {
            'fields': ('estado_aprobacion', 'observaciones', 'motivo_rechazo')
        }),
    )
    exclude = ('cargado_por', 'aprobado_por')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cargado_por = request.user
        # Aprobar o rechazar desde aquí no dejaba rastro de quién ni cuándo.
        if 'estado_aprobacion' in form.changed_data:
            ahora = timezone.now()
            if obj.estado_aprobacion == 'aprobado':
                obj.aprobado_por, obj.fecha_aprobacion = request.user, ahora
                obj.rechazado_por, obj.fecha_rechazo = None, None
            elif obj.estado_aprobacion == 'rechazado':
                obj.rechazado_por, obj.fecha_rechazo = request.user, ahora
                obj.aprobado_por, obj.fecha_aprobacion = None, None
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        for anexo in formset.save(commit=False):
            if isinstance(anexo, AnexoDocumento) and not anexo.cargado_por_id:
                anexo.cargado_por = request.user
                anexo.nombre_archivo = anexo.nombre_archivo or anexo.archivo.name.rsplit('/', 1)[-1]
            anexo.save()
        for borrado in formset.deleted_objects:
            borrado.delete()
        formset.save_m2m()
