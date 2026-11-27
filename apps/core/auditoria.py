"""Traduce una petición a una acción y una frase legible para LogActividad.

Antes la acción se adivinaba por palabras sueltas en la URL ("eliminar",
"aprobar"...). Como casi ninguna ruta las trae, el 97% de los registros
quedaba como "crear": aprobar un documento, cerrar sesión o reaccionar a una
publicación se veían igual. Ahora se resuelve la ruta con Django y se busca
en CATALOGO; el objeto afectado (el contrato de quién, qué familiar) se
identifica ANTES de ejecutar la vista, para que un borrado conserve el nombre
de lo que se borró.

Uso desde el middleware:
    contexto = preparar(request)                      # en process_request
    accion, modulo, texto = interpretar(contexto, cambios, status)  # en process_response
"""
import logging

from django.apps import apps as django_apps
from django.urls import Resolver404, resolve

logger = logging.getLogger(__name__)

# Etiquetas de las acciones, para el admin y los filtros.
ACCIONES = {
    'iniciar_sesion': 'Inició sesión',
    'login_fallido': 'Intento fallido de inicio de sesión',
    'intento_sesion': 'Intento de inicio de sesión (sin resultado)',
    'login_bloqueado': 'Inicio de sesión bloqueado',
    'cerrar_sesion': 'Cerró sesión',
    'cambiar_contrasena': 'Cambió contraseña',
    'restablecer_contrasena': 'Restablecimiento de contraseña',
    'aprobar': 'Aprobó',
    'rechazar': 'Rechazó',
    'crear': 'Creó',
    'modificar': 'Modificó',
    'eliminar': 'Eliminó',
    'eliminar_sin_confirmar': 'Pidió eliminar (sin confirmar)',
    'subir_documento': 'Subió documento',
    'actualizar_documento': 'Actualizó documento',
    'reemplazar_documento': 'Reemplazó documento rechazado',
    'agregar_anexo': 'Agregó anexo',
    'registrar_asistencia': 'Registró asistencia',
    'registrar_novedad': 'Registró novedad de nómina',
    'solicitar_vacaciones': 'Registró vacaciones',
    'inactivar': 'Inactivó',
    'activar': 'Activó',
    'asignar': 'Asignó',
    'publicar': 'Publicó',
    'comentar': 'Comentó',
    'reaccionar': 'Reaccionó',
    'responder_encuesta': 'Respondió encuesta',
    'enviar_aviso': 'Envió aviso',
    'evaluar': 'Evaluó',
    'revisar': 'Revisó',
    'registrar_gasto': 'Registró gasto',
    'entregar': 'Registró entrega',
    'importar': 'Importó',
    'descargar': 'Descargó',
    'leer_notificacion': 'Leyó notificaciones',
    'leer_mensajes': 'Leyó mensajes',
    'activar_notificaciones': 'Activó notificaciones',
    'desactivar_notificaciones': 'Desactivó notificaciones',
    'accion_masiva': 'Acción masiva en el admin',
    'otra': 'Otra acción',
}


def etiqueta(accion):
    return ACCIONES.get(accion, (accion or '').replace('_', ' ').capitalize())


def _a(objeto):
    """'a' + objeto, con la contracción: 'al Contrato' y no 'a el Contrato'."""
    return f'al {objeto[3:]}' if objeto.startswith('el ') else f'a {objeto}'


def _valor(cambios, campo):
    """Primer valor de un campo de request.POST (que llega como lista)."""
    if not isinstance(cambios, dict):
        return ''
    v = cambios.get(campo, '')
    if isinstance(v, list):
        v = v[0] if v else ''
    return str(v).strip()


# --- Objetos afectados --------------------------------------------------------
# Cada función recibe el id de la URL y devuelve un texto como "el Contrato
# laboral de Juan Pérez". Si el objeto no existe, devuelve None.

def _documento(pk):
    d = django_apps.get_model('documents', 'DocumentoEmpleado').objects.select_related(
        'tipo_documento', 'empleado').get(pk=pk)
    return f'el {d.tipo_documento.nombre} de {d.empleado.nombre_completo}'


