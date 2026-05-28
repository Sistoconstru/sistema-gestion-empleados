@echo off
REM =============================================================================
REM Script de Windows para actualizar la Polla Mundial automáticamente
REM =============================================================================
REM Este script debe ejecutarse cada 30 minutos durante el Mundial
REM Configurar en: Programador de Tareas de Windows

cd /d %~dp0

echo ========================================
echo Actualizacion Polla Mundial - %date% %time%
echo ========================================

REM Activar entorno virtual (ajusta la ruta si es diferente)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo ADVERTENCIA: No se encontro entorno virtual
)

REM 1. Actualizar equipos TBD (por si se definieron nuevos clasificados)
echo.
echo [1/3] Actualizando equipos TBD...
python manage.py actualizar_equipos_tbd

REM 2. Actualizar resultados de partidos finalizados
echo.
echo [2/3] Actualizando resultados de partidos...
python manage.py actualizar_resultados_mundial --verbose

REM 3. Importar nuevos partidos (por si se agregaron partidos de fases siguientes)
echo.
echo [3/3] Verificando nuevos partidos...
python manage.py importar_partidos_mundial --force

echo.
echo ========================================
echo Actualizacion completada - %date% %time%
echo ========================================

REM Registrar en log
echo %date% %time% - Actualizacion completada >> logs\polla_mundial_updates.log

exit /b 0
