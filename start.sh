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

# Actualiza estados de evaluaciones existentes (solo primera vez)
# Actualiza evaluaciones completadas a 'finalizada' y desaprobadas a 'requiere_correccion'
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Actualizando estados de evaluaciones existentes..."
# python manage.py actualizar_estados_evaluaciones

# Popula datos iniciales de evaluaciones (estructura base)
# DESHABILITADO: Ya se ejecutó una vez, datos ya están en la base de datos
# python manage.py configurar_evaluaciones_iniciales

# Actualiza opciones con contenido del documento completo
# DESHABILITADO: Ya se ejecutó una vez, datos ya están en la base de datos
# python manage.py actualizar_opciones_documento

# Configura tipos de notificaciones para evaluaciones (solo primera vez)
# DESHABILITADO: Ya se ejecutó una vez, los tipos de notificación ya están creados
# python manage.py configurar_notificaciones_evaluaciones

# Genera notificaciones para evaluaciones existentes (solo primera vez)
# DESHABILITADO: Ya se ejecutó una vez, las notificaciones retroactivas ya están generadas
# python manage.py generar_notificaciones_evaluaciones_existentes

# Configura evaluaciones anuales de desempeño (solo primera vez)
# DESHABILITADO: Ya se ejecutó una vez, las 5 evaluaciones anuales ya están configuradas
# python manage.py configurar_evaluacion_afiladores
# python manage.py configurar_evaluacion_operarios_produccion
# python manage.py configurar_evaluacion_auxiliar_procesos
# python manage.py configurar_evaluacion_coordinadores_procesos
# python manage.py configurar_evaluacion_mantenimiento

# Configura evaluación de Servicios Generales (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Servicios Generales..."
# python manage.py configurar_evaluacion_servicios_generales

# Configura evaluación de Auxiliares Administrativos (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Auxiliares Administrativos..."
# python manage.py configurar_evaluacion_auxiliares_administrativos

# Generar seguimientos bimensuales faltantes (ejecutar una vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Generando seguimientos bimensuales faltantes..."
# python manage.py generar_seguimientos_faltantes --ejecutar

# Configura evaluación de Auxiliar de Tesorería (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Auxiliar de Tesorería..."
# python manage.py configurar_evaluacion_auxiliar_tesoreria

# Configura evaluación de Auxiliar de RRHH (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Auxiliar de RRHH..."
# python manage.py configurar_evaluacion_auxiliar_rrhh

# Configura evaluación de Auxiliar Contable (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Auxiliar Contable..."
# python manage.py configurar_evaluacion_auxiliar_contable

# Configura evaluación de Analista Contable (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Analista Contable..."
# python manage.py configurar_evaluacion_analista_contable

# Configura evaluación de Asesor Comercial (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Asesor Comercial..."
# python manage.py configurar_evaluacion_asesor_comercial

# Configura evaluación de Directores (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Directores..."
# python manage.py configurar_evaluacion_director

# Configura evaluación de Analista de Inventario (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Analista de Inventario..."
# python manage.py configurar_evaluacion_analista_inventario

# Configura evaluación de Mensajero (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Mensajero..."
# python manage.py configurar_evaluacion_mensajero

# Configura evaluación de Auxiliar de SST (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Auxiliar de SST..."
# python manage.py configurar_evaluacion_auxiliar_sst

# Configura evaluación de Coordinador Administrativo (solo primera vez)
# DESHABILITADO: Ya se ejecutó exitosamente en producción
# echo "⚙️  Configurando evaluación de Coordinador Administrativo..."
# python manage.py configurar_evaluacion_coordinador_administrativo

# TEMPORAL: Importar partidos del Mundial 2026 (REMOVER DESPUÉS DE PRIMERA EJECUCIÓN)
echo "⚽ Importando partidos del Mundial 2026..."
python manage.py importar_partidos_mundial --season=2026 || echo "⚠️ Ya existen partidos o error en importación"

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
