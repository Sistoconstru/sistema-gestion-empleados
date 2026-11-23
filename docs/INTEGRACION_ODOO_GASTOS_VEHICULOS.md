# Integración SIGHU ↔ Odoo — Gastos de vehículos y cierres de cuentas

Estado en SIGHU: **listo y desplegado**. Los envíos se acumulan en cola y se
reintentan solos cada dos horas, así que cuando Odoo publique los endpoints
se ponen al día sin tocar código ni volver a cerrar nada.

Pendiente en Odoo:

| Endpoint | Para qué |
|---|---|
| `POST /sighu_sync/webhook/cierre_gastos` | Recibir un cierre de cuentas y contabilizarlo |
| `POST /sighu_sync/webhook/cierre_gastos_anulado` | Enterarse de que un cierre ya recibido dejó de valer |

Auth: `Authorization: Token <SIGHU_ODOO_WEBHOOK_TOKEN>` y
`Content-Type: application/json`, igual que `vehiculo_asignacion`,
`servicio_iniciado` y `servicio_finalizado`.

---

## 1. Qué es un cierre y por qué es lo que viaja

El conductor registra el gasto desde el celular en el momento de pagar, con
foto del recibo. Mientras la cuenta está abierta ese gasto todavía se puede
corregir, rechazar o reasignar a otro vehículo. Cuando el jefe del conductor
**cierra la cuenta**, lo que estaba abierto queda sellado: montos, renglones
y total no cambian más.

Ese cierre es lo que se le manda a Odoo, y no el gasto suelto, por una razón
práctica: contabilizar algo que todavía puede cambiar obliga a reversar
asientos. SIGHU no cierra por períodos ni a fin de mes — el jefe corta cuando
quiere, así que los cierres llegan en cualquier momento y con cualquier rango
de fechas.

SIGHU valida antes de cerrar que **no quede ningún gasto sin revisar**. Todo
lo que llega está aprobado o rechazado, nunca pendiente.

### Dos ámbitos, dos preguntas distintas

Un cierre es de un **conductor** o de un **vehículo**, y son cuentas
independientes que se cierran por separado:

- `ambito: "conductor"` → cuánto gastó esa persona y cuánto hay que
  legalizarle o pagarle.
- `ambito: "vehiculo"` → cuánto cuesta operar ese carro.

**El mismo gasto llega en los dos.** Es el punto más importante de este
contrato y está en §4.

---

## 2. `POST /sighu_sync/webhook/cierre_gastos`

Ejemplo generado con `python manage.py enviar_cierres_contabilidad --payload`.
Las placas y los `vehiculo_odoo_id` son los reales del maestro de producción
(`TIA 673` es el `3`), para que se pueda contrastar.

`placa` y `vehiculo_odoo_id` salen siempre de la misma fila de la copia que
SIGHU hace del maestro de Odoo, así que no pueden discrepar entre sí: si
alguna vez no cuadran, lo que está mal es la copia y se arregla
resincronizando, no el payload.