def _anexo(pk):
    a = django_apps.get_model('documents', 'AnexoDocumento').objects.select_related(
        'documento__tipo_documento', 'documento__empleado').get(pk=pk)
    return (f'el anexo «{a.get_tipo_display()}» del {a.documento.tipo_documento.nombre.lower()} '
            f'de {a.documento.empleado.nombre_completo}')


def _version(pk):
    v = django_apps.get_model('documents', 'VersionDocumento').objects.select_related(
        'documento__tipo_documento', 'documento__empleado').get(pk=pk)
    return (f'la versión {v.version} del {v.documento.tipo_documento.nombre.lower()} '
            f'de {v.documento.empleado.nombre_completo}')


def _empleado(pk):
    return django_apps.get_model('employees', 'Empleado').objects.get(pk=pk).nombre_completo


def _publicacion(pk):
    p = django_apps.get_model('employees', 'Publicacion').objects.select_related('autor').get(pk=pk)
    return f'una publicación de {p.autor.nombre_completo}'


def _comentario(pk):
    c = django_apps.get_model('employees', 'Comentario').objects.select_related('autor').get(pk=pk)
    return f'un comentario de {c.autor.nombre_completo}'


def _familiar(pk):
    f = django_apps.get_model('employees', 'Familiar').objects.select_related('empleado').get(pk=pk)
    return f'el familiar {f.nombre_completo} de {f.empleado.nombre_completo}'


def _encuesta(pk):
    return django_apps.get_model('surveys', 'Encuesta').objects.get(pk=pk).nombre


def _vacacion(pk):
    v = django_apps.get_model('employees', 'SolicitudVacacion').objects.select_related('empleado').get(pk=pk)
    return f'las vacaciones de {v.empleado.nombre_completo}'


def _vehiculo(pk):
    return f'el vehículo {django_apps.get_model("transporte", "Vehiculo").objects.get(pk=pk)}'


# (vista, parámetro de la URL) -> función. Para 'pk' depende de la vista.
OBJETOS = {
    'documento_pk': _documento,
    'anexo_pk': _anexo,
    'version_pk': _version,
    'empleado_pk': _empleado,
    'empleado_id': _empleado,
    'publicacion_pk': _publicacion,
    'comentario_id': _comentario,
    'familiar_id': _familiar,
    'vehiculo_id': _vehiculo,
    ('documents:documento_replace', 'documento_id'): _documento,
    ('employees:empleado_edit', 'pk'): _empleado,
    ('employees:empleado_inactivar', 'pk'): _empleado,
    ('employees:activar_empleado', 'pk'): _empleado,
    ('employees:eliminar_publicacion', 'pk'): _publicacion,
    ('employees:vacacion_editar_fechas', 'pk'): _vacacion,
    ('surveys:responder_encuesta', 'pk'): _encuesta,
    ('surveys:asignar_encuesta', 'pk'): _encuesta,
    ('surveys:publicar_encuesta', 'pk'): _encuesta,
    ('surveys:difundir_encuesta', 'pk'): _encuesta,
}


def _describir_objeto(vista, kwargs):
    for parametro, valor in kwargs.items():
        funcion = OBJETOS.get((vista, parametro)) or OBJETOS.get(parametro)
        if not funcion:
            continue
        try:
            return funcion(valor)
        except Exception:
            return None
    return None


def _describir_objeto_admin(app_label, modelo, object_id):
    try:
        Modelo = django_apps.get_model(app_label, modelo)
    except LookupError:
        return None, modelo
    verbose = str(Modelo._meta.verbose_name)
    if not object_id:
        return None, verbose
    try:
        return str(Modelo.objects.get(pk=object_id))[:120], verbose
    except Exception:
        return None, verbose


def preparar(request):
    """Se llama antes de la vista: resuelve la ruta y el objeto afectado."""
    return preparar_ruta(request.path_info)


