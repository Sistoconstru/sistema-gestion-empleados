"""DEFAULT a nivel de BD para las columnas NOT NULL agregadas recientemente.

Django guarda los `default=` solo del lado de Python: al agregar una columna
NOT NULL pone el default temporalmente para rellenar las filas existentes y
después lo quita (DROP DEFAULT). Eso deja la columna NOT NULL sin default.

El problema aparece cuando un proceso con código viejo (que todavía no conoce
la columna) hace un INSERT: Django omite la columna, Postgres no tiene default
que aplicar y el INSERT falla con «null value violates not-null constraint».
Pasa en cada rolling deploy, mientras conviven procesos viejos y nuevos, y
también en desarrollo cuando el runserver no se reinició.

Fijar el DEFAULT en la BD hace que esos INSERT incompletos funcionen. No
cambia el comportamiento del ORM: Django sigue mandando el valor explícito.
"""
from django.db import migrations


DEFAULTS = [
    ('delegacion_asistencia_permanente', 'false'),
    ('motivo_retiro', "''"),
    ('observacion_retiro', "''"),
    ('es_declarante', 'false'),
]


def _sql(accion):
    return '\n'.join(
        f'ALTER TABLE empleados ALTER COLUMN {col} {accion(valor)};'
        for col, valor in DEFAULTS
    )


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0051_empleado_es_declarante'),
    ]

    operations = [
        migrations.RunSQL(
            sql=_sql(lambda v: f'SET DEFAULT {v}'),
            reverse_sql=_sql(lambda v: 'DROP DEFAULT'),
        ),
    ]