```json
{
  "cierre_id": "bf5671c9-1c77-4f16-a450-3b181bc44bcf",
  "ambito": "conductor",
  "moneda": "COP",
  "cerrado_en": "2026-11-23T14:16:05-05:00",
  "cerrado_por": "Diego Espinal",
  "desde": "2026-11-02",
  "hasta": "2026-11-20",
  "cantidad": 3,
  "total_costo": 138500.0,
  "total_deuda_conductor": 650000.0,
  "observaciones": "Cierre de la primera quincena de noviembre.",
  "conductor": {
    "cedula": "71391550",
    "nombre": "Carlos Andrés Restrepo"
  },
  "vehiculo": null,
  "gastos": [
    {
      "gasto_id": "e6f5a0d3-66c9-40bb-8a8f-a79b2aacc0e0",
      "fecha": "2026-11-02",
      "tipo": "combustible",
      "tipo_nombre": "Combustible",
      "monto": 120000.0,
      "descripcion": "Terpel vía Caldas",
      "estado": "aprobado",
      "cuenta_como_costo": true,
      "placa": "TIA 673",
      "vehiculo_odoo_id": 3,
      "conductor_cedula": "71391550",
      "kilometraje": null,
      "recibo_url": "https://empleados.sistemaconstruinmuniza.com/api/v1/odoo/transporte/gastos/e6f5a0d3-66c9-40bb-8a8f-a79b2aacc0e0/recibo/",
      "registrado_por": "Carlos Andrés Restrepo",
      "lo_registro_el_conductor": true
    },
    {
      "gasto_id": "fb0fbf27-080c-4af0-88c0-85565479e7a2",
      "fecha": "2026-11-11",
      "tipo": "peaje",
      "tipo_nombre": "Peaje",
      "monto": 18500.0,
      "descripcion": "Peaje Amagá",
      "estado": "aprobado",
      "cuenta_como_costo": true,
      "placa": "TIA 673",
      "vehiculo_odoo_id": 3,
      "conductor_cedula": "71391550",
      "kilometraje": 125400,
      "recibo_url": "https://empleados.sistemaconstruinmuniza.com/api/v1/odoo/transporte/gastos/fb0fbf27-080c-4af0-88c0-85565479e7a2/recibo/",
      "servicio": {
        "odoo_modelo": "stock.picking",
        "odoo_id": 385,
        "ref": "CAL/OUT/00060"
      },
      "registrado_por": "Carlos Andrés Restrepo",
      "lo_registro_el_conductor": true
    },
    {
      "gasto_id": "7aa23ff9-2b0a-4ad4-8f53-2ed762bd131e",
      "fecha": "2026-11-20",
      "tipo": "multa",
      "tipo_nombre": "Multa o comparendo",
      "monto": 650000.0,
      "descripcion": "Comparendo por exceso de velocidad",
      "estado": "aprobado",
      "cuenta_como_costo": false,
      "responsable": "conductor",
      "placa": "TIA 673",
      "vehiculo_odoo_id": 3,
      "conductor_cedula": "71391550",
      "kilometraje": null,
      "recibo_url": "https://empleados.sistemaconstruinmuniza.com/api/v1/odoo/transporte/gastos/7aa23ff9-2b0a-4ad4-8f53-2ed762bd131e/recibo/",
      "registrado_por": "Diego Espinal",
      "lo_registro_el_conductor": false
    }
  ]
}
```

### Campos del cierre

| Campo | Tipo | Notas |
|---|---|---|
| `cierre_id` | uuid | **Llave de idempotencia.** Estable para siempre. |
| `ambito` | `conductor` \| `vehiculo` | Ver §1 y §4. |
| `moneda` | str | Siempre `COP`. Va fijo para que no se asuma. |
| `cerrado_en` | ISO 8601 con offset | Cuándo se firmó. `-05:00`. |
| `cerrado_por` | str | Nombre de quien cerró. Puede venir vacío si ese usuario ya no existe. |
| `desde` / `hasta` | fecha \| null | **Informativos.** El primero y el último gasto que entraron. **No** definen qué entró: eso lo define el cierre (ver §5). |
| `cantidad` | int | Renglones, incluidos los rechazados. |
| `total_costo` | número | Suma de los renglones con `cuenta_como_costo: true`. |
| `total_deuda_conductor` | número | Suma de las multas a cargo del conductor. **No está incluida en `total_costo`.** |
| `observaciones` | str | Lo que escribió el jefe. Puede venir vacío. |
| `conductor` | objeto \| null | Presente si `ambito == "conductor"`. Se identifica por cédula. |
| `vehiculo` | objeto \| null | Presente si `ambito == "vehiculo"`. Trae `placa` y el `odoo_id` del vehículo. |
| `gastos` | lista | Los renglones. Siempre vienen en el mismo envío, nunca en una consulta aparte. |

### Campos de cada renglón

| Campo | Tipo | Notas |
|---|---|---|
| `gasto_id` | uuid | **Llave de la línea.** El mismo gasto llega en dos cierres con este mismo id (§4). |
| `fecha` | fecha | Del gasto, no del cierre. Puede ser de hace meses. |
| `tipo` | enum | `combustible`, `peaje`, `mantenimiento`, `reparacion`, `llantas`, `lavado`, `parqueadero`, `multa`, `otro`. |
| `tipo_nombre` | str | El mismo en español, para mostrar. |
| `monto` | número | Pesos. |
| `descripcion` | str | Puede venir vacía salvo en `otro`. |
| `estado` | `aprobado` \| `rechazado` | Nunca `pendiente`. |
| `cuenta_como_costo` | bool | **Si es `false`, no lo contabilicen como gasto.** Ver §3. |
| `responsable` | `empresa` \| `conductor` | **Solo presente cuando `tipo == "multa"`.** |
| `placa` | str \| null | `null` cuando el gasto no es de ningún vehículo (un almuerzo en ruta, una herramienta). |
| `vehiculo_odoo_id` | int \| null | El id del vehículo en Odoo. Es la llave buena; la placa es para leer. |
| `conductor_cedula` | str | A quién se le atribuye el gasto. Presente también en los cierres de vehículo. |
| `kilometraje` | int \| null | Opcional, lo pone el conductor. |
| `recibo_url` | url \| null | El soporte. Ver §6. |
| `servicio` | objeto | **Solo si el gasto fue por un servicio en particular.** Trae `odoo_modelo`, `odoo_id` y `ref` del documento de Odoo. |
| `registrado_por` | str | Quién digitó el registro. |
| `lo_registro_el_conductor` | bool | `false` cuando lo digitó un coordinador por él. |