def preparar_ruta(path):
    """Igual que preparar(), a partir de la URL guardada (reprocesar registros viejos)."""
    try:
        ruta = resolve(path)
    except Resolver404:
        return {'vista': '', 'kwargs': {}, 'objeto': None}
    vista = ruta.view_name or ''
    contexto = {'vista': vista, 'kwargs': dict(ruta.kwargs), 'objeto': None}
    if vista.startswith('admin:'):
        contexto['admin'] = _preparar_admin(vista, ruta.kwargs)
    else:
        contexto['objeto'] = _describir_objeto(vista, ruta.kwargs)
    return contexto


def _preparar_admin(vista, kwargs):
    """admin:<app>_<modelo>_<operación> -> datos para la frase."""
    nombre = vista.split(':', 1)[1]
    if nombre == 'auth_user_password_change':
        objeto, verbose = _describir_objeto_admin('authentication', 'Usuario', kwargs.get('id'))
        return {'operacion': 'password', 'objeto': objeto, 'modelo': verbose}
    partes = nombre.rsplit('_', 1)
    if len(partes) != 2 or '_' not in partes[0]:
        return {'operacion': nombre, 'objeto': None, 'modelo': ''}
    app_modelo, operacion = partes
    app_label, modelo = app_modelo.split('_', 1)
    objeto, verbose = _describir_objeto_admin(app_label, modelo, kwargs.get('object_id'))
    return {'operacion': operacion, 'objeto': objeto, 'modelo': verbose,
            'app_label': app_label, 'modelo_nombre': modelo}


# --- Catálogo de rutas --------------------------------------------------------
# vista -> (acción, módulo, texto). En el texto, {objeto} es el objeto afectado.

