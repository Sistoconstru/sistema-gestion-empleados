# Integración SIGHU ↔ Odoo — Vacaciones

Este documento cubre el contrato de los endpoints de vacaciones que SIGHU expone
para Odoo. Todos requieren `Authorization: Token <SIGHU_ODOO_TOKEN>`.

## Flujos soportados

Hay dos rutas posibles para que una solicitud de vacaciones llegue a SIGHU:

### A) Origen SIGHU → Odoo (flujo del jefe)

El jefe directo o un rol autorizado crea la solicitud en SIGHU. SIGHU la envía
a Odoo para validación de saldo y aprobación por RRHH. Odoo notifica de vuelta
cuando el estado cambia.

- Push: SIGHU → webhook Odoo (fuera del alcance de este doc).
- Callback: Odoo → `POST /api/v1/odoo/vacaciones/estado/` (endpoint 1).

### B) Origen Odoo → SIGHU (flujo de RRHH)

RRHH crea la solicitud directamente en Odoo. Aplica a dos casos:

- **Vacaciones en tiempo** (días libres) creadas por RRHH sin pasar por el jefe.
- **Compensaciones en dinero** (`tipo="dinero"`), que por naturaleza solo se
  originan en Odoo por RRHH.

Al aprobar/cancelar, Odoo llama a SIGHU. Es el mismo endpoint para ambos casos.

- Callback único: Odoo → `POST /api/v1/odoo/vacaciones/importar/` (endpoint 2).

---

## Endpoint 1 — `POST /api/v1/odoo/vacaciones/estado/`

Actualiza el estado de una solicitud que YA existe en SIGHU (identificada por
`leave_id_odoo`). Si no existe → 404.

### Request

```json
{
  "leave_id": 12345,
  "estado": "aprobada",           // "aprobada" | "rechazada" | "cancelada"
  "motivo": "opcional",
  "aprobada_por": "user@odoo",
  "fecha_estado": "2026-06-30T14:00:00Z"
}
```

> El saldo NO se envía en este payload. SIGHU lo consulta bajo demanda desde
> el endpoint `GET /sighu_sync/vacaciones/saldos` que expone Odoo. Ver
> sección "Saldo de días disponibles" al final.

### Respuestas

- `200 { status: "recibido", ... }` — el estado cambió.
- `200 { status: "ya_procesado", ... }` — el estado enviado coincide con el actual (idempotente).
- `400` — payload inválido.
- `404` — `leave_id` no existe en SIGHU.

---

## Endpoint 2 — `POST /api/v1/odoo/vacaciones/importar/`

Importa una solicitud creada directamente en Odoo. Soporta **dos tipos** con
claves de upsert distintas:

| tipo | Clave de upsert | Rango de fechas |
|---|---|---|
| `tiempo` | `leave_id` | Requerido |
| `dinero` (o `pago_dinero`) | `compensacion_id` | No aplica (nulo) |

**Nunca mezclar**: si `tipo="dinero"`, no envíes `leave_id`. Y viceversa.

### Request — tipo=tiempo

```json
{
  "tipo": "tiempo",
  "leave_id": 12345,                // clave de idempotencia
  "sighu_uuid": "uuid-empleado",    // opcional
  "cedula": "1035831455",           // opcional (uno de los dos requerido al CREAR)
  "fecha_inicio": "2026-08-01",
  "fecha_fin": "2026-08-15",
  "dias": 10,                       // informativo
  "estado": "aprobada",             // "aprobada" | "cancelada"
  "motivo": "opcional",
  "aprobada_por": "user@odoo",
  "fecha_estado": "2026-06-30T14:00:00Z"
}
```

### Request — tipo=dinero (compensación)

