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

from .models import DocumentoEmpleado, TipoDocumentoEmpleado, TipoDocumentoCargo
from .forms import DocumentoEmpleadoForm, MultipleDocumentUploadForm, DocumentApprovalForm, DocumentoReemplazoForm
from apps.employees.models import Empleado

logger = logging.getLogger(__name__)


class DocumentoEmpleadoListView(LoginRequiredMixin, ListView):
    """Vista para listar documentos del empleado"""
    model = DocumentoEmpleado
    template_name = 'documents/documento_list.html'
    context_object_name = 'documentos'
    
    def get_queryset(self):
        """Filtrar documentos según usuario"""
        if self.request.user.is_staff:
            # Administradores ven todos los documentos
            return DocumentoEmpleado.objects.select_related(
                'empleado', 'tipo_documento', 'cargado_por', 'aprobado_por'
            ).order_by('-fecha_carga')
        else:
            # Empleados solo ven sus documentos
            try:
                empleado = Empleado.objects.get(usuario=self.request.user)
                return DocumentoEmpleado.objects.filter(empleado=empleado).select_related(
                    'tipo_documento', 'cargado_por', 'aprobado_por'
                ).order_by('-fecha_carga')
            except Empleado.DoesNotExist:
                return DocumentoEmpleado.objects.none()


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
                # Guardar la ruta del archivo anterior
                old_file = documento.archivo.path if documento.archivo else None
                
                # Actualizar el documento
                documento = form.save(commit=False)
                documento.estado_aprobacion = 'pendiente'
                documento.aprobado_por = None
                documento.fecha_aprobacion = None
                documento.version += 1
                documento.save()
                
                # Eliminar el archivo anterior si existe
                if old_file:
                    try:
                        storages["default"].delete(old_file)
                    except Exception:
                        # El archivo no existe en el backend, continuar sin error
                        pass
                
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
    documentos_existentes = DocumentoEmpleado.objects.filter(empleado=empleado).select_related('tipo_documento')
    
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
    
    # Documentos faltantes (obligatorios y de cargo)
    todos_requeridos = list(documentos_obligatorios) + list(documentos_cargo)
    docs_faltantes = [doc for doc in todos_requeridos if doc.codigo not in docs_por_tipo]
    
    # Documentos opcionales pendientes
    docs_opcionales_pendientes = [doc for doc in documentos_opcionales if doc.codigo not in docs_por_tipo]
    
    # Documentos próximos a vencer
    docs_por_vencer = documentos_existentes.filter(
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__lte=date.today() + timedelta(days=30)
    ).order_by('fecha_vencimiento')
    
    # --- NUEVO: Progreso considerando opcionales ---
    todos_documentos = list(documentos_obligatorios) + list(documentos_cargo) + list(documentos_opcionales)
    total_documentos = len(todos_documentos)
    aprobados = sum(
        1 for doc in todos_documentos
        if doc.codigo in docs_por_tipo and docs_por_tipo[doc.codigo].estado_aprobacion == 'aprobado'
    )
    progreso = int((aprobados / total_documentos) * 100) if total_documentos else 0
    # ------------------------------------------------
    
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
                    import logging
                    logger = logging.getLogger('storages')
                    logger.debug(f'Documento subido: {documento.archivo.name}')
                        # Log de la URL firmada generada
                    logger.debug(f'URL firmada: {documento.archivo.url}')
                    
                    messages.success(
                        request,
                        f'✅ Documento {documento.tipo_documento.nombre} subido exitosamente. '
                        f'Estado: {documento.get_estado_aprobacion_display()}'
                    )
                    
                    # Verificar si ahora el empleado puede cambiar de estado
                    verificar_cambio_estado_empleado(empleado)
                    
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
                        
                        # Verificar cambio de estado
                        verificar_cambio_estado_empleado(empleado)
                    
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
                            verificar_cambio_estado_empleado(documento.empleado)
                        else:
                            documento.rechazado_por = request.user
                            documento.fecha_rechazo = timezone.now()
                            documento.aprobado_por = None
                            documento.fecha_aprobacion = None
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
        'today': timezone.now().date()
    }
    return render(request, 'documents/documento_approval_form.html', context)


def verificar_cambio_estado_empleado(empleado):
    """Verificar si el empleado puede cambiar de estado basado en documentos"""
    try:
        from apps.employees.models import EstadoEmpleado
        
        # Solo verificar si está en prueba
        estado_prueba = EstadoEmpleado.objects.get(codigo='PRUEBA')
        if empleado.estado != estado_prueba:
            return
        
        # Obtener documentos obligatorios requeridos
        docs_obligatorios = TipoDocumentoEmpleado.objects.filter(obligatorio=True, activo=True)
        
        # Documentos específicos del cargo
        historial_actual = empleado.historialcargo_set.filter(activo=True).first()
        docs_cargo = []
        if historial_actual:
            docs_cargo = TipoDocumentoEmpleado.objects.filter(
                tipodocumentocargo__cargo=historial_actual.cargo,
                activo=True
            )
        
        todos_requeridos = list(docs_obligatorios) + list(docs_cargo)
        
        # Verificar que todos estén aprobados
        docs_aprobados = DocumentoEmpleado.objects.filter(
            empleado=empleado,
            tipo_documento__in=todos_requeridos,
            estado_aprobacion='aprobado'
        ).count()
        
        if docs_aprobados >= len(todos_requeridos):
            # Cambiar a estado activo
            estado_activo = EstadoEmpleado.objects.get(codigo='ACTIVO')
            empleado.estado = estado_activo
            empleado.save()
            
            logger.info(f"Empleado {empleado.numero_documento} cambió a estado ACTIVO por documentos completos")
            
    except Exception as e:
        logger.error(f"Error verificando cambio de estado: {str(e)}")


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