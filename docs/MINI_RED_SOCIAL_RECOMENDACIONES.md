# Mini Red Social Corporativa - Recomendaciones de Implementación

## Resumen Ejecutivo

Basado en tu arquitectura actual (Django + PostgreSQL + Bootstrap 5), recomiendo una implementación **progresiva y modular** que aproveche tu infraestructura existente, especialmente:

- ✅ Sistema de **notificaciones** ya implementado
- ✅ Sistema de **autenticación** y **empleados** estructurado
- ✅ **Bootstrap 5** para interfaz responsive
- ✅ **PostgreSQL** con soporte para datos complejos (JSON, arrays)

---

## 1. ARQUITECTURA PROPUESTA

### Stack Recomendado

```
Backend:
├─ Django 4.2+
├─ Django REST Framework (para APIs internas)
├─ Channels + Redis (para chat en tiempo real - OPCIONAL, fase 2)
├─ Pillow (manejo de imágenes)
└─ python-dateutil (cálculos de subastas)

Frontend:
├─ Bootstrap 5 (ya tienes)
├─ Alpine.js o HTMX (interactividad sin JS pesado)
├─ TailwindCSS (opcional, para estilo moderno)
└─ WebSockets (via Channels para chat real-time)

Base de Datos:
├─ PostgreSQL (ya tienes)
├─ JSONField para metadatos de productos
└─ Full-text search para búsqueda de artículos

Terceros:
├─ Pillow (imágenes)
├─ django-filter (búsqueda avanzada)
├─ django-pagination (paginación)
└─ Celery + Redis (tareas asincrónicas - OPCIONAL)
```

---

## 2. NUEVAS APLICACIONES DJANGO A CREAR

### Aplicación 1: `marketplace`
**Responsabilidad:** Gestionar productos, listados y operaciones de venta

**Modelos principales:**
```python
# Productos
Producto
├─ vendedor (FK → Empleado)
├─ titulo
├─ descripcion
├─ categoria
├─ precio_inicial
├─ imagen (ImageField)
├─ estado (activo/vendido/cancelado)
├─ tipo (venta_normal/regalo/subasta)
├─ fecha_creacion
└─ fecha_actualizacion

# Categorías
Categoria
├─ nombre
├─ descripcion
└─ icono

# Transacciones de Venta Normal
Venta
├─ producto (FK → Producto)
├─ vendedor (FK → Empleado)
├─ comprador (FK → Empleado)
├─ precio_final
├─ estado (pendiente/completada/cancelada)
├─ fecha_venta
└─ calificacion (1-5 estrellas)

# Subastas
Subasta
├─ producto (FK → Producto)
├─ vendedor (FK → Empleado)
├─ precio_inicial
├─ fecha_inicio
├─ fecha_fin
├─ puja_actual_precio
├─ pujador_actual (FK → Empleado)
├─ estado (activa/finalizada/cancelada)
└─ ganador (FK → Empleado, null si no hay pujas)

# Ofertas en Subastas
PujaSubasta
├─ subasta (FK → Subasta)
├─ pujador (FK → Empleado)
├─ monto
├─ fecha_puja
└─ es_puja_actual (boolean)

# Regalos
Regalo
├─ producto (FK → Producto)
├─ donante (FK → Empleado)
├─ receptor (FK → Empleado)
├─ estado (pendiente/aceptado/rechazado)
├─ fecha_ofrecimiento
└─ fecha_aceptacion
```

### Aplicación 2: `messaging` (Chat/Inbox)
**Responsabilidad:** Comunicación directa entre usuarios

**Modelos principales:**
```python
# Conversaciones
Conversacion
├─ participantes (M2M → Empleado)
├─ titulo (opcional, para referencia)
├─ contexto (venta/regalo/pregunta_producto)
├─ producto_referencia (FK → Producto, optional)
├─ fecha_creacion
├─ fecha_ultima_actividad
└─ archivada (boolean)

# Mensajes
Mensaje
├─ conversacion (FK → Conversacion)
├─ remitente (FK → Empleado)
├─ contenido
├─ adjunto (FileField, optional)
├─ leido (boolean)
├─ fecha_envio
└─ fecha_lectura (null si no leído)

# Lectura de Mensajes
LecturaConversacion (tracker de quién leyó qué)
├─ conversacion (FK → Conversacion)
├─ empleado (FK → Empleado)
├─ ultimo_mensaje_leido (FK → Mensaje)
└─ fecha_actualizacion
```

### Aplicación 3: Extensión a `notifications`
**Responsabilidad:** Notificaciones específicas del marketplace

