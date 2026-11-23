from django.contrib import admin
from django.utils.html import format_html

from .models import (
    DocumentoVehiculo, GastoVehiculo, ServicioIniciado, Vehiculo,
)


class DocumentoVehiculoInline(admin.TabularInline):
    model = DocumentoVehiculo
    extra = 0
    fields = ('tipo', 'numero', 'entidad', 'fecha_expedicion',
              'fecha_vencimiento', 'valor', 'aplica', 'archivo')
    ordering = ('tipo', '-fecha_vencimiento')
    show_change_link = True


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    """El maestro lo administra Odoo; aquí se consulta y se asigna conductor."""
    list_display = ('placa', 'marca', 'modelo', 'anio', 'conductor',
                    'estado_documentos', 'activo')
    list_filter = ('activo', 'marca')
    search_fields = ('placa', 'marca', 'modelo', 'odoo_id',
                     'conductor__nombres', 'conductor__apellidos',
                     'conductor__numero_documento')
    autocomplete_fields = ('conductor',)
    readonly_fields = ('id', 'odoo_id', 'fecha_creacion', 'fecha_actualizacion',
                       'fecha_sincronizacion')
    inlines = [DocumentoVehiculoInline]
    ordering = ('placa',)

    fieldsets = (
        ('Identificación', {
            'fields': ('id', 'odoo_id', 'placa', 'marca', 'modelo', 'anio'),
            'description': ('La placa, marca y modelo se refrescan desde Odoo. '
                            'Cambiarlas aquí no viaja de vuelta.'),
        }),
        ('Asignación', {'fields': ('conductor', 'activo')}),
        ('Sincronización', {
            'fields': ('fecha_sincronizacion', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def estado_documentos(self, obj):
        """Resumen de lo que está vencido o por vencer."""
        vencidos = [d for d in obj.documentos_vigentes()
                    if d.aplica and d.esta_vencido]
        proximos = [d for d in obj.documentos_vigentes()
                    if d.aplica and d.por_vencer]
        if vencidos:
            return format_html(
                '<span style="color:#b02a37;font-weight:bold;">⚠ {} vencido{}</span>',
                len(vencidos), 's' if len(vencidos) > 1 else '')
        if proximos:
            return format_html(
                '<span style="color:#997404;">⏳ {} por vencer</span>', len(proximos))
        if obj.documentos_vigentes():
            return format_html('<span style="color:#146c43;">✓ Al día</span>')
        return format_html('<span style="color:#6c757d;">Sin documentos</span>')
    estado_documentos.short_description = 'Documentos'


@admin.register(DocumentoVehiculo)
class DocumentoVehiculoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'tipo', 'numero', 'entidad',
                    'fecha_vencimiento', 'estado_coloreado', 'aplica')
    list_filter = ('tipo', 'aplica', 'fecha_vencimiento')
    search_fields = ('numero', 'entidad', 'vehiculo__placa')
    autocomplete_fields = ('vehiculo',)
    readonly_fields = ('id', 'registrado_por', 'fecha_creacion', 'fecha_actualizacion')
    date_hierarchy = 'fecha_vencimiento'
    ordering = ('-fecha_vencimiento',)

    fieldsets = (
        ('Documento', {
            'fields': ('id', 'vehiculo', 'tipo', 'numero', 'entidad', 'aplica'),
        }),
        ('Vigencia', {
            'fields': ('fecha_expedicion', 'fecha_vencimiento', 'valor'),
            'description': ('Si dejas el vencimiento vacío se calcula solo: SOAT y '
                            'tecnomecánica al año de la expedición, el impuesto '
                            'vehicular el 30 de junio y el rodamiento el 31 de diciembre.'),
        }),
        ('Soporte', {'fields': ('archivo', 'observaciones')}),
        ('Registro', {
            'fields': ('registrado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def estado_coloreado(self, obj):
        colores = {
            'vencido': ('#b02a37', '⚠'),
            'por_vencer': ('#997404', '⏳'),
            'vigente': ('#146c43', '✓'),
            'no_aplica': ('#6c757d', '—'),
            'sin_fecha': ('#6c757d', '?'),
        }
        color, icono = colores[obj.estado]
        dias = obj.dias_para_vencer
        extra = ''
        if obj.estado == 'vencido':
            extra = f' (hace {abs(dias)} días)'
        elif obj.estado == 'por_vencer':
            extra = f' (en {dias} días)'
        return format_html('<span style="color:{};">{} {}{}</span>',
                           color, icono, obj.estado_display, extra)
    estado_coloreado.short_description = 'Estado'

    def save_model(self, request, obj, form, change):
        if not obj.registrado_por_id:
            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(GastoVehiculo)
class GastoVehiculoAdmin(admin.ModelAdmin):
    """Los gastos se registran y revisan en el módulo; aquí solo se consultan."""
    list_display = ('fecha', 'vehiculo', 'conductor', 'tipo', 'monto',
                    'estado', 'cuenta_costo', 'quien_registro')
    list_filter = ('estado', 'tipo', 'responsable', 'fecha')
    search_fields = ('vehiculo__placa', 'conductor__nombres',
                     'conductor__apellidos', 'conductor__numero_documento',
                     'descripcion', 'servicio__ref')
    autocomplete_fields = ('vehiculo', 'conductor')
    readonly_fields = ('id', 'fecha_creacion', 'fecha_actualizacion',
                       'revisado_por', 'fecha_revision', 'registrado_por',
                       'servicio')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)

    def cuenta_costo(self, obj):
        return obj.cuenta_como_costo
    cuenta_costo.short_description = '¿Entra al costo?'
    cuenta_costo.boolean = True

    def quien_registro(self, obj):
        """El conductor mismo, o el coordinador que lo digitó por él."""
        if not obj.registrado_por_id:
            return '—'
        if obj.lo_registro_otro:
            nombre = (obj.registrado_por.get_full_name()
                      or obj.registrado_por.username)
            return format_html('<span title="Lo registró un tercero">👤 {}</span>',
                               nombre)
        return 'el conductor'
    quien_registro.short_description = 'Registrado por'


@admin.register(ServicioIniciado)
class ServicioIniciadoAdmin(admin.ModelAdmin):
    """Las salidas que marcan los conductores. Aquí solo se consultan."""
    list_display = ('iniciado_en', 'ref', 'vehiculo', 'conductor',
                    'entregado_en', 'novedad', 'estado_aviso', 'anulado')
    list_filter = ('conflicto_odoo', 'conflicto_odoo_entrega', 'novedad',
                   'sincronizado', 'entrega_sincronizada', 'tipo',
                   'iniciado_en')
    search_fields = ('ref', 'resumen', 'vehiculo__placa',
                     'conductor__nombres', 'conductor__apellidos',
                     'conductor__numero_documento')
    autocomplete_fields = ('vehiculo', 'conductor')
    readonly_fields = ('id', 'odoo_modelo', 'odoo_id', 'ref', 'tipo',
                       'resumen', 'fecha_creacion', 'fecha_sincronizacion',
                       'ultimo_error', 'fecha_sincronizacion_entrega',
                       'ultimo_error_entrega', 'anulado_en', 'anulado_por',
                       'duracion_texto')
    date_hierarchy = 'iniciado_en'
    ordering = ('-iniciado_en',)

    def estado_aviso(self, obj):
        """Los dos avisos en una columna: salida y, si la hubo, entrega.

        El rechazo se distingue del pendiente porque son cosas opuestas:
        uno se reintenta solo y el otro hay que ir a resolverlo.
        """
        def marca(ok, rechazado, error, nombre):
            if ok:
                return f'✓ {nombre}'
            if rechazado:
                return f'✗ {nombre} rechazada ({error[:60]})'
            return f'⏳ {nombre}' + (f' ({error[:40]})' if error else '')

        partes = [marca(obj.sincronizado, obj.conflicto_odoo,
                        obj.ultimo_error, 'salida')]
        if obj.esta_entregado:
            partes.append(marca(obj.entrega_sincronizada,
                                obj.conflicto_odoo_entrega,
                                obj.ultimo_error_entrega, 'entrega'))

        if obj.conflicto_odoo or obj.conflicto_odoo_entrega:
            color = '#b02a37'
        elif (not obj.sincronizado
              or (obj.esta_entregado and not obj.entrega_sincronizada)):
            color = '#997404'
        else:
            color = '#146c43'
        return format_html('<span style="color:{};">{}</span>',
                           color, ' · '.join(partes))
    estado_aviso.short_description = 'Aviso a Odoo'

    def anulado(self, obj):
        return not obj.esta_activo
    anulado.short_description = 'Anulado'
    anulado.boolean = True
