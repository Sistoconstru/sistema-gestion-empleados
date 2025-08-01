# =============================================================================
# apps/organizational/api_views.py - CREAR ESTE ARCHIVO
# =============================================================================

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
import logging

from .models import Sede, AreaEmpresa, Cargo
from apps.employees.models import Empleado, HistorialCargo

logger = logging.getLogger(__name__)

# =============================================================================
# APIs PARA AUTOCOMPLETADO EN FORMULARIOS
# =============================================================================

@login_required
def sede_api(request):
    """API para obtener sedes activas (autocompletado)"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 20))
    
    sedes = Sede.objects.filter(activa=True)
    
    if query:
        sedes = sedes.filter(
            Q(nombre__icontains=query) | 
            Q(codigo__icontains=query) |
            Q(ciudad__icontains=query)
        )
    
    sedes = sedes[:limit]
    
    results = []
    for sede in sedes:
        results.append({
            'id': sede.id,
            'text': f"{sede.codigo} - {sede.nombre}",
            'codigo': sede.codigo,
            'nombre': sede.nombre,
            'ciudad': sede.ciudad,
            'departamento': sede.departamento
        })
    
    return JsonResponse({'results': results})


@login_required
def area_api(request):
    """API para obtener áreas activas (autocompletado)"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 20))
    
    areas = AreaEmpresa.objects.filter(activa=True).select_related('area_padre')
    
    if query:
        areas = areas.filter(
            Q(nombre__icontains=query) | 
            Q(codigo__icontains=query)
        )
    
    areas = areas[:limit]
    
    results = []
    for area in areas:
        padre_info = f" ({area.area_padre.nombre})" if area.area_padre else ""
        results.append({
            'id': area.id,
            'text': f"{area.nombre}{padre_info}",
            'codigo': area.codigo,
            'nombre': area.nombre,
            'area_padre': area.area_padre.nombre if area.area_padre else None
        })
    
    return JsonResponse({'results': results})


@login_required
def cargo_api(request):
    """API para obtener cargos activos (autocompletado)"""
    query = request.GET.get('q', '').strip()
    area_id = request.GET.get('area_id')
    limit = int(request.GET.get('limit', 20))
    
    cargos = Cargo.objects.filter(activo=True).select_related('area', 'rol_automatico')
    
    # Filtrar por área si se especifica
    if area_id:
        cargos = cargos.filter(area_id=area_id)
    
    # Filtrar por query
    if query:
        cargos = cargos.filter(
            Q(nombre__icontains=query) | 
            Q(codigo__icontains=query) |
            Q(area__nombre__icontains=query)
        )
    
    cargos = cargos[:limit]
    
    results = []
    for cargo in cargos:
        rol_info = f" → {cargo.rol_automatico.nombre}" if cargo.rol_automatico else ""
        results.append({
            'id': cargo.id,
            'text': f"{cargo.nombre} - {cargo.area.nombre}{rol_info}",
            'codigo': cargo.codigo,
            'nombre': cargo.nombre,
            'area': cargo.area.nombre,
            'area_id': cargo.area.id,
            'nivel_jerarquico': cargo.nivel_jerarquico,
            'rol_automatico': cargo.rol_automatico.nombre if cargo.rol_automatico else None
        })
    
    return JsonResponse({'results': results})


# =============================================================================
# APIs ESPECÍFICAS PARA FUNCIONALIDADES
# =============================================================================

