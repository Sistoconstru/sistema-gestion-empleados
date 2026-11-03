# =============================================================================
# apps/documents/views.py - VISTAS PARA DOCUMENTOS
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import storages
import os
from datetime import date, timedelta
import json
import logging

from django.db.models import Count
from django.views.decorators.http import require_POST

from .models import AnexoDocumento, DocumentoEmpleado, TipoDocumentoEmpleado, TipoDocumentoCargo, VersionDocumento
from .forms import (
    AnexoDocumentoForm, DocumentoActualizacionForm, DocumentoEmpleadoForm,
    MultipleDocumentUploadForm, DocumentApprovalForm, DocumentoReemplazoForm,
)
from apps.core.mixins import StaffRequiredMixin
from apps.employees.models import Empleado

logger = logging.getLogger(__name__)


@login_required
def documento_replace(request, documento_id):
    """Vista para reemplazar un documento rechazado"""
    documento = get_object_or_404(DocumentoEmpleado, id=documento_id)
    
    # Verificar permisos
    if not request.user.is_staff and documento.empleado.usuario != request.user:
        raise PermissionDenied
    
    # Verificar que el documento esté rechazado
    if documento.estado_aprobacion != 'rechazado':
        messages.error(request, 'Solo se pueden reemplazar documentos que han sido rechazados.')
        return redirect('documents:documento_view', documento_pk=documento_id)
    
    if request.method == 'POST':
        form = DocumentoReemplazoForm(request.POST, request.FILES, instance=documento, usuario=request.user)
        if form.is_valid():
            with transaction.atomic():
                # Antes se borraba el archivo anterior de S3. Ahora pasa al
                # historial: también el rechazado sirve de rastro.
                _archivar_version(
                    DocumentoEmpleado.objects.get(pk=documento.pk), request.user,
                    f'Reemplazo de documento rechazado: {documento.motivo_rechazo}'.strip(': '),
                )

                # Actualizar el documento
                documento = form.save(commit=False)
                documento.estado_aprobacion = 'pendiente'
                documento.aprobado_por = None
                documento.fecha_aprobacion = None
                documento.version += 1
                documento.save()

                messages.success(request, 'Documento reemplazado correctamente.')
                return redirect('documents:documento_view', documento_pk=documento_id)
    else:
        form = DocumentoReemplazoForm(instance=documento, usuario=request.user)
    
    return render(request, 'documents/documento_replace.html', {
        'form': form,
        'documento': documento,
    })