CATALOGO = {
    'authentication:logout': ('cerrar_sesion', 'sesión', 'cerró sesión'),
    'authentication:password_change': ('cambiar_contrasena', 'sesión', 'cambió su contraseña'),
    'authentication:password_reset_confirm': ('restablecer_contrasena', 'sesión', 'definió una contraseña nueva con el enlace de recuperación'),
    # Documentos
    'documents:anexo_eliminar': ('eliminar', 'documentos', 'eliminó {objeto}'),
    'documents:documento_replace': ('reemplazar_documento', 'documentos', 'reemplazó {objeto}, que estaba rechazado'),
    'documents:documento_actualizar': ('actualizar_documento', 'documentos', 'subió una versión nueva de {objeto}'),
    'documents:documento_multiple_upload': ('subir_documento', 'documentos', 'subió varios documentos de {objeto}'),
    # Asistencia y novedades
    'employees:asistencia_designar_encargado': ('asignar', 'asistencia', 'designó un encargado de asistencia'),
    # Notificaciones y mensajes
    'pwa_subscribe': ('activar_notificaciones', 'notificaciones', 'activó las notificaciones en un dispositivo'),
    'pwa_unsubscribe': ('desactivar_notificaciones', 'notificaciones', 'desactivó las notificaciones en un dispositivo'),
    'notifications:marcar_leida': ('leer_notificacion', 'notificaciones', 'marcó una notificación como leída'),
    'notifications:marcar_todas_leidas': ('leer_notificacion', 'notificaciones', 'marcó todas sus notificaciones como leídas'),
    'employees:marcar_mensajes_leidos': ('leer_mensajes', 'mensajería', 'leyó una conversación'),
    # Cartelera y marketplace
    'employees:alternar_reaccion': ('reaccionar', 'cartelera', 'reaccionó a {objeto}'),  # "una publicación de X"
    'employees:agregar_comentario': ('comentar', 'cartelera', 'comentó {objeto}'),
    'employees:crear_publicacion_rapida': ('publicar', 'cartelera', 'publicó en la cartelera'),
    'employees:crear_anuncio': ('publicar', 'cartelera', 'publicó un anuncio en la cartelera'),
    'employees:eliminar_publicacion': ('eliminar', 'cartelera', 'eliminó {objeto}'),
    'employees:eliminar_comentario': ('eliminar', 'cartelera', 'eliminó {objeto}'),
    'employees:crear_producto': ('publicar', 'marketplace', 'publicó un producto en el marketplace'),
    # Empleados
    'employees:empleado_edit': ('modificar', 'empleados', 'modificó la ficha de {objeto}'),
    'employees:empleado_inactivar': ('inactivar', 'empleados', 'inactivó a {objeto}'),
    'employees:activar_empleado': ('activar', 'empleados', 'activó a {objeto}'),
    # Vacaciones
    'employees:vacacion_nueva': ('solicitar_vacaciones', 'vacaciones', 'registró vacaciones para {objeto}'),
    'employees:vacacion_editar_fechas': ('modificar', 'vacaciones', 'cambió las fechas de {objeto}'),
    'employees:descargar_carta_vacaciones': ('descargar', 'vacaciones', 'descargó una carta de vacaciones'),
    # Familia
    'employees:familiar_crear': ('crear', 'familia', 'registró un familiar'),
    'employees:familiar_editar': ('modificar', 'familia', 'modificó {objeto}'),
    'employees:familiar_eliminar': ('eliminar', 'familia', 'eliminó {objeto}'),
    'employees:documento_familiar_subir': ('subir_documento', 'familia', 'subió un documento de {objeto}'),
    'employees:documento_familiar_eliminar': ('eliminar', 'familia', 'eliminó un documento de un familiar'),
    'employees:familia_estado_civil': ('modificar', 'familia', 'actualizó su estado civil'),
    # Encuestas
    'surveys:asignar_encuesta': ('asignar', 'encuestas', 'asignó la encuesta «{objeto}»'),
    'surveys:publicar_encuesta': ('publicar', 'encuestas', 'publicó la encuesta «{objeto}»'),
    'surveys:difundir_encuesta': ('enviar_aviso', 'encuestas', 'envió un recordatorio de la encuesta «{objeto}» a los pendientes'),
    # Evaluaciones
    'evaluations:seguimiento_bimensual': ('evaluar', 'evaluaciones', 'registró un seguimiento bimensual'),
    'evaluations:revisar_plan_predefinido': ('revisar', 'evaluaciones', 'revisó un plan de mejora'),
    'evaluations:evaluacion_final': ('evaluar', 'evaluaciones', 'registró una evaluación final'),
    # Beneficios, transporte, sorteos
    'beneficios_retencion:marcar_declarante': ('modificar', 'beneficios', 'marcó la condición de declarante'),
    'beneficios_retencion:nuevo_tramite': ('crear', 'beneficios', 'inició un trámite de beneficio de retención'),
    'transporte:asignar_conductor': ('asignar', 'transporte', 'asignó conductor {objeto_a}'),
    'transporte:registrar_documento': ('subir_documento', 'transporte', 'registró un documento de {objeto}'),
    'transporte:registrar_gasto_admin': ('registrar_gasto', 'transporte', 'registró un gasto'),
    'transporte:entregar_servicio': ('entregar', 'transporte', 'registró la entrega de un servicio'),
    'sorteos:editar': ('modificar', 'sorteos', 'modificó un sorteo'),
    # Integración Odoo (sin usuario: entra con token)
    'odoo-empleado-inactivar': ('inactivar', 'odoo', 'inactivó un empleado desde Odoo'),
    'odoo-vacacion-importar': ('importar', 'odoo', 'importó vacaciones desde Odoo'),
    'odoo-vacacion-estado': ('modificar', 'odoo', 'actualizó el estado de unas vacaciones desde Odoo'),
}


