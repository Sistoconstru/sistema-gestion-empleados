Elimina la migración 0007_ciudad_departamento_alter_empleado_ciudad_nacimiento_and_more.py manualmente.

Luego ejecuta:
python manage.py makemigrations employees
python manage.py migrate employees

Esto limpiará el historial y permitirá que la base de datos quede alineada con el modelo actual (solo ciudad_nacimiento_text).

Cuando todo esté migrado y validado, podrás agregar el campo ForeignKey y migrar los datos manualmente.
