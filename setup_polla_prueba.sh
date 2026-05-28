#!/bin/bash
# =============================================================================
# Setup Rápido - Polla Mundial PROVISIONAL (Gratis)
# =============================================================================
# Este script configura el sistema con datos del Mundial 2022 para pruebas
# NO REQUIERE SUSCRIPCIÓN NI API PREMIUM

echo "============================================================"
echo "   SETUP: Polla Mundial 2026 - Versión Provisional (GRATIS)"
echo "============================================================"
echo ""
echo "Este script va a:"
echo "  1. Aplicar migraciones a la base de datos"
echo "  2. Importar partidos del Mundial 2022 Qatar"
echo "  3. Actualizar resultados históricos"
echo "  4. Crear predicciones de prueba"
echo ""
echo "Tiempo estimado: 2-3 minutos"
echo "============================================================"
echo ""
read -p "Presiona ENTER para continuar..."

# Cambiar al directorio del script
cd "$(dirname "$0")"

# Activar entorno virtual
echo "[1/4] Activando entorno virtual..."
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
    echo "   ✓ OK - Entorno virtual activado"
elif [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "   ✓ OK - Entorno virtual activado"
else
    echo "   ⚠️  ADVERTENCIA: No se encontró entorno virtual, continuando..."
fi
echo ""

# Aplicar migraciones
echo "[2/4] Aplicando migraciones..."
python manage.py makemigrations employees
python manage.py migrate employees
echo "   ✓ OK - Migraciones aplicadas"
echo ""

# Importar partidos del Mundial 2022
echo "[3/4] Importando partidos del Mundial 2022 (API gratuita)..."
echo "   Esto puede tardar 1-2 minutos..."
python manage.py importar_partidos_mundial --season=2022
echo ""

# Actualizar resultados
echo "[4/4] Actualizando resultados de partidos..."
python manage.py actualizar_resultados_mundial
echo ""

echo "============================================================"
echo "   ✅ SETUP COMPLETADO EXITOSAMENTE"
echo "============================================================"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Iniciar servidor Django:"
echo "   python manage.py runserver"
echo ""
echo "2. Acceder a la Polla Mundial:"
echo "   http://localhost:8000/empleados/polla-mundial/"
echo ""
echo "3. Ver admin:"
echo "   http://localhost:8000/admin/employees/partidomundial/"
echo ""
echo "4. (Opcional) Crear predicciones de prueba:"
echo "   python manage.py shell < scripts/crear_predicciones_prueba.py"
echo ""
echo "============================================================"
echo ""
echo "NOTA: Estos son datos del Mundial 2022 para PRUEBAS."
echo "      Cuando llegue el Mundial 2026, sigue la guía:"
echo "      GUIA_API_PREMIUM_MUNDIAL.md"
echo ""
echo "============================================================"
