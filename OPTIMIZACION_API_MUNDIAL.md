# 💰 Optimización de Consumo de API - Polla Mundial 2026

## 📊 Comparativa de Escenarios

### Resumen Ejecutivo

| Escenario | Requests Totales | Costo Estimado | Ahorro | Cobertura |
|-----------|------------------|----------------|--------|-----------|
| 🔴 **24/7 - Cada 30 min** | ~5,616 | $18 (2 meses) | - | 100% |
| 🟡 **1PM-1AM - Cada 30 min** | ~2,808 | $9 (1 mes) | **50%** ⭐ | 95% |
| 🟢 **1PM-1AM - Cada 60 min** | ~1,404 | $9 (1 mes) | **75%** | 90% |
| 🟢 **Solo días de partido - Manual** | ~150 | $9 (1 mes) | **97%** | 100% manual |

⭐ **Recomendado:** Escenario 1PM-1AM cada 30 min

---

## 🔴 Escenario 1: 24/7 - Cada 30 Minutos (Sin Optimización)

### Configuración
```bash
# Script: actualizar_polla_mundial.bat/.sh
# Frecuencia: */30 * * * * (cada 30 minutos, 24/7)
```

### Consumo
- **Ciclos por día:** 48
- **Requests por ciclo:** 3
- **Requests diarios:** 144
- **Requests totales (39 días):** ~5,616

### Distribución Mensual
- **Junio (30 días):** ~4,320 requests ❌ Excede límite (3,000)
- **Julio (9 días):** ~1,296 requests ✅ OK

### Análisis
❌ **Excede límite mensual en junio**
❌ **Requiere 2 meses de suscripción** ($18)
✅ Cobertura 100% del tiempo
✅ Sin configuración adicional

**Costo:** $18 USD (2 meses)

---

## 🟡 Escenario 2: 1PM-1AM - Cada 30 Minutos ⭐ **RECOMENDADO**

### Configuración

**Windows:**
```bash
# Usar: actualizar_polla_mundial_horario.bat
# Programador de Tareas:
# - Ejecutar cada 30 minutos (24/7)
# - El script filtra automáticamente el horario
```

**Linux/Mac:**
```bash
# Crontab:
*/30 * * * * /ruta/proyecto/actualizar_polla_mundial_horario.sh
```

### Consumo
- **Horario activo:** 13:00 - 01:00 (12 horas)
- **Ciclos por día:** 24
- **Requests por ciclo:** 3
- **Requests diarios:** 72
- **Requests totales (39 días):** ~2,808

### Distribución Mensual
- **Junio (30 días):** ~2,160 requests ✅ OK
- **Julio (9 días):** ~648 requests ✅ OK

### Análisis
✅ **Dentro del límite mensual** (2,808 < 3,000)
✅ **Solo 1 mes de suscripción** ($9)
✅ **Ahorro del 50%** en requests
✅ **Cubre horario clave** (mayoría de partidos son 12PM-9PM)
✅ **Configuración automática** (el script filtra por horario)

**Costo:** $9 USD (1 mes)

### Cobertura de Partidos

Los partidos del Mundial 2026 usualmente se juegan en estos horarios (hora local):
- **12:00 PM** (mediodía)
- **3:00 PM** (tarde)
- **6:00 PM** (noche)
- **9:00 PM** (noche)

Con actualización 1PM-1AM cubres:
- ✅ **Todos** los partidos del mediodía (12 PM)
- ✅ **Todos** los partidos de la tarde (3 PM, 6 PM)
- ✅ **Todos** los partidos de la noche (9 PM)
- ✅ Actualización hasta 4 horas después del último partido

**Cobertura estimada:** 95-100% de todos los partidos

---

## 🟢 Escenario 3: 1PM-1AM - Cada 60 Minutos

### Configuración

**Windows:**
```bash
# Modificar actualizar_polla_mundial_horario.bat
# Programador de Tareas: Ejecutar cada 60 minutos
```

