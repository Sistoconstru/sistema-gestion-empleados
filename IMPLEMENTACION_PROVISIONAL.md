# 🧪 Implementación Provisional - Polla Mundial (Sin Costo)

## 📋 Objetivo

Implementar y probar **completamente gratis** el sistema de Polla Mundial usando:
- ✅ API gratuita de TheSportsDB (key: `3`)
- ✅ Datos del Mundial 2022 Qatar (104 partidos completos)
- ✅ Todos los empleados pueden probar el sistema
- ✅ Cero costos hasta que decidas usar el Mundial 2026 real

---

## 🎯 Ventajas de Implementación Provisional

| Ventaja | Descripción |
|---------|-------------|
| 💰 **Gratis** | Sin suscripción Premium necesaria |
| 🧪 **Prueba completa** | Testear todas las funcionalidades |
| 📚 **Capacitación** | Empleados aprenden a usar el sistema |
| 🐛 **Detectar bugs** | Encontrar errores antes del Mundial real |
| 🎮 **Gamificación** | Generar interés en la app |
| 🔄 **Fácil migración** | Cambiar a Mundial 2026 con 1 comando |

---

## 🚀 Paso 1: Configuración Inicial (5 minutos)

### 1.1 Aplicar Migraciones

```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Crear migraciones
python manage.py makemigrations employees

# Aplicar migraciones
python manage.py migrate employees
```

### 1.2 Configurar API Gratuita

Editar [`.env`](.env):

```env
# Usar API key gratuita (no cambiar, ya está configurada)
THESPORTSDB_API_KEY=3
```

**No requiere suscripción ni registro.**

---

## 🏆 Paso 2: Importar Mundial 2022 Qatar (Datos de Prueba)

### 2.1 Ejecutar Importación

```bash
# Importar fixture completo del Mundial 2022
python manage.py importar_partidos_mundial --season=2022
```

### 2.2 Salida Esperada

```
Importando partidos del Mundial 2022...
⚠️  ADVERTENCIA: Usando API key gratuita o no configurada
Configura THESPORTSDB_API_KEY en tu archivo .env con tu API key premium
Continúa con limitaciones de la API gratuita (15 requests/mes)...

Consultando: https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4429&s=2022
Se encontraron 64 partidos
✓ Creado: Qatar vs Ecuador
✓ Creado: England vs Iran
✓ Creado: Senegal vs Netherlands
✓ Creado: USA vs Wales
...
✓ Creado: Argentina vs France (FINAL)
=== Resumen ===
Partidos creados: 64
Partidos actualizados: 0
```

**Nota:** El Mundial 2022 tuvo 64 partidos (no 104 como tendrá el 2026 con más equipos).

### 2.3 Verificar Importación

```bash
# Abrir shell de Django
python manage.py shell

# Verificar partidos importados
from apps.employees.models import PartidoMundial
print(f"Total partidos: {PartidoMundial.objects.count()}")
print(f"Finalizados: {PartidoMundial.objects.filter(finalizado=True).count()}")
```

**Resultado esperado:**
```python
Total partidos: 64
Finalizados: 64  # Mundial 2022 ya terminó
```

---

## 🎮 Paso 3: Actualizar Resultados Automáticamente

### 3.1 Ejecutar Actualización de Resultados

```bash
# Actualizar resultados de todos los partidos del Mundial 2022
python manage.py actualizar_resultados_mundial --verbose
```

### 3.2 Salida Esperada

```
Actualizando resultados desde TheSportsDB Premium...
⚠️  ADVERTENCIA: Usando API key gratuita
Configura THESPORTSDB_API_KEY en tu archivo .env

Partidos pendientes de actualización: 64

✓ Qatar 0 - 2 Ecuador
  → 0 predicciones actualizadas
✓ England 6 - 2 Iran
  → 0 predicciones actualizadas
...
✓ Argentina 3 - 3 France (Penales: 4-2)
  → 0 predicciones actualizadas

=== Resumen ===
Partidos actualizados: 64
```

**Importante:** Como el Mundial 2022 ya finalizó, todos los partidos ya tienen resultados.

---

## 👥 Paso 4: Pruebas con Empleados

### 4.1 Comunicar a Empleados

Enviar mensaje interno:

```
🏆 NUEVA FUNCIONALIDAD: Polla Mundialista de Prueba

Hemos habilitado un sistema de predicciones deportivas para que lo prueben.
Usamos datos del Mundial 2022 Qatar como demo.

📍 Acceso:
1. Ir a Marketplace > Polla Mundial 2026
2. Ver partidos del Mundial 2022
3. Revisar ranking y resultados finales

🎯 Objetivo:
- Familiarizarse con el sistema
- Dar feedback sobre usabilidad
- Prepararnos para el Mundial 2026 real

⚠️ Nota: Los partidos ya finalizaron (es histórico), pero pueden ver cómo funciona el sistema de puntos y ranking.
```

### 4.2 Crear Predicciones de Prueba Manualmente

Para probar el cálculo de puntos:

```bash
# Abrir shell de Django
python manage.py shell
```

```python
from apps.employees.models import PartidoMundial, PrediccionMundial, Empleado
from apps.authentication.models import Usuario

# Obtener un empleado de prueba
empleado = Empleado.objects.first()

# Obtener un partido finalizado (ejemplo: Final Argentina vs Francia)
partido = PartidoMundial.objects.filter(
    equipo_local__icontains='Argentina',
    equipo_visitante__icontains='France',
    finalizado=True
).first()

if partido:
    print(f"Partido: {partido}")
    print(f"Resultado real: {partido.goles_local} - {partido.goles_visitante}")

    # Crear predicción de prueba (resultado exacto)
    prediccion = PrediccionMundial.objects.create(
        empleado=empleado,
        partido=partido,
        goles_local_prediccion=3,  # Argentina ganó 3-3 (4-2 penales)
        goles_visitante_prediccion=3
    )

    # Calcular puntos
    puntos = prediccion.calcular_puntos()
    prediccion.save()

    print(f"Predicción creada: {prediccion.goles_local_prediccion} - {prediccion.goles_visitante_prediccion}")
    print(f"Puntos obtenidos: {puntos}")
```

---

## 🔧 Paso 5: Configuración Sin Actualización Automática

### 5.1 ¿Por Qué No Automatizar con API Gratuita?

❌ **NO configurar tarea automática** con API gratuita porque:
- Límite: Solo 15 requests/mes
- Se agotaría en 1 día
- No tiene sentido para datos históricos (2022)

### 5.2 Alternativa: Actualización Manual Bajo Demanda

```bash
# Solo cuando necesites actualizar algo:
python manage.py actualizar_resultados_mundial
```

---

## 📊 Paso 6: Verificar Funcionamiento

### 6.1 Acceder a la Interfaz Web

1. Iniciar servidor Django:
   ```bash
   python manage.py runserver
   ```

2. Abrir navegador: `http://localhost:8000/empleados/polla-mundial/`

3. Verificar que aparezcan:
   - ✅ Partidos del Mundial 2022
   - ✅ Resultados finales
   - ✅ Banderas de equipos
   - ✅ Fases del torneo

### 6.2 Probar Funcionalidades

**Como Empleado:**
- [ ] Ver lista de partidos
- [ ] Ver resultados (ya finalizados)
- [ ] Ver ranking (aunque esté vacío)
- [ ] Navegar entre secciones

**Como Admin:**
- [ ] Acceder a `/admin/employees/partidomundial/`
- [ ] Ver todos los partidos importados
- [ ] Editar un partido de prueba
- [ ] Ver predicciones (si creaste alguna)

---

## 🎯 Paso 7: Crear Escenario de Prueba Realista

### 7.1 Simular Predicciones de Varios Empleados

Crear script de prueba [`scripts/crear_predicciones_prueba.py`](scripts/crear_predicciones_prueba.py):