@login_required
def cargos_por_area_api(request, area_id):
    """API para obtener cargos de un área específica"""
    try:
        area = get_object_or_404(AreaEmpresa, id=area_id, activa=True)
        cargos = Cargo.objects.filter(
            area=area, 
            activo=True
        ).select_related('rol_automatico').order_by('nivel_jerarquico', 'nombre')
        
        results = []
        for cargo in cargos:
            # Contar empleados actuales en este cargo
            empleados_count = Empleado.objects.filter(
                historialcargo__cargo=cargo,
                historialcargo__activo=True
            ).count()
            
            results.append({
                'id': cargo.id,
                'codigo': cargo.codigo,
                'nombre': cargo.nombre,
                'nivel_jerarquico': cargo.nivel_jerarquico,
                'rol_automatico': cargo.rol_automatico.nombre if cargo.rol_automatico else None,
                'requiere_licencia': cargo.requiere_licencia_conducir,
                'requiere_alturas': cargo.requiere_certificado_alturas,
                'empleados_count': empleados_count,
                'salario_min': str(cargo.salario_minimo) if cargo.salario_minimo else None,
                'salario_max': str(cargo.salario_maximo) if cargo.salario_maximo else None
            })
        
        return JsonResponse({
            'area': {
                'id': area.id,
                'nombre': area.nombre,
                'codigo': area.codigo,
            },
            'cargos': results
        })
        
    except Exception as e:
        logger.error(f"Error en cargos_por_area_api: {e}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required 
def estructura_json_api(request):
    """API para obtener estructura organizacional completa en JSON"""
    try:
        def area_to_dict(area):
            # Obtener cargos del área
            cargos = []
            for cargo in Cargo.objects.filter(area=area, activo=True).order_by('nivel_jerarquico'):
                empleados_count = Empleado.objects.filter(
                    historialcargo__cargo=cargo,
                    historialcargo__activo=True
                ).count()
                
                cargos.append({
                    'id': cargo.id,
                    'nombre': cargo.nombre,
                    'codigo': cargo.codigo,
                    'nivel': cargo.nivel_jerarquico,
                    'empleados': empleados_count,
                    'rol': cargo.rol_automatico.nombre if cargo.rol_automatico else None,
                    'requiere_licencia': cargo.requiere_licencia_conducir,
                    'requiere_alturas': cargo.requiere_certificado_alturas
                })
            
            # Construir el diccionario del área
            area_dict = {
                'id': area.id,
                'nombre': area.nombre,
                'codigo': area.codigo,
                'responsable': area.responsable.nombre_completo if area.responsable else None,
                'cargos': cargos,
                'total_empleados': sum(cargo['empleados'] for cargo in cargos)
            }
            
            # Agregar subáreas recursivamente
            subareas = []
            for subarea in area.areaempresa_set.filter(activa=True).order_by('nombre'):
                subareas.append(area_to_dict(subarea))
            
            area_dict['subareas'] = subareas
            return area_dict
        
        # Construir estructura desde áreas principales
        estructura = []
        areas_principales = AreaEmpresa.objects.filter(
            activa=True, 
            area_padre__isnull=True
        ).order_by('nombre')
        
        for area_principal in areas_principales:
            estructura.append(area_to_dict(area_principal))
        
        # Estadísticas generales
        stats = {
            'total_areas': AreaEmpresa.objects.filter(activa=True).count(),
            'total_cargos': Cargo.objects.filter(activo=True).count(),
            'total_empleados': Empleado.objects.count(),
            'areas_principales': len(estructura)
        }
        
        return JsonResponse({
            'estructura': estructura,
            'estadisticas': stats,
            'timestamp': timezone.now().isoformat(),
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error en estructura_json_api: {e}")
        return JsonResponse({
            'error': str(e), 
            'success': False
        }, status=500)


# =============================================================================
# APIs PARA VALIDACIONES EN TIEMPO REAL
# =============================================================================

@login_required
def validar_cargo_area_api(request):
    """API para validar si un cargo pertenece a un área específica"""
    cargo_id = request.GET.get('cargo_id')
    area_id = request.GET.get('area_id')
    
    if not cargo_id or not area_id:
        return JsonResponse({'valid': False, 'error': 'Parámetros requeridos'})
    
    try:
        cargo = Cargo.objects.get(id=cargo_id, activo=True)
        return JsonResponse({
            'valid': cargo.area_id == int(area_id),
            'cargo_area': cargo.area.nombre,
            'cargo_area_id': cargo.area.id
        })
    except Cargo.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Cargo no encontrado'})
    except Exception as e:
        return JsonResponse({'valid': False, 'error': str(e)})