---

## 3. Lo que `cuenta_como_costo: false` quiere decir

Hay dos motivos para que un renglón venga marcado así, y los dos significan
*no lo lleven al gasto del vehículo*:

1. **`estado: "rechazado"`** — el jefe lo revisó y no lo aprobó: recibo
   ilegible, gasto que no correspondía. Llega como constancia de que existió,
   y porque cuenta en `cantidad`. No es nada contablemente.

2. **`tipo: "multa"` con `responsable: "conductor"`** — es una deuda de la
   persona, no un costo de operar el vehículo. Va sumada en
   `total_deuda_conductor`, aparte de `total_costo`, porque mezclarla
   distorsiona el costo por kilómetro, que es justo lo que se quiere medir.
   Si a esto le corresponde una cuenta por cobrar al empleado o un descuento
   de nómina, es decisión de ustedes: SIGHU solo dice de quién es.

Una multa con `responsable: "empresa"` sí es costo y viene con
`cuenta_como_costo: true`.

---

## 4. El mismo gasto llega dos veces

Esto es lo único que puede salir caro si no se tiene en cuenta.

La cuenta del conductor y la del vehículo son independientes. El gasto de
combustible del ejemplo entra en las dos y cada una se cierra por su lado, en
momentos distintos. Entonces ese `gasto_id` va a llegar:

- una vez en un cierre con `ambito: "conductor"`, y
- otra vez en un cierre con `ambito: "vehiculo"`.

**`gasto_id` es el mismo en los dos**, y es estable para siempre. Es lo que
permite no contarlo dos veces.

**Decidido con Odoo el 23/11/2026:**

- **Se contabiliza el cierre de conductor.** Es a esa persona a quien se le
  legaliza, y todos los gastos pasan por un conductor —el campo es
  obligatorio en SIGHU—, así que nada se escapa por ahí. Cada renglón trae
  `vehiculo_odoo_id`, con lo que el costo se distribuye por vehículo desde
  ese mismo asiento.
- **El cierre de vehículo se guarda solo para consulta.** No genera asiento.
  Es la vista de cuánto cuesta operar ese carro, incluidos los gastos que
  un conductor hizo sobre un vehículo que no es el suyo.

SIGHU sigue mandando los dos. Que uno no se contabilice no lo vuelve
opcional: es la misma información vista por el otro lado y para eso la
guardan.

Consecuencia de haber elegido el de conductor: los gastos con `placa: null`
—un almuerzo en ruta, una herramienta— quedan cubiertos, porque igual
aparecen en el cierre de su conductor. Al revés se habrían perdido.

---

## 5. Las fechas no definen qué entró

El cierre lleva `desde` y `hasta`, pero son informativos. Lo que define qué
entró a un cierre es el cierre mismo, no el rango.

La diferencia importa: un conductor puede registrar hoy un gasto con fecha
del 2 de noviembre, cuando ya se cerró la quincena. Ese gasto **no** se cuela
en el total que alguien ya revisó y firmó: queda abierto y entra en el cierre
siguiente, que entonces va a traer un `desde` anterior a su propio período.
Es correcto y va a pasar.

O sea: no reconstruyan los renglones de un cierre filtrando por fechas. Los
renglones son los que vienen en `gastos`.

---

## 6. Los recibos

Cada renglón trae `recibo_url`, un enlace a SIGHU que Odoo descarga cuando lo
necesite:

```
GET /api/v1/odoo/transporte/gastos/<gasto_id>/recibo/
Authorization: Token <SIGHU_ODOO_TOKEN>
```

Ojo: este es el token **entrante**, el mismo con el que Odoo ya consulta
empleados y vacaciones, no el de los webhooks salientes.

Responde el archivo (JPG, PNG o PDF) como `attachment`, con el header
`X-SIGHU-Gasto` repitiendo el id. `404` si el gasto no existe o no tiene
recibo cargado.

Dos cosas que no hicimos y por qué:

- **No va la URL de S3.** Las del bucket van firmadas y caducan en una hora.
  Un soporte contable tiene que poder abrirse cuando lo pida la revisoría.
- **No va en base64,** como en beneficios de retención. Un cierre puede traer
  cuarenta fotos de recibo y el payload pesaría más que la contabilidad del
  mes.

El enlace es permanente y no caduca.

---