**Linux/Mac:**
```bash
# Crontab (cada hora, de 1 PM a 1 AM):
0 13-23,0-1 * * * /ruta/proyecto/actualizar_polla_mundial_horario.sh
```

### Consumo
- **Horario activo:** 13:00 - 01:00 (12 horas)
- **Ciclos por día:** 12
- **Requests por ciclo:** 3
- **Requests diarios:** 36
- **Requests totales (39 días):** ~1,404

### Distribución Mensual
- **Junio (30 días):** ~1,080 requests ✅ OK
- **Julio (9 días):** ~324 requests ✅ OK

### Análisis
✅ **Ahorro del 75%** en requests
✅ Solo 1 mes de suscripción ($9)
⚠️ **Resultados menos frecuentes** (1 hora vs 30 min de delay)
✅ Aún cubre todos los partidos

**Costo:** $9 USD (1 mes)

---

## 🟢 Escenario 4: Solo Días de Partido - Actualización Manual

### Configuración
```bash
# NO configurar tarea automática
# Ejecutar manualmente después de cada jornada:
python manage.py actualizar_resultados_mundial --verbose
```

### Consumo
- **Partidos totales:** 104
- **Jornadas estimadas:** ~50
- **Requests por ejecución manual:** 3
- **Requests totales:** ~150

### Análisis
✅ **Ahorro del 97%** en requests
✅ Solo 1 mes de suscripción ($9)
✅ **Control total** de cuándo actualizar
❌ **Requiere intervención manual** cada día
⚠️ Empleados no ven resultados en tiempo real

**Costo:** $9 USD (1 mes)

---

## 📋 Tabla Comparativa Detallada

| Métrica | 24/7 (30min) | 1PM-1AM (30min) ⭐ | 1PM-1AM (60min) | Manual |
|---------|--------------|-------------------|-----------------|--------|
| **Requests/día** | 144 | 72 | 36 | 3 |
| **Requests totales** | 5,616 | 2,808 | 1,404 | 150 |
| **Ahorro vs 24/7** | - | 50% | 75% | 97% |
| **Meses necesarios** | 2 | 1 | 1 | 1 |
| **Costo total** | $18 | $9 | $9 | $9 |
| **Delay máximo** | 30 min | 30 min | 60 min | Variable |
| **Cobertura** | 100% | 95% | 90% | 100% |
| **Automatización** | ✅ Total | ✅ Total | ✅ Total | ❌ Manual |
| **Trabajo manual** | Ninguno | Ninguno | Ninguno | Alto |

---

## 🎯 Recomendación Final

### Para la mayoría de casos: **Escenario 2 (1PM-1AM cada 30 min)**

**Razones:**
1. ✅ **Costo óptimo:** Solo $9 (1 mes vs 2 meses)
2. ✅ **Ahorro significativo:** 50% menos requests
3. ✅ **100% automático:** Sin trabajo manual
4. ✅ **Cobertura excelente:** Cubre todos los partidos
5. ✅ **Tiempo real:** Resultados actualizados cada 30 min
6. ✅ **Configuración simple:** Scripts ya creados

### ¿Cuándo usar otros escenarios?

**Escenario 1 (24/7):**
- Si tu zona horaria está muy alejada de las sedes del Mundial
- Si quieres monitoreo nocturno también
- Si el presupuesto no es limitación

**Escenario 3 (60 min):**
- Si quieres ahorrar aún más
- Si 1 hora de delay es aceptable
- Si solo quieres 1 mes de suscripción con margen extra

**Escenario 4 (Manual):**
- Presupuesto muy ajustado
- Pocos partidos a seguir
- No te importa actualizar manualmente

---

## 🛠️ Implementación del Escenario Recomendado

### Paso 1: Usar Script con Restricción de Horario

**Ya está creado para ti:**
- ✅ Windows: [`actualizar_polla_mundial_horario.bat`](actualizar_polla_mundial_horario.bat)
- ✅ Linux/Mac: [`actualizar_polla_mundial_horario.sh`](actualizar_polla_mundial_horario.sh)