**Nuevos Tipos de Notificación:**
```
- "NUEVO_PRODUCTO_SUBASTA" → Producto en subasta disponible
- "NUEVA_PUJA_SUPERADA" → Tu puja fue superada
- "NUEVO_MENSAJE" → Tienes un mensaje no leído
- "PRODUCTO_DISPONIBLE" → El producto que buscas está disponible
- "VENTA_COMPLETADA" → Tu venta fue completada
- "REGALO_RECIBIDO" → Te ofrecieron un regalo
- "PUJA_GANADA" → Ganaste la subasta
- "PUJA_PERDIDA" → Perdiste la subasta
```

---

## 3. ESTRUCTURA DE CARPETAS PROPUESTA

```
apps/
├── marketplace/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── activar_subastas_vencidas.py
│   ├── templates/
│   │   ├── marketplace/
│   │   │   ├── index.html (listado de productos)
│   │   │   ├── producto_detalle.html
│   │   │   ├── crear_producto.html
│   │   │   ├── mi_tienda.html (mis productos vendidos/activos)
│   │   │   ├── compras.html (mis compras)
│   │   │   └── subastas/
│   │   │       ├── listar.html
│   │   │       ├── detalle.html
│   │   │       └── pujar.html
│   │   └── components/
│   │       ├── producto_card.html
│   │       ├── puja_form.html
│   │       └── calificacion.html
│   ├── static/marketplace/
│   │   ├── css/marketplace.css
│   │   └── js/
│   │       ├── subastas.js (actualización en tiempo real)
│   │       └── busqueda.js
│   ├── filters.py (búsqueda avanzada)
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── messaging/
│   ├── migrations/
│   ├── templates/
│   │   ├── messaging/
│   │   │   ├── inbox.html (lista de conversaciones)
│   │   │   ├── conversacion.html (chat)
│   │   │   └── nueva_conversacion.html
│   │   └── components/
│   │       ├── mensaje_item.html
│   │       └── conversacion_header.html
│   ├── static/messaging/
│   │   ├── css/chat.css
│   │   └── js/chat.js
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── consumers.py (WebSockets para chat real-time)
│   └── apps.py
│
└── notifications/ (EXTENSIÓN EXISTENTE)
    └── management/
        └── commands/
            └── enviar_notificaciones_marketplace.py

templates/
├── components/
│   └── notificaciones_badge.html (campana con contador)
└── base.html (actualizar con nuevas rutas)

static/
├── js/
│   ├── notificaciones.js (actualizar contador en tiempo real)
│   └── marketplace-rtc.js (real-time con WebSockets)
└── css/
    └── marketplace-theme.css
```

---

## 4. IMPLEMENTACIÓN POR FASES

### FASE 1: MVP (2-3 semanas)
**Objetivo:** Marketplace funcional básico

**Qué incluir:**
1. ✅ Modelos de Producto, Venta, Subasta, Regalo
2. ✅ Vistas para:
   - Listar productos (con filtros)
   - Ver detalle de producto
   - Crear producto
   - Realizar venta simple (comprador confirma, vendedor confirma)
   - Ver mis productos/compras
3. ✅ Sistema de búsqueda básico
4. ✅ Sistema de rating/calificación simple
5. ✅ Notificaciones cuando:
   - Alguien compra un producto
   - Alguien hace oferta en subasta

**NO incluir aún:**
- ❌ Chat en tiempo real (usar formularios POST simples)
- ❌ WebSockets
- ❌ Imágenes múltiples
- ❌ Sistema de pago integrado

---

### FASE 2: Chat & Mejoras (2-3 semanas)
**Objetivo:** Comunicación fluida entre usuarios

**Qué añadir:**
1. ✅ Modelo Conversacion y Mensaje
2. ✅ Vista Inbox (lista de chats)
3. ✅ Vista Chat (conversación individual)
4. ✅ Notificaciones de nuevos mensajes
5. ✅ AJAX para enviar mensajes sin recargar
6. ✅ Indicador de "escribiendo..."
7. ✅ Lectura de mensajes

**Mejoras opcionales:**
- ❌ WebSockets para tiempo real (vs AJAX polling)
- ❌ Búsqueda fulltext en mensajes
- ❌ Adjuntos (imágenes/documentos)

---

### FASE 3: Subastas Avanzadas (2-3 semanas)
**Objetivo:** Subastas robustas con historial

**Qué añadir:**
1. ✅ Historial completo de pujas
2. ✅ Notificaciones "puja superada"
3. ✅ Auto-cierre de subastas por tiempo (Celery task)
4. ✅ Puja automática (máximo permisible)
5. ✅ Validación de pujas en tiempo real

---

