# Permisos por jerarquía: quién ve y gestiona a quién

Este documento describe cómo SIGHU decide qué empleados puede ver o gestionar
un jefe, coordinador o director según lo que se quiere controlar (asistencia,
novedades de nómina, vacaciones, perfiles). La fuente de verdad es el código;
cada regla lleva la función donde vive.

Se escribió después de una regresión: al endurecer los permisos de
`apps/reports` (octubre 2026) se restringió a staff `NovedadesAccionView`, que
es también la vista con la que los **directores** aprueban horas extras. Los
directores no son `is_staff`, así que su bandeja abría pero al aprobar recibían
un 403. Ver la sección [Lección: staff vs. jerarquía](#lección-staff-vs-jerarquía).

---

## 1. Roles

| Rol | Cómo se reconoce | Alcance |
|---|---|---|
| **Superusuario** | `user.is_superuser` | Todo. |
| **RRHH / Admin** | `user.is_staff` | Todo lo administrativo: listados globales, reportes, exports. Vistas protegidas con `StaffRequiredMixin` o `@staff_member_required`. |
| **Director** | Empleado que tiene **jefes o coordinadores** reportándole por `jefe_directo` | Aprueba novedades registradas por esos coordinadores. **No es staff.** |
| **Jefe / Coordinador** | Empleado que tiene **subalternos** reportándole por `jefe_directo` | Su equipo directo: asistencia, novedades, vacaciones. **No es staff.** |
| **Empleado** | Cualquier usuario con ficha de empleado | Solo lo propio: perfil, documentos, vacaciones, familia. |

"Director" y "coordinador" **no son un campo ni un rol del sistema**: se deducen
de la estructura de `jefe_directo`. Una misma persona puede ser coordinador de
su equipo y, a la vez, director de otros coordinadores.

---

## 2. La relación base: `HistorialCargo.jefe_directo`

Casi todas las reglas usan la relación **por persona**:

```
HistorialCargo(empleado=X, activo=True, jefe_directo=Y)   →   Y es jefe directo de X
```

- Solo cuenta el registro **activo** (`activo=True`).
- Es una relación **directa**, no transitiva: un director no ve a los
  operarios de sus coordinadores, salvo donde se indica.
- Se asigna a mano en la ficha. No se deduce del cargo.

La estructura de cargos (`Cargo.cargo_jefe`, `nivel_jerarquico`) **no se usa
para permisos** en ninguna vista. Ver la sección 5 para la que la usaba.

---

## 3. Reglas por lo que se controla

### 3.1 Asistencia diaria

| Quién | A quién registra | Código |
|---|---|---|
| Jefe | Subalternos directos activos (`estado` `999` o `p-prue`) | `_equipo_del_jefe`, `_subalternos_activos_de` |
| Encargado por ausencia | El equipo de un jefe que lo designó **y que ese día está ausente** | `_jefes_ausentes_reemplazados` |
| Encargado permanente | El equipo de un jefe que lo designó, **todos los días** | `_jefes_con_delegacion_permanente` |

Exclusiones:

- Empleados cuyo cargo tiene `excluido_control_asistencia=True`
  (típicamente directores) no aparecen en el tablero de su jefe.
- Cuentan como ausencia del jefe: `ausente`, `permiso`,
  `permiso_no_remunerado`, `incapacidad`, `en_vacaciones`. Llegar tarde
  (`retardo`) no lo hace ausente.

Delegación permanente — el jefe delega todos los días si:

- su equipo tiene **30 o más** subalternos activos
  (`UMBRAL_EQUIPO_GRANDE_ENCARGADO`), **o**
- tiene el flag `Empleado.delegacion_asistencia_permanente=True`, que RRHH
  activa para equipos pequeños que igual necesitan delegar.

### 3.2 Novedades de nómina (horas extras y recargos)

Flujo en dos niveles: el **coordinador registra**, el **director aprueba**.

| Paso | Quién | Alcance | Código |
|---|---|---|---|
| Registrar | Coordinador / jefe | Su equipo directo, **sin** empleados del área Administración (no generan horas extras) | `novedades_semana`, `_equipo_del_jefe` |
| Exportar su semana | Coordinador / jefe | Su equipo directo | `novedades_export_excel_jefe` |
| Ver pendientes | Director | Novedades **pendientes** registradas por quienes le reportan directamente | `novedades_aprobacion`, `_novedades_pendientes_para_director` |
| **Aprobar / rechazar** | Director | Las mismas: el queryset se acota por `registrado_por.jefe_directo = director` | **`NovedadesAccionView`** |
| Aprobar / rechazar | RRHH (`is_staff`) | Cualquier novedad pendiente | `NovedadesAccionView` |
| Vista global y export | RRHH | Todas | `novedades_rrhh_semana`, `novedades_rrhh_export_excel`, `NovedadesReportView` |

El director aprueba lo que **registró** su coordinador, no lo que corresponde a
sus empleados: la relación que se mira es `registrado_por`, no `empleado`.

### 3.3 Vacaciones

| Quién | Puede solicitar o editar las vacaciones de | Código |
|---|---|---|
| RRHH | Cualquiera | `_puede_solicitar_vacacion_para` |
| Jefe directo | Sus subalternos directos | `_puede_solicitar_vacacion_para` |
| Jefe | Ver el tablero de su equipo | `vacaciones_equipo` → `_equipo_del_jefe` |

Un jefe que además es staff ve en el tablero de equipo **solo a su equipo**; la
vista de todos los activos es la administrativa, aparte.

### 3.4 Perfiles de empleados

| Vista | Quién la abre | Regla |
|---|---|---|
| `EmpleadoPerfilView` (`/empleados/perfil/<pk>/`) | El propio empleado o staff | `empleado.usuario == request.user or is_staff` |
| `EmpleadoDetailSupervisorView` (`/empleados/supervisor/<pk>/`) | Staff, o alguien **por encima en la cadena de `jefe_directo`** (su jefe, el jefe de su jefe…) | `_es_superior_en_cadena` |
| `EmpleadoDetailView` (`/empleados/<pk>/`) | Solo staff | `StaffRequiredMixin` |
| `EmpleadoListView` (`/empleados/`) | Solo staff | `StaffRequiredMixin` — trae la cédula de toda la nómina |

### 3.5 Evaluaciones de desempeño

El evaluador es el `jefe_directo` asignado en `HistorialCargo`. El código lo
dice explícitamente: *usa el jefe_directo asignado manualmente, no busca por
cargo*. Ver `docs/AUTOMATIZACION_EVALUACIONES.md`.

---

## 4. Lo que ningún jefe ve

Exclusivo de staff, sin excepción por jerarquía:

- Listado completo de empleados y la ficha administrativa de cualquiera.
- Todo `apps/reports` (asistencia, evaluaciones, novedades globales, SENA),
  **salvo** `NovedadesAccionView`.
- Exports masivos (`/empleados/export/`, familiares, novedades de RRHH).
- Panel de capacitaciones (`/capacitaciones/admin/`) y reporte de periodo de prueba.

---

## 5. La ficha de supervisor: de jerarquía por cargo a cadena de jefes

Es la única vista que permite ver hacia abajo **más de un nivel**: un director
abre la ficha de los operarios de sus coordinadores. Se resuelve con
`_es_superior_en_cadena`, que sube por `jefe_directo` desde el empleado (tope de
10 niveles y control de ciclos, por si una asignación mal hecha encadena a dos
personas entre sí). Staff entra siempre.

**Hasta octubre de 2026 esta vista decidía por cargo**, y era la única:

1. Subordinado directo: el `cargo_jefe` del cargo del empleado es mi cargo.
2. Subordinado indirecto: misma área y `nivel_jerarquico` del empleado mayor
   que el mío.

Medido sobre producción antes de cambiarlo, eso tenía dos fallos:

- **Exposición.** La regla 2 ignoraba los equipos: 237 personas podían abrir la
  ficha de unas 209 cada una, 5.914 accesos en total. **216 de ellas eran
  empleados sin nadie a cargo**, casi todos de nivel 4, que "superaban" a los
  cargos de nivel 5 de su área. La ficha muestra documento, dirección,
  teléfono, contacto de emergencia y correo. No tenían el enlace, pero la URL
  respondía.
- **404 a jefes legítimos.** La lista "empleados a cargo" del perfil se arma por
  `jefe_directo`, pero esta vista validaba por cargo: 13 parejas de jefe y
  subalterno directo veían a la persona en su lista y recibían un 404 al
  abrirla, porque la estructura de cargos no coincidía con la asignación real.

Además RRHH no-superusuario recibía 404; ahora entra.

---

## 6. Lección: staff vs. jerarquía

`LoginRequiredMixin` **autentica pero no autoriza**, y los `{% if perms %}` de
los templates solo esconden botones. Por eso las vistas administrativas usan
`StaffRequiredMixin` (`apps/core/mixins.py`).

Pero **una vista que sirve a jefes o directores no puede llevar ese mixin**,
porque ellos no son staff. En esas vistas la autorización vive en el cuerpo:
se acota el queryset por `jefe_directo` y un empleado sin subalternos
simplemente no obtiene nada.

Antes de poner `StaffRequiredMixin` en una vista, comprobar:

- ¿El docstring menciona director, jefe o coordinador?
- ¿Hay una rama `if not request.user.is_staff:` que **sigue** en lugar de
  rechazar? Esa es la entrada de la ruta jerárquica, no una negación.
- ¿Algún template de `employees/` hace `action="{% url 'reports:...' %}"`?

Las tres señales estaban en `NovedadesAccionView`. Su test de regresión vive en
`apps/reports/tests_novedades_accion.py`.