```json
{
  "tipo": "dinero",
  "compensacion_id": 1635,          // clave de idempotencia (distinta de leave_id)
  "leave_id": null,                 // debe ir nulo o ausente para tipo=dinero
  "sighu_uuid": "uuid-empleado",    // opcional
  "cedula": "1035831455",           // opcional (uno de los dos requerido al CREAR)
  "dias": 7.0,                      // días compensados (informativo)
  "valor": 408544,                  // valor pagado en pesos (evidencia)
  "fecha": "2026-07-01",            // periodo del lote de nómina
  "fecha_inicio": null,             // NO aplica: no hay disfrute de días
  "fecha_fin": null,                // NO aplica
  "estado": "aprobada",             // "aprobada" (aplicada) | "cancelada" (reversada)
  "motivo": "Compensación de vacaciones en dinero (7 días) aplicada por RRHH.",
  "aprobada_por": "rrhh@empresa.com"
}
```

### Respuestas

- `201 { status: "creado", sighu_uuid, leave_id|compensacion_id, estado_local }` — nueva solicitud creada.
- `200 { status: "actualizado", ... }` — solicitud existente actualizada (cambió estado).
- `200 { status: "ya_procesado", ... }` — el estado enviado coincide (idempotente).
- `400` — payload inválido (clave faltante, fechas inválidas, tipo/estado no permitido).
- `404` — empleado no encontrado por `sighu_uuid` ni por `cedula`.

### Comportamiento clave

- **Identificación del empleado:** primero por `sighu_uuid`; si no matchea, por `cedula`
  (=`numero_documento`). Solo se requiere al CREAR. En un update por reintento se
  puede omitir.
- **Idempotencia:** por `leave_id` cuando `tipo=tiempo`, por `compensacion_id` cuando
  `tipo=dinero`. Reintentos del cron de Odoo NO duplican registros ni notificaciones.
  Nunca colisionan porque son campos distintos.
- **`jefe_solicitante`:** siempre NULL en este flujo (nació en Odoo, no en SIGHU).
- **Cancelación posterior:** llamar al mismo endpoint con `estado="cancelada"`,
  manteniendo la misma clave de upsert (`leave_id` o `compensacion_id`).
- **Notificación al empleado:** cada transición terminal dispara una notificación
  in-app específica para cada tipo (`vacacion_aprobada` vs `vacacion_comp_aprobada`).
  Idempotente: `ya_procesado` no notifica.
- **Estados permitidos:** solo `aprobada` y `cancelada`. Los estados intermedios
  (`borrador`, `enviada_pendiente_rrhh`) no aplican porque las solicitudes creadas
  en Odoo llegan a SIGHU solo cuando ya son un hecho.

---

## Saldo de días disponibles

**Odoo es la fuente autoritativa del saldo.** SIGHU NO calcula saldo — lo
muestra tal como lo entrega Odoo (que ya considera vacaciones en tiempo + dinero).

Modelo elegido: **pull bajo demanda desde SIGHU**. Cuando el empleado abre
"Mis vacaciones", SIGHU llama al endpoint expuesto por Odoo. Con cache local de
5 minutos para evitar hammering en recargas. Si Odoo no responde, se muestra el
último saldo conocido con un aviso.

### Ventajas del pull vs push

- Si SIGHU está caído, no hay que encolar ni reintentar en Odoo — el próximo
  request lo trae.
- SIGHU decide su frescura (bajo demanda cuando el empleado abre la vista).
- Odoo solo expone un dato; no necesita conocer el contrato de escritura.
- Reutiliza el token de auth ya establecido (`SIGHU_ODOO_WEBHOOK_TOKEN`).

### Condición operativa

La acumulación diaria de saldos en Odoo debe correr **antes** de las 2:30 AM
(propuesto: 2:00 AM) para que las consultas de la mañana no muestren un día
atrasado. Es un cambio en un cron de Odoo, lo asume el equipo de Odoo.

### Endpoint expuesto por Odoo

```
GET <base>/sighu_sync/vacaciones/saldos
Authorization: Token <SIGHU_ODOO_WEBHOOK_TOKEN>

Params opcionales:
  ?sighu_uuid=<uuid>    ← consulta un solo empleado
  ?cedula=<numero>      ← alternativa por cédula

Respuesta 200:
{
  "fecha_corte": "2026-07-22",
  "saldos": [
    {
      "sighu_uuid": "492066c9-260f-4696-8be0-576defdd8f5a",
      "cedula": "66964818",
      "nombre": "Adriana Patricia Guarin Giraldo",
      "saldo_dias_disponibles": 12.5
    }
    // ... más empleados si es consulta bulk
  ]
}
```

