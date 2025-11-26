# Automatización del Sistema de Evaluaciones

Este documento explica cómo usar y configurar la automatización del sistema de evaluaciones de período de prueba.

## Comandos Disponibles

### 1. Asignación Automática de Evaluaciones

**Comando:** `asignar_evaluaciones_periodo_prueba`

**Propósito:** Asigna automáticamente evaluaciones de período de prueba a empleados que tienen entre 30 y 60 días de servicio.

**Uso:**

```bash
# Modo simulación (no hace cambios)
python manage.py asignar_evaluaciones_periodo_prueba --dry-run

# Ejecutar asignaciones reales
python manage.py asignar_evaluaciones_periodo_prueba

# Personalizar rango de días
python manage.py asignar_evaluaciones_periodo_prueba --dias-minimos 30 --dias-maximos 60
```

**Lógica del comando:**

1. Busca empleados en estado `p-prue` (período de prueba)
2. Filtra los que tienen entre 30-60 días de servicio
3. Verifica si ya tienen una evaluación asignada
4. Busca el jefe directo desde `HistorialCargo.jefe_directo`
5. Crea la asignación con vencimiento de 15 días
6. Registra logs para auditoría

**Características:**

- ✅ Evita duplicados (no asigna si ya existe evaluación para ese período)
- ✅ Valida que el jefe directo esté activo
- ✅ Genera logs detallados en `logs/django.log`
- ✅ Modo dry-run para pruebas sin cambios
- ✅ Estadísticas detalladas al finalizar

**Salida esperada:**

```
Encontrados 5 empleados elegibles para evaluación:

- Andres Andes (Doc: 1035212554211)
  Fecha ingreso: 2025-10-22 (33 días transcurridos)
  Sede: CO-0001 - Caldas
  Jefe directo: Bernardo Marin
  [OK] Evaluacion asignada - Vence: 2025-12-09

- Pedro Perez (Doc: 12356923555)
  Fecha ingreso: 2025-10-15 (40 días transcurridos)
  Sede: CO-0001 - Caldas
  [!] No se encontro jefe directo - NO SE ASIGNARA

============================================================
RESUMEN DE ASIGNACIONES:
[OK] Evaluaciones asignadas: 2
[!] Ya tenian evaluacion: 0
[!] Sin jefe directo: 3
============================================================
```

---

### 2. Activación Automática de Empleados

**Comando:** `activar_empleados_prueba`

**Propósito:** Activa automáticamente empleados que completaron su período de prueba de 60 días con evaluación satisfactoria.

**Uso:**

```bash
# Modo simulación (no hace cambios)
python manage.py activar_empleados_prueba --dry-run

# Ejecutar activaciones reales
python manage.py activar_empleados_prueba

# Personalizar período (por defecto 60 días)
python manage.py activar_empleados_prueba --dias-periodo 60
```

**Lógica del comando:**

1. Busca empleados en estado `p-prue` con más de 60 días
2. Verifica que tengan evaluación de período de prueba completada
3. Valida que el puntaje sea satisfactorio (≥ 14/21 puntos por suma)
4. Cambia el estado a ACTIVO (`999` o `ACTIVO`)
5. Registra logs para auditoría

**Sistema de Calificación:**

- **Método:** Suma de respuestas (NO promedio)
- **Preguntas:** 7
- **Escala por pregunta:** 1-3 puntos
- **Puntaje máximo:** 21 puntos (7 × 3)
- **Puntaje mínimo aprobatorio:** 14 puntos (≥66.67%)

**Características:**

- ✅ Validación estricta de evaluación completada
- ✅ Cálculo por suma (no promedio)
- ✅ No activa si evaluación es insatisfactoria
- ✅ No activa si evaluación no existe o está pendiente
- ✅ Logs detallados con puntajes
- ✅ Modo dry-run para pruebas

**Salida esperada:**

```
Encontrados 2 empleados para activar:

- Juan Pérez (Doc: 123456789)
  Fecha ingreso: 2025-08-15 (101 días transcurridos)
  Sede: CO-0001 - Caldas
  ✅ Evaluación satisfactoria (18/21 puntos) - PROCEDE ACTIVACIÓN
  ✓ Activado exitosamente

- María García (Doc: 987654321)
  Fecha ingreso: 2025-08-20 (96 días transcurridos)
  Sede: CO-0002 - Bogotá
  ❌ Evaluación insatisfactoria (12/21 puntos) - NO SE ACTIVARÁ

============================================================
📊 RESUMEN DE ACTIVACIONES:
✅ Empleados activados: 1
⚠️ Sin evaluación/pendiente: 0
❌ Evaluación insatisfactoria: 1
============================================================
```

---

## Scripts de Automatización

### Script 1: `scripts/asignar_evaluaciones_automatico.py`

Script wrapper para ejecutar el comando de asignación de evaluaciones como tarea programada.

**Características:**

- Configura Django automáticamente
- Registra logs en `logs/asignacion_automatica.log`
- Manejo de errores robusto

**Uso manual:**

```bash
python scripts/asignar_evaluaciones_automatico.py
```

### Script 2: `scripts/activar_empleados_automatico.py`

