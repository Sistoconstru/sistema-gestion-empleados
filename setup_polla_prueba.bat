@echo off
REM =============================================================================
REM Setup Rápido - Polla Mundial PROVISIONAL (Gratis)
REM =============================================================================
REM Este script configura el sistema con datos del Mundial 2022 para pruebas
REM NO REQUIERE SUSCRIPCIÓN NI API PREMIUM

echo ============================================================
echo    SETUP: Polla Mundial 2026 - Version Provisional (GRATIS)
echo ============================================================
echo.
echo Este script va a:
echo   1. Aplicar migraciones a la base de datos
echo   2. Importar partidos del Mundial 2022 Qatar
echo   3. Actualizar resultados historicos
echo   4. Crear predicciones de prueba
echo.
echo Tiempo estimado: 2-3 minutos
echo ============================================================
echo.

pause

cd /d %~dp0

REM Activar entorno virtual
echo [1/4] Activando entorno virtual...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo    OK - Entorno virtual activado
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo    OK - Entorno virtual activado
) else (
    echo    ADVERTENCIA: No se encontro entorno virtual, continuando...
)
echo.

REM Aplicar migraciones
echo [2/4] Aplicando migraciones...
python manage.py makemigrations employees
python manage.py migrate employees
echo    OK - Migraciones aplicadas
echo.

REM Importar partidos del Mundial 2022
echo [3/4] Importando partidos del Mundial 2022 (API gratuita)...
echo    Esto puede tardar 1-2 minutos...
python manage.py importar_partidos_mundial --season=2022
echo.

REM Actualizar resultados
echo [4/4] Actualizando resultados de partidos...
python manage.py actualizar_resultados_mundial
echo.

echo ============================================================
echo    SETUP COMPLETADO EXITOSAMENTE
echo ============================================================
echo.
echo Proximos pasos:
echo.
echo 1. Iniciar servidor Django:
echo    python manage.py runserver
echo.
echo 2. Acceder a la Polla Mundial:
echo    http://localhost:8000/empleados/polla-mundial/
echo.
echo 3. Ver admin:
echo    http://localhost:8000/admin/employees/partidomundial/
echo.
echo 4. (Opcional) Crear predicciones de prueba:
echo    python manage.py shell ^< scripts\crear_predicciones_prueba.py
echo.
echo ============================================================
echo.
echo NOTA: Estos son datos del Mundial 2022 para PRUEBAS.
echo       Cuando llegue el Mundial 2026, sigue la guia:
echo       GUIA_API_PREMIUM_MUNDIAL.md
echo.
echo ============================================================

pause