@login_required
def documento_empleado_detail(request, empleado_pk):
    """Vista detallada de documentos de un empleado específico"""
    empleado = get_object_or_404(Empleado, pk=empleado_pk)
    
    # Verificar permisos
    if not request.user.is_staff and (not hasattr(request.user, 'empleado') or request.user.empleado != empleado):
        raise PermissionDenied("No tienes permisos para ver estos documentos")
    
    # Obtener documentos existentes
    documentos_existentes = (
        DocumentoEmpleado.objects.filter(empleado=empleado).select_related('tipo_documento')
        .annotate(num_anexos=Count('anexos'))
    )
    
    # Obtener tipos de documentos requeridos/disponibles
    documentos_obligatorios = TipoDocumentoEmpleado.objects.filter(obligatorio=True, activo=True)
    documentos_opcionales = TipoDocumentoEmpleado.objects.filter(obligatorio=False, activo=True)
    
    # Documentos específicos del cargo
    documentos_cargo = []
    historial_actual = empleado.historialcargo_set.filter(activo=True).first()
    if historial_actual:
        documentos_cargo = TipoDocumentoEmpleado.objects.filter(
            tipodocumentocargo__cargo=historial_actual.cargo,
            activo=True
        )
    
    # Organizar documentos por estado
    docs_por_tipo = {doc.tipo_documento.codigo: doc for doc in documentos_existentes}
    
    # Documentos faltantes (obligatorios y de cargo), sin repetir
    todos_requeridos = list({doc.codigo: doc for doc in list(documentos_obligatorios) + list(documentos_cargo)}.values())
    codigos_requeridos = {doc.codigo for doc in todos_requeridos}
    docs_faltantes = [doc for doc in todos_requeridos if doc.codigo not in docs_por_tipo]

    # Opcionales pendientes: los que su cargo exige ya salen arriba como faltantes
    docs_opcionales_pendientes = [
        doc for doc in documentos_opcionales
        if doc.codigo not in docs_por_tipo and doc.codigo not in codigos_requeridos
    ]
    
    # Documentos próximos a vencer
    docs_por_vencer = documentos_existentes.filter(
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__lte=date.today() + timedelta(days=30)
    ).order_by('fecha_vencimiento')
    
    # Progreso sobre lo que este empleado debe tener: obligatorios + los de su
    # cargo. Antes sumaba también los opcionales y nadie llegaba al 100%.
    requeridos = {doc.codigo: doc for doc in todos_requeridos}.values()
    total_documentos = len(requeridos)
    aprobados = sum(
        1 for doc in requeridos
        if doc.codigo in docs_por_tipo and docs_por_tipo[doc.codigo].estado_aprobacion == 'aprobado'
    )
    progreso = int((aprobados / total_documentos) * 100) if total_documentos else 0
    
    total_aprobados = documentos_existentes.filter(estado_aprobacion='aprobado').count()
    total_pendientes = documentos_existentes.filter(estado_aprobacion='pendiente').count()
    
    context = {
        'empleado': empleado,
        'documentos_existentes': documentos_existentes,
        'documentos_obligatorios': documentos_obligatorios,
        'documentos_opcionales': documentos_opcionales,
        'documentos_cargo': documentos_cargo,
        'docs_por_tipo': docs_por_tipo,
        'docs_faltantes': docs_faltantes,
        'docs_por_vencer': docs_por_vencer,
        'puede_editar': request.user.is_staff or getattr(request.user, 'empleado', None) == empleado,
        'es_administrador': request.user.is_staff,
        'total_aprobados': total_aprobados,
        'total_pendientes': total_pendientes,
        'docs_opcionales_pendientes': docs_opcionales_pendientes,
        # --- Para la barra de progreso ---
        'documentos': {
            'progreso': progreso,
            'aprobados': aprobados,
            'total': total_documentos,
        },
    }
    
    return render(request, 'documents/empleado_documentos.html', context)