### FASE 4: Escalabilidad (Según demanda)
**Objetivo:** Sistema robusto y escalable

**Qué añadir:**
1. ✅ WebSockets con Channels + Redis
2. ✅ Búsqueda fulltext (PostgreSQL pg_trgm)
3. ✅ Caché Redis para productos populares
4. ✅ Colas Celery para tareas pesadas
5. ✅ Moderación de contenido

---

## 5. TECNOLOGÍAS RECOMENDADAS POR COMPONENTE

### Chat (Messaging)

**Opción A: Sencilla (AJAX Polling) - RECOMENDADO PARA FASE 1**
```
Ventajas:
- ✅ Fácil de implementar
- ✅ No requiere dependencias externas
- ✅ Funciona con infraestructura actual
- ✅ Compatible con WebSocket en futuro

Desventajas:
- ❌ Pequeño delay (500ms-1s) en mensajes
- ❌ Más uso de ancho de banda

Implementación:
- AJAX cada 1-2 segundos
- Endpoint: /api/messages/nuevos/?conversacion_id=X
```

**Opción B: Tiempo Real (WebSockets + Channels) - FASE 2-3**
```
Ventajas:
- ✅ Chat en tiempo real (< 100ms latency)
- ✅ Escalable a muchos usuarios
- ✅ Indicadores de "escribiendo"

Desventajas:
- ❌ Requiere Channels + Redis
- ❌ Más complejo de configurar
- ❌ Mayor consumo de recursos

Librerías:
- django-channels
- redis
- channels-redis
```

### Subastas

**Historial de Pujas:**
```python
# Modelo: PujaSubasta con timestamp y validación
# Endpoint: GET /subastas/{id}/pujas/ (ordenado por fecha DESC)

# Vista debe mostrar:
- Pujador (nombre + avatar)
- Monto
- Fecha/hora
- Estado (puja actual / superada / ganadora)
```

**Actualización en Tiempo Real:**
```
Opción A (Simple): AJAX cada 2-3 segundos
Opción B (Avanzado): WebSocket para actualización instantánea
```

### Marketplace General

**Búsqueda:**
```python
# Usar django-filter para búsqueda avanzada
# Filtros:
- Categoría
- Precio (rango)
- Tipo (venta/regalo/subasta)
- Ordenar por (fecha, precio, relevancia)
- Buscar texto libre (título + descripción)

# Para búsqueda fulltext (fase posterior):
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchVector
```

---

## 6. DEPENDENCIAS A INSTALAR

```bash
# Instalaciones recomendadas
pip install pillow              # Manejo de imágenes
pip install django-filter       # Búsqueda/filtros
pip install django-extensions   # Shell plus útil
pip install celery              # Tareas async (opcional, fase 3+)
pip install redis               # Cache + Celery (opcional)
pip install channels            # WebSockets (opcional, fase 3+)
pip install channels-redis      # Redis backend para Channels

# Para desarrollo
pip install django-debug-toolbar # Debug
pip install factory-boy          # Fixtures para testing
```

---

## 7. FLUJOS DE USUARIO PRINCIPALES

### Flujo 1: Venta Normal

```
1. Vendedor crea producto (título, desc, precio, imagen)
   → Producto estado = "activo"
   → Notificación: "Nuevo producto: [Título]"

2. Otros empleados ven el producto en el marketplace
   → Pueden hacer preguntas via chat

3. Comprador decide comprar
   → Crea orden (Venta)
   → Estado = "pendiente_vendedor"
   → Notificación vendedor: "Alguien quiere comprar tu [Producto]"

4. Vendedor confirma venta
   → Estado = "pendiente_comprador"
   → Notificación comprador: "El vendedor confirmó, puedes pasar a recoger"

5. Comprador confirma recepción
   → Estado = "completada"
   → Ambos pueden calificarse

6. Chat histórico se mantiene como referencia
```

### Flujo 2: Subasta

```
1. Vendedor crea subasta
   → Producto tipo = "subasta"
   → Subasta estado = "activa"
   → fecha_fin = hoy + X días
   → Notificación: "Nueva subasta: [Producto] hasta [fecha]"

2. Empleados ven subasta y realizan pujas
   → Cada puja:
     - Validar: monto > puja_actual + incremento_mínimo
     - Crear PujaSubasta
     - Actualizar puja_actual_precio
     - Notificación anterior pujador: "Tu puja fue superada"
     - Si es puja automática, intentar contra-puja

3. Finalización automática (02:00 AM vía Celery)
   → Si fecha_fin ha pasado:
     - Estado = "finalizada"
     - ganador = último pujador
     - Crear Venta automática
     - Notificación ganador: "Ganaste la subasta"
     - Notificación perdedores: "Alguien ganó la subasta"

4. Chat entre ganador y vendedor para coordinación entrega
```