Script wrapper para ejecutar el comando de activación de empleados como tarea programada.

**Características:**

- Configura Django automáticamente
- Registra logs en `logs/activacion_automatica.log`
- Manejo de errores robusto

**Uso manual:**

```bash
python scripts/activar_empleados_automatico.py
```

---

## Configuración de Tareas Programadas

### Windows (Task Scheduler)

#### Asignación de Evaluaciones - Diaria a las 6:00 AM

1. Abrir **Programador de tareas** (Task Scheduler)
2. Crear tarea básica:
   - **Nombre:** Asignar Evaluaciones Periodo Prueba
   - **Desencadenador:** Diariamente a las 6:00 AM
   - **Acción:** Iniciar programa
   - **Programa/script:** `C:\Sisto\SIGHU\sistema-gestion-empleados-mi-rama\mi-entorno\Scripts\python.exe`
   - **Argumentos:** `scripts\asignar_evaluaciones_automatico.py`
   - **Iniciar en:** `C:\Sisto\SIGHU\sistema-gestion-empleados-mi-rama`

#### Activación de Empleados - Diaria a las 7:00 AM

1. Abrir **Programador de tareas** (Task Scheduler)
2. Crear tarea básica:
   - **Nombre:** Activar Empleados Periodo Prueba
   - **Desencadenador:** Diariamente a las 7:00 AM
   - **Acción:** Iniciar programa
   - **Programa/script:** `C:\Sisto\SIGHU\sistema-gestion-empleados-mi-rama\mi-entorno\Scripts\python.exe`
   - **Argumentos:** `scripts\activar_empleados_automatico.py`
   - **Iniciar en:** `C:\Sisto\SIGHU\sistema-gestion-empleados-mi-rama`

### Linux/Mac (Crontab)

#### Asignación de Evaluaciones - Diaria a las 6:00 AM

```bash
crontab -e
```

Agregar línea:

```
0 6 * * * /path/to/venv/bin/python /path/to/proyecto/scripts/asignar_evaluaciones_automatico.py >> /path/to/logs/cron_asignacion.log 2>&1
```

#### Activación de Empleados - Diaria a las 7:00 AM

```
0 7 * * * /path/to/venv/bin/python /path/to/proyecto/scripts/activar_empleados_automatico.py >> /path/to/logs/cron_activacion.log 2>&1
```

---

## Flujo Completo del Proceso

```
Día 0: Empleado ingresa con estado "p-prue"
    ↓
Día 30-60: Script asigna evaluación al jefe directo
    ↓
Jefe directo completa evaluación (15 días para completar)
    ↓
Día 60+: Script verifica evaluación y activa empleado
    ↓
Estado cambia a "ACTIVO" (si puntaje ≥ 14/21)
```

---

## Logs y Monitoreo

### Ubicación de Logs

- **Django general:** `logs/django.log`
- **Asignación automática:** `logs/asignacion_automatica.log`
- **Activación automática:** `logs/activacion_automatica.log`

### Qué se registra

**Asignación:**
- Empleados encontrados con 30-60 días
- Asignaciones creadas exitosamente
- Empleados sin jefe directo
- Errores técnicos

**Activación:**
- Empleados con 60+ días
- Puntajes de evaluación (X/21 puntos)
- Activaciones exitosas
- Empleados con evaluación insatisfactoria
- Empleados sin evaluación

---

## Solución de Problemas

### "No se encontró jefe directo"

**Causa:** El empleado no tiene un jefe directo asignado en `HistorialCargo.jefe_directo`

**Solución:**
1. Ir al admin de Django
2. Buscar el empleado en Historial de Cargos
3. Editar el registro activo
4. Asignar el jefe directo correspondiente

### "No se encontró evaluación activa"

**Causa:** No existe una evaluación de tipo `PERIODO_PRUEBA` marcada como activa

**Solución:**
1. Verificar que existe un registro en `TipoEvaluacion` con código `PERIODO_PRUEBA`
2. Verificar que existe una `EvaluacionDesempeño` con ese tipo y `activa=True`

### "Evaluación insatisfactoria"

**Causa:** El puntaje es < 14 puntos

**Solución:**
- **Si es legítimo:** El empleado requiere seguimiento adicional
- **Si es error:** Revisar las respuestas de la evaluación y corregir si necesario

### Problemas de encoding en Windows

Los mensajes pueden aparecer con caracteres extraños debido a la codificación de la consola de Windows. Esto no afecta el funcionamiento del sistema, solo la visualización.

---

## Recomendaciones

1. **Ejecutar primero en modo dry-run** antes de programar las tareas
2. **Revisar logs regularmente** para detectar problemas temprano
3. **Asignar jefes directos** a todos los empleados nuevos desde el primer día
4. **Monitorear empleados sin jefe directo** cada semana
5. **Configurar alertas** si los logs muestran muchos errores
6. **Respaldar la base de datos** antes de cambios masivos

---

## Contacto y Soporte

Para problemas o dudas sobre estos comandos, revisar:
- Logs en `logs/`
- Código fuente en `apps/evaluations/management/commands/`
- Código fuente en `apps/employees/management/commands/`