## 7. `POST /sighu_sync/webhook/cierre_gastos_anulado`

Un cierre se anula cuando se hizo mal: faltaba un gasto, se cerró al
conductor equivocado. Sus renglones vuelven a quedar abiertos en SIGHU y
**van a llegar otra vez en el cierre siguiente**, con los mismos `gasto_id`.

Si Odoo ya contabilizó ese cierre, hay que reversar el asiento. Sin eso, el
costo queda contado dos veces.

```json
{
  "cierre_id": "bf5671c9-1c77-4f16-a450-3b181bc44bcf",
  "ambito": "conductor",
  "anulado_en": "2026-11-23T15:40:12-05:00",
  "anulado_por": "Diego Espinal",
  "motivo": "Faltaban dos peajes del viaje a Bogotá."
}
```

El motivo es obligatorio en SIGHU: nunca llega vacío.

SIGHU solo manda este aviso de cierres que alcanzó a enviarles. Si uno se
anuló antes de llegar, no se avisa nada.

---

## 8. Respuestas que SIGHU espera

Mismo criterio que en `servicio_iniciado` / `servicio_finalizado`:

| Código | Qué entiende SIGHU | Qué hace |
|---|---|---|
| `200` | Recibido | Marca el cierre como sincronizado y guarda el `odoo_ref` del body: **el número de la legalización**, acordado el 23/11/2026. Queda a la vista en la pantalla del cierre para poder buscarlo en Odoo. Si no viniera, SIGHU acepta igual y lo deja vacío (también lee `ref`, `documento`, `move_name` o `name`). |
| `400` | El dato que mandamos no sirve | **No reintenta.** Es un bug nuestro; queda registrado como error. |
| `409` | Odoo lo rechaza a propósito (p. ej. el vehículo no tiene cuenta configurada, el período está cerrado) | **No reintenta.** Muestra el motivo al jefe que cerró, con un botón para reenviar cuando esté resuelto del lado de Odoo. |
| `5xx`, timeout, conexión caída | No llegó | Queda en cola y se reintenta cada dos horas, indefinidamente. |

En `400` y `409`, el motivo se saca del body: se busca `detail`, `error`,
`mensaje`, `message` o `motivo`. Ese texto se le muestra tal cual a la
persona que cerró la cuenta, así que conviene que se entienda sin saber de
Odoo.

**Idempotencia:** repetir un envío con el mismo `cierre_id` tiene que
responder `200` sin duplicar nada. Pasa de verdad —un timeout en el que
Odoo sí procesó— y es la situación normal, no un error.

---

## 9. Variables de entorno

Nada nuevo del lado saliente: se reusan `SIGHU_ODOO_WEBHOOK_URL` (de donde se
deriva la raíz `/sighu_sync/`) y `SIGHU_ODOO_WEBHOOK_TOKEN`.

| Variable | Para qué |
|---|---|
| `SIGHU_URL_PUBLICA` | Raíz con la que se arman los `recibo_url`. Por defecto `https://empleados.sistemaconstruinmuniza.com`. |
| `SIGHU_ODOO_TRANSPORTE_URL` | Opcional: raíz explícita de `/sighu_sync/` si no se quiere derivar. |
| `SIGHU_ODOO_TRANSPORTE_TIMEOUT` | Timeout del envío de fondo. Por defecto 30 s. |

---

## 10. Cómo probar

Del lado de SIGHU, sin mandar nada:

```bash
# El JSON exacto que viajaría, de los cierres que están en cola
python manage.py enviar_cierres_contabilidad --payload

# Uno en particular, aunque ya esté enviado
python manage.py enviar_cierres_contabilidad --payload --cierre <uuid>

# Qué se mandaría, sin el JSON completo
python manage.py enviar_cierres_contabilidad --dry-run

# Mandarlo de verdad (es lo que corre el scheduler cada 2 h)
python manage.py enviar_cierres_contabilidad
```

El envío también se intenta en el momento de cerrar la cuenta, con un timeout
de 8 segundos, para que el jefe sepa ahí mismo si llegó. Si no llega, el
cierre vale igual: queda en cola.

---

## 11. Lo que SIGHU sigue haciendo y no viaja

Para que quede claro el límite:

- La **revisión** de los gastos (aprobar o rechazar) es de SIGHU, la hace el
  jefe del conductor y no se le consulta a Odoo.
- Los **documentos del vehículo** (SOAT, tecnomecánica, póliza, impuesto,
  semaforización) y sus vencimientos son de SIGHU y no viajan.
- El **maestro de vehículos** sigue siendo de Odoo: SIGHU lo copia cada 6 h.
- Las cuentas **abiertas** no se envían. Solo los cierres.