@login_required
def documento_upload(request, empleado_pk):
    """Vista para subir nuevo documento"""
    empleado = get_object_or_404(Empleado, pk=empleado_pk)
    
    # Verificar permisos
    if not request.user.is_staff and (not hasattr(request.user, 'empleado') or request.user.empleado != empleado):
        raise PermissionDenied("No tienes permisos para subir documentos para este empleado")
    
    if request.method == 'POST':
        form = DocumentoEmpleadoForm(request.POST, request.FILES, empleado=empleado, usuario=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    documento = form.save()
                    messages.success(
                        request,
                        f'✅ Documento {documento.tipo_documento.nombre} subido exitosamente. '
                        f'Estado: {documento.get_estado_aprobacion_display()}'
                    )
                    return redirect('documents:empleado_documentos', empleado_pk=empleado.pk)
                    
            except Exception as e:
                logger.error(f"Error subiendo documento: {str(e)}")
                messages.error(request, f'❌ Error al subir documento: {str(e)}')
    else:
        form = DocumentoEmpleadoForm(empleado=empleado, usuario=request.user)
    
    context = {
        'form': form,
        'empleado': empleado,
        'titulo': 'Subir Nuevo Documento'
    }
    
    return render(request, 'documents/documento_form.html', context)


@login_required
def documento_multiple_upload(request, empleado_pk):
    """Vista para subir múltiples documentos a la vez"""
    empleado = get_object_or_404(Empleado, pk=empleado_pk)
    
    # Verificar permisos
    if not request.user.is_staff and (not hasattr(request.user, 'empleado') or request.user.empleado != empleado):
        raise PermissionDenied("No tienes permisos para subir documentos para este empleado")
    
    if request.method == 'POST':
        form = MultipleDocumentUploadForm(request.POST, request.FILES, empleado=empleado)
        
        if form.is_valid():
            documentos_creados = 0
            errores = []
            
            try:
                with transaction.atomic():
                    # Procesar cada archivo subido
                    available_types = form.get_available_document_types()
                    
                    for tipo_doc in available_types:
                        field_name = f'documento_{tipo_doc.codigo}'
                        venc_field_name = f'vencimiento_{tipo_doc.codigo}'
                        
                        archivo = form.cleaned_data.get(field_name)
                        fecha_vencimiento = form.cleaned_data.get(venc_field_name)
                        
                        if archivo:
                            try:
                                # Crear documento
                                documento = DocumentoEmpleado.objects.create(
                                    empleado=empleado,
                                    tipo_documento=tipo_doc,
                                    archivo=archivo,
                                    fecha_vencimiento=fecha_vencimiento,
                                    nombre_archivo=f"{tipo_doc.codigo}_{empleado.numero_documento}.{archivo.name.split('.')[-1]}",
                                    cargado_por=request.user
                                )
                                documentos_creados += 1
                                
                            except Exception as e:
                                errores.append(f"{tipo_doc.nombre}: {str(e)}")
                    
                    if documentos_creados > 0:
                        messages.success(
                            request,
                            f'✅ {documentos_creados} documentos subidos exitosamente.'
                        )

                    
                    if errores:
                        for error in errores:
                            messages.error(request, f'❌ {error}')
                    
                    return redirect('documents:empleado_documentos', empleado_pk=empleado.pk)
                    
            except Exception as e:
                logger.error(f"Error en subida múltiple: {str(e)}")
                messages.error(request, f'❌ Error general: {str(e)}')
    else:
        form = MultipleDocumentUploadForm(empleado=empleado)
    
    context = {
        'form': form,
        'empleado': empleado,
        'titulo': 'Subir Múltiples Documentos'
    }
    
    return render(request, 'documents/documento_multiple_form.html', context)


@login_required

def documento_approve(request, documento_pk):
    """Vista para aprobar/rechazar documento o solo visualizarlo"""
    documento = get_object_or_404(DocumentoEmpleado, pk=documento_pk)

    # Si el usuario es staff, puede aprobar/rechazar
    if request.user.is_staff:
        if request.method == 'POST':
            form = DocumentApprovalForm(request.POST, instance=documento)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        documento = form.save(commit=False)
                        
                        if documento.estado_aprobacion == 'aprobado':
                            documento.aprobado_por = request.user
                            documento.fecha_aprobacion = timezone.now()
                            documento.rechazado_por = None
                            documento.fecha_rechazo = None
                            documento.motivo_rechazo = ''
                            messages.success(
                                request,
                                f'✅ Documento {documento.tipo_documento.nombre} de {documento.empleado.nombre_completo} aprobado exitosamente.'
                            )
                        else:
                            documento.rechazado_por = request.user
                            documento.fecha_rechazo = timezone.now()
                            documento.aprobado_por = None
                            documento.fecha_aprobacion = None
                            # El formulario llama "observaciones" al motivo; la
                            # vista del empleado y el reemplazo leen motivo_rechazo.
                            documento.motivo_rechazo = form.cleaned_data.get('observaciones', '')
                            messages.warning(
                                request,
                                f'⚠️ Documento {documento.tipo_documento.nombre} de {documento.empleado.nombre_completo} rechazado.'
                            )
                        
                        documento.save()
                        return redirect('documents:empleado_documentos', empleado_pk=documento.empleado.pk)
                except Exception as e:
                    logger.error(f"Error aprobando documento: {str(e)}")
                    messages.error(request, f'❌ Error: {str(e)}')
        else:
            form = DocumentApprovalForm(instance=documento)
        modo_visualizacion = False
    else:
        # Empleado solo puede visualizar su propio documento
        if not hasattr(request.user, 'empleado') or request.user.empleado != documento.empleado:
            raise PermissionDenied("No tienes permisos para ver este documento")
        form = DocumentApprovalForm(instance=documento)
        # Deshabilitar todos los campos del formulario
        for field in form.fields.values():
            field.disabled = True
        modo_visualizacion = True

    context = {
        'form': form,
        'documento': documento,
        'titulo': f'Revisar Documento - {documento.tipo_documento.nombre}',
        'modo_visualizacion': modo_visualizacion,
        'today': timezone.now().date(),
        # Anexos: los ven RRHH y el empleado. Versiones anteriores: solo RRHH.
        'anexos': documento.anexos.select_related('cargado_por'),
        'versiones': (
            documento.versiones_anteriores.select_related('reemplazada_por')
            if request.user.is_staff else []
        ),
    }
    return render(request, 'documents/documento_approval_form.html', context)


@login_required
def documento_download(request, documento_pk):
    """Descargar documento"""
    documento = get_object_or_404(DocumentoEmpleado, pk=documento_pk)
    
    # Verificar permisos
    if not request.user.is_staff and (not hasattr(request.user, 'empleado') or request.user.empleado != documento.empleado):
        raise PermissionDenied("No tienes permisos para descargar este documento")
    
    try:
        # Servir archivo
        response = HttpResponse(documento.archivo.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{documento.nombre_archivo}"'
        return response
        
    except Exception as e:
        logger.error(f"Error descargando documento: {str(e)}")
        messages.error(request, f'❌ Error descargando archivo: {str(e)}')
        return redirect('documents:empleado_documentos', empleado_pk=documento.empleado.pk)


@login_required
def empleados_documentos_pendientes(request):
    """Vista para mostrar empleados con documentos pendientes de aprobación"""
    from apps.employees.models import Empleado
    from django.db.models import Prefetch, Q
    
    # Verificar que el usuario tenga permisos
    if not request.user.is_staff:
        empleado = getattr(request.user, 'empleado', None)
        if empleado is None:
            raise PermissionDenied('Solo Talento Humano revisa documentos pendientes.')
        return redirect('employees:empleado_perfil_detail', pk=empleado.pk)
    
    # Obtener empleados con documentos pendientes
    empleados_con_pendientes = Empleado.objects.filter(
        documentoempleado__estado_aprobacion='pendiente'
    ).annotate(
        documentos_pendientes_count=Count(
            'documentoempleado', 
            filter=Q(documentoempleado__estado_aprobacion='pendiente')
        )
    ).select_related('usuario', 'sede', 'estado').distinct().order_by('apellidos', 'nombres').prefetch_related(
        # Una sola consulta para los documentos de todos, en vez de dos por empleado.
        Prefetch(
            'documentoempleado_set',
            queryset=DocumentoEmpleado.objects.filter(estado_aprobacion='pendiente')
            .select_related('tipo_documento', 'cargado_por').order_by('-fecha_carga'),
            to_attr='pendientes',
        )
    )

    empleados_data = [
        {'empleado': e, 'documentos_pendientes': e.pendientes, 'count': len(e.pendientes)}
        for e in empleados_con_pendientes
    ]
    
    context = {
        'empleados_data': empleados_data,
        'total_empleados': len(empleados_data),
        'total_documentos': sum(item['count'] for item in empleados_data),
        'titulo_pagina': 'Empleados con Documentos Pendientes de Aprobación'
    }
    
    return render(request, 'documents/empleados_pendientes.html', context)


@login_required
def documentos_pendientes_api(request):
    """API para obtener documentos pendientes de aprobación"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    documentos_pendientes = DocumentoEmpleado.objects.filter(
        estado_aprobacion='pendiente'
    ).select_related('empleado', 'tipo_documento').order_by('-fecha_carga')
    
    data = []
    for doc in documentos_pendientes:
        data.append({
            'id': str(doc.id),
            'empleado': doc.empleado.nombre_completo,
            'tipo_documento': doc.tipo_documento.nombre,
            'fecha_carga': doc.fecha_carga.strftime('%d/%m/%Y %H:%M'),
            'dias_pendiente': (timezone.now().date() - doc.fecha_carga.date()).days
        })
    
    return JsonResponse({'documentos': data})


# =============================================================================
# VISTA DE LISTA DE DOCUMENTOS (PARA ADMINISTRADORES)
# =============================================================================

class DocumentoEmpleadoListView(StaffRequiredMixin, ListView):
    """Todos los documentos del sistema, con filtro por estado y búsqueda.

    Antes filtraba y ordenaba por campos que no existen (estado,
    fecha_creacion) y daba error 500; y exigía un permiso de Django que el
    personal de RRHH no-superusuario no tiene. Ahora la regla es la del resto
    del módulo: staff.
    """
    model = DocumentoEmpleado
    template_name = 'documents/documento_list.html'
    context_object_name = 'documentos'
    paginate_by = 25
    ESTADOS = [('', 'Todos'), ('pendiente', 'Pendientes'), ('aprobado', 'Aprobados'), ('rechazado', 'Rechazados')]

    def get_queryset(self):
        from django.db.models import Q
        queryset = DocumentoEmpleado.objects.select_related(
            'empleado', 'tipo_documento', 'cargado_por',
        ).order_by('-fecha_carga')
        estado = self.request.GET.get('estado', '')
        if estado in dict(self.ESTADOS) and estado:
            queryset = queryset.filter(estado_aprobacion=estado)
        buscar = self.request.GET.get('q', '').strip()
        if buscar:
            queryset = queryset.filter(
                Q(empleado__nombres__icontains=buscar) | Q(empleado__apellidos__icontains=buscar)
                | Q(empleado__numero_documento__icontains=buscar)
                | Q(tipo_documento__nombre__icontains=buscar)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        por_estado = dict(
            DocumentoEmpleado.objects.values_list('estado_aprobacion').annotate(n=Count('id'))
        )
        context.update({
            'total_documentos': sum(por_estado.values()),
            'pendientes': por_estado.get('pendiente', 0),
            'aprobados': por_estado.get('aprobado', 0),
            'rechazados': por_estado.get('rechazado', 0),
            'estados': self.ESTADOS,
            'estado_filtro': self.request.GET.get('estado', ''),
            'buscar': self.request.GET.get('q', '').strip(),
        })
        return context


# =============================================================================
# VERSIONES Y ANEXOS (solo RRHH)
# =============================================================================

def _solo_staff(request):
    if not request.user.is_staff:
        raise PermissionDenied('Solo Talento Humano puede hacer esto.')


def _archivar_version(documento, usuario, motivo):
    """Copia los datos de la versión actual al historial antes de reemplazarla.

    El archivo no se mueve ni se borra: la fila del historial apunta a la
    misma ruta de S3, y el documento pasa a apuntar a la nueva.
    """
    return VersionDocumento.objects.create(
        documento=documento,
        version=documento.version,
        archivo=documento.archivo.name,
        nombre_archivo=documento.nombre_archivo,
        fecha_documento=documento.fecha_documento,
        fecha_vencimiento=documento.fecha_vencimiento,
        estado_aprobacion=documento.estado_aprobacion,
        fecha_carga=documento.fecha_carga,
        cargado_por=documento.cargado_por,
        aprobado_por=documento.aprobado_por,
        fecha_aprobacion=documento.fecha_aprobacion,
        reemplazada_por=usuario,
        motivo=motivo,
    )


def _servir_archivo(archivo, nombre):
    try:
        response = HttpResponse(archivo.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{nombre}"'
        return response
    except Exception as e:
        logger.error(f'Error descargando {nombre}: {e}')
        raise Http404('No se encontró el archivo.')


@login_required
def documento_actualizar(request, documento_pk):
    """RRHH reemplaza un documento en cualquier estado, también aprobado.

    La versión actual queda en el historial y la nueva queda aprobada: la
    sube Talento Humano, no hay a quién más pedirle la revisión.
    """
    _solo_staff(request)
    documento = get_object_or_404(DocumentoEmpleado, pk=documento_pk)

    if request.method == 'POST':
        form = DocumentoActualizacionForm(request.POST, request.FILES, documento=documento)
        if form.is_valid():
            with transaction.atomic():
                _archivar_version(documento, request.user, form.cleaned_data['motivo'])

                archivo = form.cleaned_data['archivo']
                ext = archivo.name.rsplit('.', 1)[-1].lower()
                ahora = timezone.now()
                documento.archivo = archivo
                documento.nombre_archivo = (
                    f'{documento.tipo_documento.codigo}_{documento.empleado.numero_documento}.{ext}'
                )
                documento.fecha_documento = form.cleaned_data['fecha_documento']
                if documento.tipo_documento.tiene_vencimiento:
                    documento.fecha_vencimiento = form.cleaned_data['fecha_vencimiento']
                documento.version += 1
                documento.cargado_por = request.user
                documento.estado_aprobacion = 'aprobado'
                documento.aprobado_por = request.user
                documento.fecha_aprobacion = ahora
                documento.rechazado_por = None
                documento.fecha_rechazo = None
                documento.motivo_rechazo = ''
                documento.save()
                # fecha_carga es auto_now_add: save() no la mueve.
                DocumentoEmpleado.objects.filter(pk=documento.pk).update(fecha_carga=ahora)

            messages.success(
                request,
                f'{documento.tipo_documento.nombre} actualizado a la versión {documento.version}. '
                f'La anterior quedó en el historial.'
            )
            return redirect('documents:documento_view', documento_pk=documento.pk)
    else:
        form = DocumentoActualizacionForm(documento=documento)

    return render(request, 'documents/documento_actualizar.html', {
        'form': form,
        'documento': documento,
    })


@login_required
def anexo_crear(request, documento_pk):
    """RRHH adjunta un otrosí, prórroga u otro anexo. Queda aprobado."""
    _solo_staff(request)
    documento = get_object_or_404(DocumentoEmpleado, pk=documento_pk)
    if not documento.tipo_documento.admite_anexos:
        messages.error(request, f'{documento.tipo_documento.nombre} no admite anexos.')
        return redirect('documents:documento_view', documento_pk=documento.pk)

    if request.method == 'POST':
        form = AnexoDocumentoForm(request.POST, request.FILES, documento=documento)
        if form.is_valid():
            anexo = form.save(commit=False)
            anexo.documento = documento
            anexo.cargado_por = request.user
            ext = anexo.archivo.name.rsplit('.', 1)[-1].lower()
            anexo.nombre_archivo = (
                f'{anexo.tipo.upper()}_{documento.empleado.numero_documento}_'
                f'{anexo.fecha_vigencia:%Y%m%d}.{ext}'
            )
            anexo.save()
            messages.success(request, f'{anexo.get_tipo_display()} agregado al {documento.tipo_documento.nombre.lower()}.')
            return redirect('documents:documento_view', documento_pk=documento.pk)
    else:
        form = AnexoDocumentoForm(documento=documento)

    return render(request, 'documents/anexo_form.html', {
        'form': form,
        'documento': documento,
    })


@login_required
def anexo_descargar(request, anexo_pk):
    """RRHH o el propio empleado."""
    anexo = get_object_or_404(AnexoDocumento.objects.select_related('documento__empleado'), pk=anexo_pk)
    empleado = anexo.documento.empleado
    if not request.user.is_staff and getattr(request.user, 'empleado', None) != empleado:
        raise PermissionDenied('No tienes permisos para descargar este anexo.')
    return _servir_archivo(anexo.archivo, anexo.nombre_archivo)


@login_required
@require_POST
def anexo_eliminar(request, anexo_pk):
    """Para anexos cargados por error. Borra también el archivo."""
    _solo_staff(request)
    anexo = get_object_or_404(AnexoDocumento, pk=anexo_pk)
    documento_pk = anexo.documento_id
    nombre = anexo.get_tipo_display()
    archivo = anexo.archivo.name
    anexo.delete()
    try:
        storages['default'].delete(archivo)
    except Exception as e:
        logger.warning(f'No se pudo borrar el archivo del anexo {archivo}: {e}')
    logger.info(f'[ANEXO] {request.user.username} eliminó {nombre} ({archivo}) del documento {documento_pk}')
    messages.success(request, f'{nombre} eliminado.')
    return redirect('documents:documento_view', documento_pk=documento_pk)


@login_required
def version_descargar(request, version_pk):
    """Versiones anteriores: solo RRHH. El empleado ve solo la vigente."""
    _solo_staff(request)
    version = get_object_or_404(VersionDocumento, pk=version_pk)
    return _servir_archivo(version.archivo, f'v{version.version}_{version.nombre_archivo}')
