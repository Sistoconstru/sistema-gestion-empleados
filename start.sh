#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE=config.settings.production

# Instalar fuentes TrueType necesarias para renderizado de texto
echo "📦 Instalando fuentes TrueType..."
apt-get update -qq && apt-get install -y -qq fonts-liberation fonts-dejavu-core > /dev/null 2>&1 || echo "⚠️  No se pudieron instalar fuentes (puede que ya estén instaladas)"

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
# DESHABILITADO: Ya se ejecutó una vez, datos ya están en la base de datos
# python manage.py configurar_evaluaciones_iniciales

# Actualiza opciones con contenido del documento completo
# DESHABILITADO: Ya se ejecutó una vez, datos ya están en la base de datos
# python manage.py actualizar_opciones_documento

# Configura tipos de notificaciones para evaluaciones (solo primera vez)
echo "📧 Configurando tipos de notificaciones..."
python manage.py configurar_notificaciones_evaluaciones

# Genera notificaciones para evaluaciones existentes (solo primera vez)
echo "🔔 Generando notificaciones para evaluaciones existentes..."
python manage.py generar_notificaciones_evaluaciones_existentes

# Recopila archivos estáticos (incluye dependencias locales)
python manage.py collectstatic --noinput

# Crea un superusuario si no existe

# Inicia el scheduler de tareas automáticas en segundo plano (modo daemon)
echo "🔄 Iniciando scheduler de evaluaciones automáticas..."
python manage.py start_scheduler --daemon > /dev/null 2>&1 &
SCHEDULER_PID=$!
echo "✅ Scheduler iniciado (PID: $SCHEDULER_PID)"
echo "  - 02:00 AM: Asignar evaluaciones de período de prueba"
echo "  - 02:15 AM: Activar empleados completados"

# Inicia Gunicorn en modo producción
echo "🚀 Iniciando Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