```python
# scripts/crear_predicciones_prueba.py
"""
Script para crear predicciones de prueba con datos del Mundial 2022
Ejecutar: python manage.py shell < scripts/crear_predicciones_prueba.py
"""

from apps.employees.models import PartidoMundial, PrediccionMundial, Empleado
from random import randint

# Obtener todos los partidos finalizados
partidos = PartidoMundial.objects.filter(finalizado=True)[:10]  # Primeros 10 partidos

# Obtener empleados
empleados = Empleado.objects.all()[:5]  # Primeros 5 empleados

if not empleados.exists():
    print("❌ No hay empleados en la base de datos")
    print("Crear al menos un empleado desde /admin/employees/empleado/")
else:
    print(f"📊 Creando predicciones de prueba...")
    print(f"   Partidos: {partidos.count()}")
    print(f"   Empleados: {empleados.count()}")

    predicciones_creadas = 0

    for empleado in empleados:
        for partido in partidos:
            # Verificar que no exista predicción
            if not PrediccionMundial.objects.filter(empleado=empleado, partido=partido).exists():
                # Crear predicción aleatoria (cercana al resultado real)
                if partido.goles_local is not None:
                    # Predicción con variación ±1 gol del resultado real
                    pred_local = max(0, partido.goles_local + randint(-1, 1))
                    pred_visitante = max(0, partido.goles_visitante + randint(-1, 1))

                    prediccion = PrediccionMundial.objects.create(
                        empleado=empleado,
                        partido=partido,
                        goles_local_prediccion=pred_local,
                        goles_visitante_prediccion=pred_visitante
                    )

                    # Calcular puntos
                    puntos = prediccion.calcular_puntos()
                    prediccion.save()

                    predicciones_creadas += 1

    print(f"✅ Predicciones creadas: {predicciones_creadas}")

    # Mostrar ranking
    from django.db.models import Sum

    ranking = PrediccionMundial.objects.values('empleado__nombre_completo').annotate(
        total_puntos=Sum('puntos_ganados')
    ).order_by('-total_puntos')[:5]

    print(f"\n🏆 TOP 5 Ranking:")
    for idx, entry in enumerate(ranking, 1):
        print(f"   {idx}. {entry['empleado__nombre_completo']}: {entry['total_puntos']} pts")
```

### 7.2 Ejecutar Script de Prueba

```bash
# Opción 1: Ejecutar directamente
python manage.py shell < scripts/crear_predicciones_prueba.py

# Opción 2: Copiar y pegar en shell
python manage.py shell
# Luego copiar el código del script
```

---

## 🔄 Paso 8: Migración a Mundial 2026 Real (Futuro)

### 8.1 Cuándo Migrar

**Momento ideal:** 1-2 meses antes del Mundial 2026 (abril-mayo 2026)

### 8.2 Proceso de Migración (5 minutos)

```bash
# 1. Contratar TheSportsDB Premium ($9/mes)
# Ir a: https://www.thesportsdb.com/pricing

# 2. Actualizar API key en .env
THESPORTSDB_API_KEY=tu_api_key_premium_2026

# 3. Limpiar datos de prueba del Mundial 2022
python manage.py shell
```

```python
from apps.employees.models import PartidoMundial, PrediccionMundial

# Eliminar todas las predicciones de prueba
PrediccionMundial.objects.all().delete()

# Eliminar partidos del Mundial 2022
PartidoMundial.objects.all().delete()

print("✅ Datos de prueba eliminados")
```

```bash
# 4. Importar partidos del Mundial 2026
python manage.py importar_partidos_mundial --season=2026

# 5. Configurar actualización automática
# Windows: Usar actualizar_polla_mundial_horario.bat
# Linux: Agregar a crontab

# 6. ¡Listo! Sistema en producción
```

---

## 📋 Checklist de Implementación Provisional

### Setup Inicial (Una sola vez)
- [ ] Aplicar migraciones: `python manage.py migrate`
- [ ] Verificar API key gratuita en `.env` (key: `3`)
- [ ] Importar Mundial 2022: `python manage.py importar_partidos_mundial --season=2022`
- [ ] Actualizar resultados: `python manage.py actualizar_resultados_mundial`

### Configuración Admin
- [ ] Verificar partidos en `/admin/employees/partidomundial/`
- [ ] Revisar que todos los partidos estén finalizados
- [ ] Ajustar algún resultado si quieres probar cálculo de puntos

### Pruebas con Empleados
- [ ] Crear predicciones de prueba (manual o con script)
- [ ] Verificar cálculo de puntos
- [ ] Revisar ranking en `/empleados/polla-mundial/ranking/`
- [ ] Probar navegación entre secciones
- [ ] Solicitar feedback de empleados

### Antes del Mundial 2026
- [ ] Contratar TheSportsDB Premium
- [ ] Limpiar datos de prueba
- [ ] Importar Mundial 2026 real
- [ ] Configurar actualización automática
- [ ] Comunicar a empleados el inicio oficial

