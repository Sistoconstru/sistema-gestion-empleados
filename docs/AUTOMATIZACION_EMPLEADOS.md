# ========================================
# CONFIGURACIÓN DE AUTOMATIZACIÓN
# ========================================

## PARA WINDOWS (Task Scheduler)

### 1. Crear Tarea Programada
1. Abrir "Programador de Tareas" (Task Scheduler)
2. Crear Tarea Básica
3. Configurar:
   - Nombre: "Activar Empleados Periodo Prueba"
   - Descripción: "Activa automáticamente empleados que han completado 2 meses de periodo de prueba"
   - Disparador: Diario a las 06:00 AM
   - Acción: Iniciar programa
     - Programa: C:\path\to\python.exe  (ruta al Python del entorno virtual)
     - Argumentos: scripts\activar_empleados_automatico.py
     - Iniciar en: C:\Sisto\SIGHU\sistema-gestion-empleados-mi-rama

### 2. Comando PowerShell para crear la tarea
```powershell
$Action = New-ScheduledTaskAction -Execute "C:\path\to\python.exe" -Argument "scripts\activar_empleados_automatico.py" -WorkingDirectory "C:\Sisto\SIGHU\sistema-gestion-empleados-mi-rama"
$Trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "ActivarEmpleadosPeriodoPrueba" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Activa empleados que completaron periodo de prueba"
```

## PARA LINUX/MAC (Crontab)

### 1. Editar crontab
```bash
crontab -e
```

### 2. Agregar línea
```bash
# Ejecutar todos los días a las 6:00 AM
0 6 * * * cd /path/to/sistema-gestion-empleados && /path/to/python scripts/activar_empleados_automatico.py
```

## COMANDOS MANUALES

### 1. Ejecutar activación (dry-run)
```bash
python manage.py activar_empleados_prueba --dry-run
```

### 2. Ejecutar activación real
```bash
python manage.py activar_empleados_prueba
```

### 3. Ejecutar con periodo personalizado (120 días en lugar de 90)
```bash
python manage.py activar_empleados_prueba --dias-periodo 120
```

### 4. Ejecutar script automatizado
```bash
python scripts/activar_empleados_automatico.py
```

## LOGS Y MONITOREO

Los logs se guardan en:
- logs/activacion_automatica.log (script automatizado)
- Logs de Django según configuración

## PRUEBAS

### Verificar empleados que se activarían:
```bash
python manage.py activar_empleados_prueba --dry-run
```

### Activar manualmente:
```bash
python manage.py activar_empleados_prueba
```