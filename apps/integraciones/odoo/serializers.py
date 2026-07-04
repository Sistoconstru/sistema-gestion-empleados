from rest_framework import serializers
from rest_framework.fields import DateTimeField as _DRFDateTimeField


_dt_iso = _DRFDateTimeField()


TIPO_DOCUMENTO_DIAN = {
    'CED': '13',
    'TI': '12',
    'CEX': '22',
    'PASP': '41',
}


class OdooEmpleadoSerializer(serializers.Serializer):
    """Serializa un Empleado en el contrato §3.4 de docs/INTEGRACION_ODOO.md."""

    sighu_uuid = serializers.UUIDField(source='id')
    tipo_documento = serializers.SerializerMethodField()
    numero_documento = serializers.CharField()
    nombres = serializers.CharField()
    apellidos = serializers.CharField()
    nombre_completo = serializers.CharField()
    fecha_nacimiento = serializers.DateField()
    ciudad_nacimiento = serializers.SerializerMethodField()
    correo_electronico = serializers.CharField()
    telefono_contacto = serializers.CharField()
    direccion = serializers.CharField()
    fecha_ingreso = serializers.DateField()
    estado = serializers.SerializerMethodField()
    sede = serializers.SerializerMethodField()
    escolaridad = serializers.SerializerMethodField()
    contacto_emergencia = serializers.SerializerMethodField()
    cargo_actual = serializers.SerializerMethodField()
    centro_costo = serializers.SerializerMethodField()
    fecha_actualizacion = serializers.SerializerMethodField()

    def get_tipo_documento(self, obj):
        tipo = obj.tipo_documento
        return {
            'codigo_sighu': tipo.codigo,
            'codigo_dian': TIPO_DOCUMENTO_DIAN.get(tipo.codigo),
            'nombre': tipo.nombre,
        }

    def get_ciudad_nacimiento(self, obj):
        return obj.ciudad_nacimiento.nombre if obj.ciudad_nacimiento else None

    def get_estado(self, obj):
        return {'codigo': obj.estado.codigo, 'nombre': obj.estado.nombre}

    def get_sede(self, obj):
        return {'codigo': obj.sede.codigo, 'nombre': obj.sede.nombre}

    def get_escolaridad(self, obj):
        return obj.escolaridad.nivel if obj.escolaridad else None

    def get_contacto_emergencia(self, obj):
        return {
            'nombre': obj.contacto_emergencia_nombre or None,
            'telefono': obj.contacto_emergencia_telefono or None,
        }

    def get_cargo_actual(self, obj):
        historial = obj.historialcargo_set.filter(activo=True).select_related(
            'cargo', 'cargo__area', 'jefe_directo'
        ).first()
        if not historial:
            return None
        cargo = historial.cargo
        return {
            'codigo': cargo.codigo,
            'nombre': cargo.nombre,
            'area': cargo.area.nombre if cargo.area_id else None,
            'salario': str(historial.salario) if historial.salario is not None else None,
            'fecha_inicio_cargo': historial.fecha_inicio.isoformat() if historial.fecha_inicio else None,
            'jefe_directo_uuid': str(historial.jefe_directo_id) if historial.jefe_directo_id else None,
        }

    def get_centro_costo(self, obj):
        """Centro de costo del empleado. La llave de matching contra Odoo es `referencia`
        (= `account.analytic.account.code`). `cuenta_analitica` es la etiqueta Odoo
        "[CODE] NOMBRE" tal cual aparece en el catálogo del cliente.
        """
        cc = obj.centro_costo
        if not cc:
            return None
        return {
            'referencia': cc.referencia,
            'cuenta_analitica': cc.cuenta_analitica,
            'nombre': cc.nombre,
        }

    def get_fecha_actualizacion(self, obj):
        """MAX(empleado.fecha_actualizacion, historial_activo.fecha_actualizacion) — §3.4 doc.

        Se devuelve como string ISO 8601 (usando el formato DRF, con 'Z' para UTC)
        para que `.data` sea JSON-serializable desde `requests.post(json=...)` sin
        depender del renderer de DRF.
        """
        empleado_fecha = obj.fecha_actualizacion
        historial = obj.historialcargo_set.filter(activo=True).order_by('-fecha_actualizacion').first()
        if historial and historial.fecha_actualizacion > empleado_fecha:
            empleado_fecha = historial.fecha_actualizacion
        return _dt_iso.to_representation(empleado_fecha)