Cuando la consulta es puntual (`?sighu_uuid=X`), se espera 0 o 1 elementos en
`saldos`. Cuando es bulk (sin params), retorna todos los empleados.

### Configuración en SIGHU

- **Env var opcional** `SIGHU_ODOO_SALDOS_URL`: URL completa. Si no está,
  SIGHU la deriva de `SIGHU_ODOO_WEBHOOK_URL` reemplazando `/empleado` por
  `/vacaciones/saldos`.
- **Env var opcional** `SIGHU_ODOO_SALDOS_TIMEOUT`: segundos (default `3`).
- **Auth**: reutiliza `SIGHU_ODOO_WEBHOOK_TOKEN`. No hay token separado.

### Comportamiento del cache y fallos

- SIGHU pide a Odoo si el último saldo del empleado es de hace **> 5 minutos**
  (o si nunca se ha pedido).
- Si la respuesta es exitosa: actualiza `Empleado.saldo_vacaciones_dias` y
  `saldo_vacaciones_actualizado = now()`.
- Si Odoo falla (timeout, 5xx, JSON inválido, empleado sin saldo): NO se toca el
  cache. La vista muestra el último saldo conocido + aviso "no se pudo
  actualizar en este momento".
- Si nunca se ha obtenido saldo Y Odoo falla ahora: se muestra "— sin sincronizar —"
  con una explicación al empleado.

### Actualizaciones fuera de eventos de vacaciones

Cierres anuales, ajustes manuales u otras razones que modifiquen el saldo en
Odoo sin generar una vacación se reflejan automáticamente en SIGHU en la
siguiente consulta bajo demanda (cache de 5 minutos como máximo).

---

## Ejemplos

### Ejemplo 1 — crear vacación en tiempo

```http
POST /api/v1/odoo/vacaciones/importar/
Authorization: Token <SIGHU_ODOO_TOKEN>
Content-Type: application/json

{
  "tipo": "tiempo",
  "leave_id": 8891,
  "cedula": "1035831455",
  "fecha_inicio": "2026-08-01",
  "fecha_fin": "2026-08-10",
  "dias": 10,
  "estado": "aprobada",
  "aprobada_por": "rrhh@empresa.com"
}
```

Respuesta:
```json
{ "status": "creado", "sighu_uuid": "b1c2...", "leave_id": 8891, "estado_local": "aprobada_rrhh" }
```

### Ejemplo 2 — crear compensación en dinero

```http
POST /api/v1/odoo/vacaciones/importar/
Authorization: Token <SIGHU_ODOO_TOKEN>
Content-Type: application/json

{
  "tipo": "dinero",
  "compensacion_id": 1635,
  "cedula": "1035831455",
  "dias": 7.0,
  "valor": 408544,
  "fecha": "2026-07-01",
  "estado": "aprobada",
  "motivo": "Compensación de vacaciones en dinero (7 días) aplicada por RRHH.",
  "aprobada_por": "rrhh@empresa.com"
}
```

Respuesta:
```json
{ "status": "creado", "sighu_uuid": "b1c2...", "compensacion_id": 1635, "estado_local": "aprobada_rrhh" }
```

### Ejemplo 3 — reversar la compensación (RRHH la anula)

```http
POST /api/v1/odoo/vacaciones/importar/
Authorization: Token <SIGHU_ODOO_TOKEN>
Content-Type: application/json

{
  "tipo": "dinero",
  "compensacion_id": 1635,
  "estado": "cancelada",
  "motivo": "Reversada por RRHH — error en el lote de nómina."
}
```

Respuesta:
```json
{ "status": "actualizado", "sighu_uuid": "b1c2...", "compensacion_id": 1635, "estado_local": "cancelada_rrhh" }
```