---

## 💡 Ideas para Maximizar Valor de la Prueba

### 1. Mini-Torneo Interno (Opcional)

Crear un "torneo de predicciones retrospectivas":

```
🎮 DESAFÍO: Polla Mundial 2022 Retrospectiva

¿Quién hubiera ganado la polla del Mundial 2022?

📅 Dinámica:
- Los empleados "predicen" partidos como si no conocieran el resultado
- Se otorgan puntos según el sistema oficial
- Ganador obtiene reconocimiento interno

🏆 Premio:
- Badge especial en el perfil
- Reconocimiento en apps.recognition
- Early access a funciones nuevas
```

### 2. Capacitación Gamificada

Usar el sistema de prueba para:
- Onboarding de nuevos empleados
- Familiarización con la plataforma
- Generar engagement antes del Mundial real

### 3. Prueba A/B de Sistema de Puntos

Experimentar con diferentes configuraciones:
- Multiplicadores por fase
- Puntos por aciertos parciales
- Bonos especiales

---

## 🐛 Troubleshooting

### Problema: No se importan partidos del Mundial 2022

**Solución:**
```bash
# Verificar conectividad a la API
curl "https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4429&s=2022"

# Si no funciona, cargar partidos manualmente desde el admin
```

### Problema: Todos los partidos están finalizados, no puedo probar predicciones

**Solución:**
```bash
# Abrir un partido en el admin y marcarlo como NO finalizado
# /admin/employees/partidomundial/{id}/
# Cambiar: finalizado = False
# Ahora los empleados podrán hacer predicciones
```

### Problema: No aparecen banderas de equipos

**Solución:**
```python
# Agregar banderas manualmente en el admin o con script
from apps.employees.models import PartidoMundial

# Mapa de banderas (emoji)
banderas = {
    'Argentina': '🇦🇷',
    'France': '🇫🇷',
    'Brazil': '🇧🇷',
    'Germany': '🇩🇪',
    'Spain': '🇪🇸',
    'England': '🏴󐁧󐁢󐁥󐁮󐁧󐁿',
    'Qatar': '🇶🇦',
    'Ecuador': '🇪🇨',
    # Agregar más según necesites
}

for partido in PartidoMundial.objects.all():
    if partido.equipo_local in banderas:
        partido.bandera_local = banderas[partido.equipo_local]
    if partido.equipo_visitante in banderas:
        partido.bandera_visitante = banderas[partido.equipo_visitante]
    partido.save()
```

---

## 📊 Consumo de API con Mundial 2022

| Operación | Requests | Estado |
|-----------|----------|--------|
| Importar fixture (1 vez) | 1 | ✅ OK |
| Actualizar resultados (1 vez) | ~64 | ⚠️ Excede límite gratuito |
| **Total mínimo** | **65** | ❌ Supera 15/mes |

**Solución:** La primera importación funciona. Para actualizar resultados:
1. Hacerlo UNA sola vez manualmente
2. O cargar resultados desde el admin directamente
3. No configurar actualización automática

---

## ✅ Resumen Ejecutivo

### Lo que puedes hacer GRATIS

✅ Importar 64 partidos del Mundial 2022
✅ Ver todos los resultados históricos
✅ Probar interfaz completa
✅ Crear predicciones de prueba
✅ Calcular puntos automáticamente
✅ Generar ranking
✅ Capacitar empleados
✅ Detectar bugs

### Lo que NO puedes hacer con API Gratuita

❌ Actualización automática continua
❌ Importar partidos de múltiples torneos simultáneos
❌ Monitoreo en tiempo real

### Migración a Producción

Cuando llegue el Mundial 2026:
1. ✅ Contratar Premium ($9/mes)
2. ✅ Limpiar datos de prueba (1 comando)
3. ✅ Importar Mundial 2026 (1 comando)
4. ✅ Activar actualización automática
5. ✅ **5 minutos total**

---

**¿Listo para empezar? Ejecuta:**

```bash
python manage.py makemigrations employees
python manage.py migrate
python manage.py importar_partidos_mundial --season=2022
```

**¡Sistema de prueba funcionando en 2 minutos! ⚽🧪**