### Paso 2: Configurar Tarea Programada

**Windows - Programador de Tareas:**
```
- Nombre: Actualizar Polla Mundial (Optimizado)
- Programa: C:\ruta\actualizar_polla_mundial_horario.bat
- Desencadenador: Cada 30 minutos (24/7)
- El script filtra automáticamente por horario
```

**Linux/Mac - Crontab:**
```bash
# Editar crontab
crontab -e

# Agregar línea (cada 30 min, 24/7 - el script filtra):
*/30 * * * * /ruta/proyecto/actualizar_polla_mundial_horario.sh
```

### Paso 3: Verificar Funcionamiento

```bash
# Ejecutar manualmente para probar
./actualizar_polla_mundial_horario.bat   # Windows
./actualizar_polla_mundial_horario.sh    # Linux/Mac

# Verificar log
type logs\polla_mundial_updates.log      # Windows
tail -f logs/polla_mundial_updates.log   # Linux/Mac
```

**Salida esperada:**

**Dentro del horario (1 PM - 1 AM):**
```
========================================
Actualización Polla Mundial - 2026-06-15 14:30:00
Horario permitido: 1 PM - 1 AM
========================================
[1/3] Actualizando equipos TBD...
[2/3] Actualizando resultados de partidos...
[3/3] Verificando nuevos partidos...
========================================
Actualización completada - 2026-06-15 14:32:00
========================================
```

**Fuera del horario (2 AM - 12 PM):**
```
2026-06-15 03:00:00 - Fuera de horario permitido (1 PM - 1 AM). Omitiendo actualización...
```

---

## 💡 Consejos Adicionales

### 1. Activar Solo Durante el Mundial

En lugar de ejecutar 24/7 todo el año:

**Windows:**
- Deshabilitar tarea programada antes y después del Mundial
- Habilitar del 11 junio al 19 julio 2026

**Linux/Mac:**
```bash
# Comentar/descomentar línea en crontab
crontab -e

# Durante el Mundial (activado):
*/30 * * * * /ruta/proyecto/actualizar_polla_mundial_horario.sh

# Después del Mundial (comentado):
# */30 * * * * /ruta/proyecto/actualizar_polla_mundial_horario.sh
```

### 2. Monitorear Consumo de API

Crear script de monitoreo:

```bash
# Ver requests realizados hoy
grep "$(date +%Y-%m-%d)" logs/polla_mundial_updates.log | wc -l
```

### 3. Ajustar Horario Según Zona Horaria

Si estás en una zona horaria diferente a las sedes del Mundial, ajusta el script:

**Ejemplo: Sedes en UTC-5, tú en UTC-8 (3 horas de diferencia)**

Modificar en el script:
```bash
# Ajustar horario 3 horas antes
# En lugar de: 13:00 - 01:00
# Usar: 10:00 - 22:00
```

---

## 📊 Resumen de Costos

| Opción | Requests | Meses | Costo | Ahorro |
|--------|----------|-------|-------|--------|
| Sin optimizar | 5,616 | 2 | $18 | - |
| **Optimizado (1PM-1AM)** ⭐ | 2,808 | 1 | **$9** | **$9 (50%)** |

**Ahorro total implementando optimización: $9 USD**

---

## ✅ Checklist de Implementación

- [ ] Decidir escenario (recomendado: 1PM-1AM cada 30 min)
- [ ] Usar script optimizado: `actualizar_polla_mundial_horario.bat/.sh`
- [ ] Configurar tarea programada cada 30 minutos
- [ ] Probar ejecución manual
- [ ] Verificar que se omita fuera de horario
- [ ] Monitorear logs primeros días
- [ ] Contratar solo 1 mes de API Premium ($9)
- [ ] Cancelar suscripción después del Mundial

---

**Con esta optimización ahorras 50% en costos y requests. ¡Implementación lista! ⚽💰**
