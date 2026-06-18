"""Seed inicial de centros de costo desde el catálogo Odoo (xlsx Construinmuniza)."""
from django.db import migrations


CENTROS = [
    # (cuenta_analitica, referencia, nombre)
    ('[1001] GERENCIA', '1001', 'GERENCIA'),
    ('[1002] FINANCIERO(TESORERÍA Y CONTABILIDAD)', '1002', 'FINANCIERO(TESORERÍA Y CONTABILIDAD)'),
    ('[1003] RRHH', '1003', 'RRHH'),
    ('[1004] SST', '1004', 'SST'),
    ('[1005] INVENTARIOS', '1005', 'INVENTARIOS'),
    ('[1006] TI (SISTEMAS)', '1006', 'TI (SISTEMAS)'),
    ('[1007] COMPRAS ADMINISTRACION', '1007', 'COMPRAS ADMINISTRACION'),
    ('[1008] SERVICIOS ADMINISTRACION', '1008', 'SERVICIOS ADMINISTRACION'),
    ('[1009] DIVERSOS DE ADMINISTRACION', '1009', 'DIVERSOS DE ADMINISTRACION'),
    ('[2001] DIRECCION COMERCIAL', '2001', 'DIRECCION COMERCIAL'),
    ('[2002] ASESORES COMERCIALES', '2002', 'ASESORES COMERCIALES'),
    ('[2003] DESPACHOS', '2003', 'DESPACHOS'),
    ('[2004] IMPUESTOS', '2004', 'IMPUESTOS'),
    ('[2005] COMPRAS DEL AREA COMERCIAL', '2005', 'COMPRAS DEL AREA COMERCIAL'),
    ('[2006] SERVICIOS DEL AREA COMERCIAL', '2006', 'SERVICIOS DEL AREA COMERCIAL'),
    ('[2007] ADMINISTRACIÓN/VENTAS', '2007', 'ADMINISTRACIÓN/VENTAS'),
    ('[2008] DIVERSOS DEL AREA COMERCIAL', '2008', 'DIVERSOS DEL AREA COMERCIAL'),
    ('[2009] MERCADEO', '2009', 'MERCADEO'),
    ('[2010] LOGISTICA DE ENTREGA', '2010', 'LOGISTICA DE ENTREGA'),
    ('[3001] ASERRIO (D)', '3001', 'ASERRIO (D)'),
    ('[3003] SECADO (D)', '3003', 'SECADO (D)'),
    ('[3005] CEPILLADO (D)', '3005', 'CEPILLADO (D)'),
    ('[3007] DIMENSIONADO (D)', '3007', 'DIMENSIONADO (D)'),
    ('[3009] TERMOTRADO (D)', '3009', 'TERMOTRADO (D)'),
    ('[3011] INMUNIZADO (D)', '3011', 'INMUNIZADO (D)'),
    ('[3013] LAMINADO (D)', '3013', 'LAMINADO (D)'),
    ('[3015] SUBPRODUCTOS (D)', '3015', 'SUBPRODUCTOS (D)'),
    ('[3019] FINGER (D)', '3019', 'FINGER (D)'),
    ('[3023] CARPINTERIA (D)', '3023', 'CARPINTERIA (D)'),
    ('[3025] CILINDRADO (D)', '3025', 'CILINDRADO (D)'),
    ('[3027] DESCORTEZADO (D)', '3027', 'DESCORTEZADO (D)'),
]


def crear_centros(apps, schema_editor):
    CentroCosto = apps.get_model('organizational', 'CentroCosto')
    for cuenta, ref, nombre in CENTROS:
        CentroCosto.objects.update_or_create(
            cuenta_analitica=cuenta,
            defaults={'referencia': ref, 'nombre': nombre, 'activo': True},
        )


def borrar_centros(apps, schema_editor):
    CentroCosto = apps.get_model('organizational', 'CentroCosto')
    cuentas = [c[0] for c in CENTROS]
    CentroCosto.objects.filter(cuenta_analitica__in=cuentas).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('organizational', '0004_alter_centrocosto_options_remove_centrocosto_sede_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_centros, borrar_centros),
    ]