def _especiales(vista, objeto, cambios, status):
    """Rutas cuya acción depende de lo enviado o del resultado."""
    if vista in ('authentication:login', 'admin:login'):
        usuario = _valor(cambios, 'username')
        if status == 429:
            return 'login_bloqueado', 'sesión', f'tuvo el inicio de sesión bloqueado por demasiados intentos («{usuario}»)'
        if status in (301, 302, 303):
            return 'iniciar_sesion', 'sesión', 'inició sesión'
        if status is None:  # registros viejos: el resultado no se guardaba
            return 'intento_sesion', 'sesión', f'intentó iniciar sesión como «{usuario}» (resultado no registrado)'
        return 'login_fallido', 'sesión', f'intentó iniciar sesión como «{usuario}» con datos incorrectos'

    if vista == 'authentication:password_reset':
        return 'restablecer_contrasena', 'sesión', f'pidió restablecer la contraseña de {_valor(cambios, "email") or "una cuenta"}'

    if vista in ('documents:documento_view', 'documents:documento_approve'):
        estado = _valor(cambios, 'estado_aprobacion')
        if estado == 'rechazado':
            motivo = _valor(cambios, 'observaciones')
            return 'rechazar', 'documentos', f'rechazó {objeto}' + (f': «{motivo[:80]}»' if motivo else '')
        return 'aprobar', 'documentos', f'aprobó {objeto}'

    if vista == 'documents:anexo_crear':
        tipos = dict(django_apps.get_model('documents', 'AnexoDocumento').TIPOS)
        tipo = tipos.get(_valor(cambios, 'tipo'), 'anexo')
        fecha = _valor(cambios, 'fecha_vigencia')
        return 'agregar_anexo', 'documentos', f'agregó un {tipo} {_a(objeto)}' + (f' (vigente desde {fecha})' if fecha else '')

    if vista == 'documents:documento_upload':
        tipo = ''
        tipo_id = _valor(cambios, 'tipo_documento')
        if tipo_id:
            try:
                tipo = django_apps.get_model('documents', 'TipoDocumentoEmpleado').objects.get(pk=tipo_id).nombre
            except Exception:
                pass
        return 'subir_documento', 'documentos', f'subió {tipo or "un documento"} de {objeto}'

    if vista == 'employees:asistencia_diaria':
        estados = [v for k, v in (cambios or {}).items() if str(k).startswith('estado_')]
        estados = [e[0] if isinstance(e, list) else e for e in estados]
        novedades = sum(1 for e in estados if e and e != 'presente')
        detalle = f' de {len(estados)} personas' if estados else ''
        if novedades:
            detalle += f' ({novedades} con novedad)'
        return 'registrar_asistencia', 'asistencia', f'registró la asistencia{detalle}'

    if vista == 'employees:novedades_semana':
        tipo = _valor(cambios, 'tipo').replace('_', ' ')
        quien = ''
        if _valor(cambios, 'empleado_id'):
            try:
                quien = ' de ' + _empleado(_valor(cambios, 'empleado_id'))
            except Exception:
                pass
        return 'registrar_novedad', 'novedades', f'registró una novedad de nómina{" (" + tipo + ")" if tipo else ""}{quien}'

    if vista == 'reports:novedades_accion':
        accion = _valor(cambios, 'accion')
        n = len(cambios.get('novedad_ids', [])) if isinstance(cambios, dict) else 0
        verbo = {'aprobar': 'aprobar', 'rechazar': 'rechazar'}.get(accion, 'modificar')
        texto = {'aprobar': 'aprobó', 'rechazar': 'rechazó'}.get(accion, 'procesó')
        return verbo, 'novedades', f'{texto} {n} novedad{"es" if n != 1 else ""} de nómina'

    if vista == 'surveys:responder_encuesta':
        if _valor(cambios, 'finalizar_encuesta') == 'true':
            return 'responder_encuesta', 'encuestas', f'envió sus respuestas a la encuesta «{objeto}»'
        return 'responder_encuesta', 'encuestas', f'guardó un borrador de la encuesta «{objeto}»'

    if vista == 'employees:empleado_create':
        nombre = f'{_valor(cambios, "nombres")} {_valor(cambios, "apellidos")}'.strip()
        return 'crear', 'empleados', f'creó el empleado {nombre}' if nombre else 'creó un empleado'

    return None


