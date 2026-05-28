@echo off
REM =============================================================================
REM Script de Windows para actualizar la Polla Mundial (HORARIO LIMITADO)
REM =============================================================================
REM Este script solo ejecuta entre 1 PM (13:00) y 1 AM (01:00)
REM REDUCE CONSUMO DE API EN 50%
REM Configurar en: Programador de Tareas - Ejecutar cada 30 minutos (24/7)

cd /d %~dp0

REM Obtener hora actual (formato 24h)
for /f "tokens=1-2 delims=:" %%a in ("%time%") do (
    set hora=%%a
    set minuto=%%b
)

REM Eliminar espacios en blanco de la hora
set hora=%hora: =%

REM Convertir a número
set /a hora_num=%hora%

REM Verificar si estamos en el horario permitido (13:00 - 01:00)
REM Horario: 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1
if %hora_num% geq 13 goto ejecutar
if %hora_num% leq 1 goto ejecutar

REM Fuera del horario - No ejecutar
echo %date% %time% - Fuera de horario permitido (1 PM - 1 AM). Omitiendo actualizacion... >> logs\polla_mundial_updates.log
exit /b 0

:ejecutar
echo ========================================
echo Actualizacion Polla Mundial - %date% %time%
echo Horario permitido: 1 PM - 1 AM
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
