#!/bin/bash
# =============================================================================
# Script de Linux/Mac para actualizar la Polla Mundial automáticamente
# =============================================================================
# Este script debe ejecutarse cada 30 minutos durante el Mundial
# Configurar en crontab: */30 * * * * /ruta/proyecto/actualizar_polla_mundial.sh

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

echo "========================================"
echo "Actualización Polla Mundial - $(date)"
echo "========================================"

# Activar entorno virtual (ajusta la ruta si es diferente)
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
elif [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
else
    echo "ADVERTENCIA: No se encontró entorno virtual"
fi

# 1. Actualizar equipos TBD (por si se definieron nuevos clasificados)
echo ""
echo "[1/3] Actualizando equipos TBD..."
python manage.py actualizar_equipos_tbd

# 2. Actualizar resultados de partidos finalizados
echo ""
echo "[2/3] Actualizando resultados de partidos..."
python manage.py actualizar_resultados_mundial --verbose

# 3. Importar nuevos partidos (por si se agregaron partidos de fases siguientes)
echo ""
echo "[3/3] Verificando nuevos partidos..."
python manage.py importar_partidos_mundial --force

echo ""
echo "========================================"
echo "Actualización completada - $(date)"
echo "========================================"

# Registrar en log
mkdir -p logs
echo "$(date) - Actualización completada" >> logs/polla_mundial_updates.log

exit 0