def _admin(info, cambios):
    operacion, modelo, objeto = info.get('operacion'), info.get('modelo') or 'registro', info.get('objeto')
    nombre = f' «{objeto}»' if objeto else ''
    confirmado = _valor(cambios, 'post') == 'yes'
    if operacion == 'password':
        return 'cambiar_contrasena', 'admin', f'cambió desde el admin la contraseña del usuario{nombre}'
    if operacion == 'add':
        return 'crear', 'admin', f'agregó desde el admin un registro de {modelo}'
    if operacion == 'change':
        return 'modificar', 'admin', f'modificó desde el admin {modelo}{nombre}'
    if operacion == 'delete':
        if confirmado:
            return 'eliminar', 'admin', f'eliminó desde el admin {modelo}{nombre}'
        return 'eliminar_sin_confirmar', 'admin', f'pidió eliminar desde el admin {modelo}{nombre} (aún sin confirmar)'
    if operacion == 'changelist':
        accion = _valor(cambios, 'action')
        seleccion = cambios.get('_selected_action', []) if isinstance(cambios, dict) else []
        n = len(seleccion)
        nombres = _nombres_admin(info, seleccion)
        if accion == 'delete_selected':
            if confirmado:
                return 'eliminar', 'admin', f'eliminó desde el admin {n} registro(s) de {modelo}{nombres}'
            return 'eliminar_sin_confirmar', 'admin', f'pidió eliminar desde el admin {n} registro(s) de {modelo}{nombres} (aún sin confirmar)'
        if accion:
            return 'accion_masiva', 'admin', f'aplicó «{accion}» a {n} registro(s) de {modelo}{nombres}'
        return 'modificar', 'admin', f'modificó desde el admin la lista de {modelo}'
    return 'otra', 'admin', f'usó el admin ({operacion}) en {modelo}'


def _nombres_admin(info, ids):
    """Al pedir eliminar en bloque los objetos aún existen: se nombran."""
    if not ids or not info.get('app_label'):
        return ''
    try:
        Modelo = django_apps.get_model(info['app_label'], info['modelo_nombre'])
        nombres = [str(o)[:80] for o in Modelo.objects.filter(pk__in=ids[:5])]
        if nombres and len(ids) > 5:
            nombres.append(f'y {len(ids) - 5} más')
        return (': ' + '; '.join(nombres)) if nombres else ''
    except Exception:
        return ''


# Palabras del nombre de la ruta -> acción, para rutas que no están en el catálogo.
_PALABRAS = [
    (('eliminar', 'delete', 'borrar'), 'eliminar', 'eliminó'),
    (('aprobar', 'approve'), 'aprobar', 'aprobó'),
    (('rechazar',), 'rechazar', 'rechazó'),
    (('subir', 'upload', 'cargar'), 'subir_documento', 'subió un archivo'),
    (('crear', 'nuevo', 'nueva', 'add', 'registrar'), 'crear', 'creó'),
    (('editar', 'update', 'change', 'modificar', 'actualizar'), 'modificar', 'modificó'),
    (('asignar',), 'asignar', 'asignó'),
    (('inactivar',), 'inactivar', 'inactivó'),
    (('activar',), 'activar', 'activó'),
    (('enviar',), 'enviar_aviso', 'envió'),
]


def interpretar(contexto, cambios, status):
    """-> (acción, módulo, texto sin el nombre del usuario)."""
    contexto = contexto or {}
    vista = contexto.get('vista', '')
    objeto = contexto.get('objeto') or 'un registro'

    if 'admin' in contexto and vista != 'admin:login':
        return _admin(contexto['admin'], cambios)

    especial = _especiales(vista, objeto, cambios, status)
    if especial:
        return especial

    if vista in CATALOGO:
        accion, modulo, texto = CATALOGO[vista]
        return accion, modulo, texto.format(objeto=objeto, objeto_a=_a(objeto))

    nombre = vista.split(':')[-1].lower()
    modulo = vista.split(':')[0] if ':' in vista else ''
    for palabras, accion, verbo in _PALABRAS:
        if any(p in nombre for p in palabras):
            detalle = f' {contexto["objeto"]}' if contexto.get('objeto') else ''
            return accion, modulo, f'{verbo}{detalle} ({nombre.replace("_", " ")})'
    return 'otra', modulo, f'envió un formulario en «{nombre.replace("_", " ") or "ruta desconocida"}»'
