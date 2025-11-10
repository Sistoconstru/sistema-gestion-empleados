# SISTEMA DE ACTIVACIÓN AUTOMÁTICA DE EMPLEADOS

## Descripción General

El sistema de gestión de empleados ahora incluye funcionalidad para activar automáticamente a los empleados que han completado su período de prueba de 2 meses (60 días).

## Características Principales

### 1. Activación Automática
- **Criterio**: Empleados con estado "per. prueba" (código: p-prue) que hayan cumplido 60 días desde su fecha de ingreso
- **Estado destino**: Activo (código: 999)
- **Proceso**: Completamente automatizado

### 2. Comando de Gestión
```bash
# Comando principal
python manage.py activar_empleados_prueba

# Opciones disponibles
python manage.py activar_empleados_prueba --dry-run              # Solo muestra qué se haría
python manage.py activar_empleados_prueba --dias-periodo 90      # Usar 90 días en lugar de 60
```

### 3. Script Automatizado
```bash
python scripts/activar_empleados_automatico.py
```

### 4. Reporte de Período de Prueba
- **URL**: `/empleados/periodo-prueba/`
- **Acceso**: Desde el listado de empleados, botón "Período de Prueba"
- **Información mostrada**:
  - Empleados actualmente en período de prueba
  - Días transcurridos y restantes
  - Fecha prevista de activación automática
  - Estado de cada empleado

## Funcionalidades del Sistema

### Registro de Auditoría
- Todos los cambios de estado se registran en los logs del sistema
- Se diferencia entre cambios manuales y automáticos
- Información detallada para cada activación

### Signals de Django
- **pre_save**: Captura el estado anterior del empleado
- **post_save**: Registra cambios de estado y detecta activaciones automáticas

## Configuración de Automatización

### Windows (Task Scheduler)
1. Abrir "Programador de Tareas"
2. Crear nueva tarea:
   - **Nombre**: "Activar Empleados Periodo Prueba"
   - **Disparador**: Diario a las 6:00 AM
   - **Acción**: Ejecutar script
   - **Programa**: Ruta al Python del entorno virtual
   - **Argumentos**: `scripts\activar_empleados_automatico.py`
   - **Directorio**: Directorio raíz del proyecto

### Linux/Mac (Crontab)
```bash
# Ejecutar todos los días a las 6:00 AM
0 6 * * * cd /path/to/proyecto && /path/to/python scripts/activar_empleados_automatico.py
```

## Logs y Monitoreo

### Ubicación de Logs
- **Comando de gestión**: Logs de Django (según configuración)
- **Script automatizado**: `logs/activacion_automatica.log`

### Ejemplo de Log
```
INFO 2025-11-10 12:21:19,488 activar_empleados_prueba Empleado 10352125 (Ana Maria Aaron) activado automáticamente después de 96 días en periodo de prueba
```

## Casos de Uso

### 1. Ejecución Manual
```bash
# Ver qué empleados se activarían
python manage.py activar_empleados_prueba --dry-run

# Activar empleados
python manage.py activar_empleados_prueba
```

### 2. Monitoreo Regular
- Acceder al reporte: `http://tu-servidor/empleados/periodo-prueba/`
- Revisar empleados próximos a cumplir período
- Verificar fechas de activación automática

### 3. Configuración Personalizada
```bash
# Usar período de 90 días en lugar de 60 (política anterior)
python manage.py activar_empleados_prueba --dias-periodo 90
```

## Consideraciones Importantes

### Estados Requeridos
El sistema requiere que existan estos estados en la base de datos:
- **p-prue**: per. prueba (estado origen)
- **999**: Activo (estado destino)

### Validaciones
- Solo empleados con estado "p-prue" son considerados
- Solo se activan empleados que hayan cumplido exactamente el período configurado
- No se modifican empleados ya activos o con otros estados

### Seguridad
- El comando requiere acceso a la base de datos
- Se registra información de auditoría para cada cambio
- Modo dry-run permite verificar cambios antes de aplicarlos

## Solución de Problemas

### Error: Estados no encontrados
```bash
# Verificar que existan los estados necesarios
python -c "
import django
django.setup()
from apps.employees.models import EstadoEmpleado
print('Estados disponibles:')
[print(f'{e.codigo}: {e.nombre}') for e in EstadoEmpleado.objects.all()]
"
```

### Verificar Empleados en Período de Prueba
```bash
python -c "
import django
django.setup()
from apps.employees.models import Empleado, EstadoEmpleado
estado = EstadoEmpleado.objects.get(codigo='p-prue')
empleados = Empleado.objects.filter(estado=estado)
print(f'Empleados en período de prueba: {empleados.count()}')
for emp in empleados:
    print(f'- {emp.nombre_completo}: {emp.fecha_ingreso}')
"
```

## Próximas Mejoras

### Funcionalidades Planificadas
1. **Notificaciones**: Envío de emails cuando se activa un empleado
2. **API REST**: Endpoints para consultar y activar empleados
3. **Dashboard**: Gráficos de activaciones en el dashboard principal
4. **Configuración**: Período de prueba configurable desde la interfaz admin

### Automatización Avanzada
1. **Webhooks**: Notificaciones a sistemas externos
2. **Integración con nómina**: Actualización automática de sistemas de pago
3. **Reportes programados**: Envío automático de reportes semanales

## Contacto y Soporte

Para reportar problemas o solicitar mejoras, contactar al equipo de desarrollo con:
- Logs del error
- Configuración utilizada
- Pasos para reproducir el problema