from multiprocessing import context
from django.shortcuts import render
from django.views.generic import TemplateView

# =============================================================================
#ACTUALIZACIÓN DEL DASHBOARD PRINCIPAL - core/views.py
#============================================================================= 

# Agregar al dashboard principal para mostrar estadísticas de documentos

def dashboard_view(request):
    """Vista del dashboard principal con estadísticas de documentos"""
    
    # Estadísticas existentes de empleados...
    
    # NUEVAS ESTADÍSTICAS DE DOCUMENTOS
    from apps.documents.models import DocumentoEmpleado, TipoDocumentoEmpleado
    from datetime import date, timedelta
    
    # Documentos pendientes de aprobación
    documentos_pendientes = DocumentoEmpleado.objects.filter(
        estado_aprobacion='pendiente'
    ).count()
    
    # Documentos próximos a vencer (30 días)
    fecha_limite = date.today() + timedelta(days=30)
    documentos_por_vencer = DocumentoEmpleado.objects.filter(
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__lte=fecha_limite,
        estado_aprobacion='aprobado'
    ).count()
    
    # Documentos vencidos
    documentos_vencidos = DocumentoEmpleado.objects.filter(
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__lt=date.today(),
        estado_aprobacion='aprobado'
    ).count()
    
    # Empleados con documentación incompleta
    from apps.employees.models import Empleado
    
    empleados_docs_incompletos = 0
    for empleado in Empleado.objects.filter(estado__codigo='PRUEBA'):
        # Verificar si tiene todos los documentos obligatorios
        docs_obligatorios = TipoDocumentoEmpleado.objects.filter(obligatorio=True, activo=True)
        docs_aprobados = DocumentoEmpleado.objects.filter(
            empleado=empleado,
            estado_aprobacion='aprobado',
            tipo_documento__in=docs_obligatorios
        ).count()
        
        if docs_aprobados < docs_obligatorios.count():
            empleados_docs_incompletos += 1
    
    context.update({
        # Estadísticas de documentos
        'documentos_pendientes': documentos_pendientes,
        'documentos_por_vencer': documentos_por_vencer,
        'documentos_vencidos': documentos_vencidos,
        'empleados_docs_incompletos': empleados_docs_incompletos,
        
        # Para alertas en el dashboard
        'alertas_documentos': {
            'pendientes': documentos_pendientes > 0,
            'vencimientos': documentos_por_vencer > 0,
            'vencidos': documentos_vencidos > 0,
            'incompletos': empleados_docs_incompletos > 0
        }
    })