### Flujo 3: Regalo

```
1. Donante crea regalo (producto, selecciona receptor)
   → Regalo estado = "pendiente"
   → Notificación receptor: "[Nombre] te ofreció un regalo"

2. Receptor puede:
   - Aceptar → estado = "aceptado"
   - Rechazar → estado = "rechazado"

3. Historial de regalos visible en perfil
```

---

## 8. SEGURIDAD & VALIDACIONES

### Validaciones Críticas

```python
# Pujas
- Validar que puja > puja_actual + incremento_mínimo
- Validar que subasta está activa
- Validar que pujador no sea el vendedor
- Validar que no haya pujas después de fecha_fin

# Ventas
- Validar que producto está en estado "activo"
- Validar que comprador ≠ vendedor
- Validar que producto no está ya vendido

# Regalos
- Validar que receptor existe y es activo
- Validar que donante ≠ receptor

# Permisos
- Solo vendedor puede ver stats de su tienda
- Solo participantes de conversación pueden ver mensajes
- Solo comprador/vendedor pueden calificar mutuamente
```

### Datos Sensibles

```python
# Proteger:
- Precios de pujas (solo vendedor + pujadores)
- Datos personales (email, teléfono)
- Historial de transacciones (solo usuario + admin)

# Logs
- Registrar todas las transacciones importantes
- Auditoría de modificaciones de precios
```

---

## 9. CRONOGRAMA SUGERIDO

| Fase | Semanas | Funcionalidades |
|------|---------|-----------------|
| **MVP** | 2-3 | Productos, Venta simple, Subastas básicas |
| **Chat** | 2-3 | Mensajería, Notificaciones, Inbox |
| **Subastas Avanzadas** | 2-3 | Historial, Auto-cierre, Pujas automáticas |
| **Escalabilidad** | 2-4 | WebSockets, Caché, Búsqueda avanzada |
| **Moderación & Análisis** | 2+ | Reportes, Sistema de reputación |

**Duración Total Estimada:** 3-4 meses para un MVP completo y funcional

---

## 10. COMPARATIVA: CONSTRUIR vs USAR PLATAFORMA EXISTENTE

### Opción 1: CONSTRUIR PROPIO (RECOMENDADO)

**Ventajas:**
- ✅ Control total de datos y características
- ✅ Integración perfecta con tu sistema de empleados
- ✅ Marca corporativa consistente
- ✅ Escalable según tus necesidades
- ✅ Menor costo de licencias (a largo plazo)

**Desventajas:**
- ❌ Mayor esfuerzo inicial
- ❌ Necesitas mantenimiento continuo
- ❌ Requiere expertos en Django/React

---

### Opción 2: USAR PLATAFORMA TERCERA (ej: Intranet Kit, Employees Hub)

**Ventajas:**
- ✅ Rápido para implementar
- ✅ Características probadas
- ✅ Soporte profesional

**Desventajas:**
- ❌ Menos control
- ❌ Integración complicada
- ❌ Costo de suscripción permanente
- ❌ Datos en servidores de terceros

---

## RECOMENDACIÓN FINAL

### Implementa en DJANGO PROPIO, con esta estrategia:

1. **Semana 1-2:** Setup de modelos + Vistas básicas (Fase 1 MVP)
2. **Semana 3-4:** Mensajería simple con AJAX (Fase 2A)
3. **Semana 5-6:** Subastas con actualización automática (Fase 2B)
4. **Semana 7-8+:** Mejoras y escalabilidad según feedback

### Por qué esta es LA MEJOR OPCIÓN para TI:

1. **Ya tienes la base:** Django, PostgreSQL, autenticación, notificaciones
2. **Control total:** Personalizables según necesidades corporativas
3. **Integración perfecta:** Con tu sistema de empleados y evaluaciones
4. **Crecimiento gradual:** Agrega features incrementalmente
5. **Bajo costo:** Solo pagar hosting, no suscripciones de terceros

---

## Siguiente Paso

¿Quieres que comience a implementar la **Fase 1 (MVP del Marketplace)**?

Si es así, necesito confirmar:
1. ¿Empezamos con `app marketplace`?
2. ¿Descartas WebSockets por ahora (AJAX en Fase 2)?
3. ¿Categorías predefinidas o permitir que usuarios creen?
4. ¿Sistema de calificaciones tipo estrellas (1-5)?
5. ¿Precio mínimo/máximo para productos?

---

**Documento creado:** 2025-11-26
**Versión:** 1.0
