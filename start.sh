#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE=config.settings.production

# Verificar que DATABASE_URL esté configurada
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurada."
    echo "Por favor configura la variable DATABASE_URL en Railway:"
    echo "1. Ve a tu proyecto en Railway"
    echo "2. Settings → Variables"
    echo "3. Asegúrate de que el servicio PostgreSQL está conectado"
    echo "4. La variable debe estar disponible como: \${{ Postgres.DATABASE_URL }}"
    exit 1
fi

# Ejecuta migraciones
python manage.py migrate

# Popula datos iniciales de evaluaciones (estructura base)
python manage.py configurar_evaluaciones_iniciales

# Configura evaluación específica de período de prueba
python manage.py configurar_evaluacion_periodo_prueba

# Actualiza opciones con contenido del documento completo
python manage.py actualizar_opciones_documento

# Recopila archivos estáticos (incluye dependencias locales)
python manage.py collectstatic --noinput

# Crea un superusuario si no existe

# Inicia Gunicorn en modo producción
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
