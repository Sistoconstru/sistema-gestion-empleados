#!/bin/bash
# =============================================================================
# Script de cron para actualizar Polla Mundial automáticamente
# Se ejecuta cada 30 minutos entre 1 PM y 1 AM (optimización de API)
# =============================================================================

echo "=================================="
echo "Iniciando actualización Polla Mundial - $(date)"
echo "=================================="

# 1. Actualizar equipos TBD (equipos pendientes de definir en eliminatorias)
echo ""
echo "[1/3] Actualizando equipos TBD..."
python manage.py actualizar_equipos_tbd || echo "⚠️ Error actualizando TBD (continuando...)"

# 2. Actualizar resultados de partidos finalizados y calcular puntos
echo ""
echo "[2/3] Actualizando resultados de partidos..."
python manage.py actualizar_resultados_mundial --verbose

# 3. Importar nuevos partidos (por si se agregan más partidos durante el torneo)
echo ""
echo "[3/3] Verificando nuevos partidos..."
python manage.py importar_partidos_mundial --season=2026 --force || echo "⚠️ Sin nuevos partidos"

echo ""
echo "=================================="
echo "Actualización completada - $(date)"
echo "=================================="
