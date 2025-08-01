
# =============================================================================
# apps/organizational/views.py - VISTAS MÍNIMAS NECESARIAS
# =============================================================================

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
import json
# Importaciones adicionales necesarias
from django.utils import timezone
from django.db import models
from .models import Sede, AreaEmpresa, Cargo
from apps.employees.models import Empleado, HistorialCargo


class OrganizationalIndexView(LoginRequiredMixin, TemplateView):
    """Vista principal del módulo organizacional"""
    template_name = 'organizational/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas básicas
        context.update({
            'total_sedes': Sede.objects.filter(activa=True).count(),
            'total_areas': AreaEmpresa.objects.filter(activa=True).count(),
            'total_cargos': Cargo.objects.filter(activo=True).count(),
            'empleados_por_sede': self.get_empleados_por_sede(),
            'empleados_por_area': self.get_empleados_por_area(),
        })
        
        return context
    
    def get_empleados_por_sede(self):
        """Obtener distribución de empleados por sede"""
        return Sede.objects.filter(activa=True).annotate(
            empleados_count=Count('empleado')
        ).values('nombre', 'empleados_count')
    
    def get_empleados_por_area(self):
        """Obtener distribución de empleados por área"""
        return AreaEmpresa.objects.filter(activa=True).annotate(
            empleados_count=Count('cargo__historialcargo', 
                                filter=Q(cargo__historialcargo__activo=True))
        ).values('nombre', 'empleados_count')


class OrganizationalStructureView(LoginRequiredMixin, TemplateView):
    """Vista del organigrama/estructura organizacional"""
    template_name = 'organizational/organigrama.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estructura jerárquica de áreas
        areas_principales = AreaEmpresa.objects.filter(
            activa=True, 
            area_padre__isnull=True
        ).prefetch_related('areaempresa_set', 'responsable')
        
        # Estructura de cargos por área
        context.update({
            'areas_principales': areas_principales,
            'estructura_organizacional': self.build_organizational_tree(),
            'total_niveles': self.get_max_hierarchy_level(),
        })
        
        return context
    
    def build_organizational_tree(self):
        """Construir árbol organizacional completo"""
        def get_area_tree(area):
            cargos = Cargo.objects.filter(area=area, activo=True).select_related('rol_automatico')
            
            # Obtener empleados actuales por cargo
            cargos_con_empleados = []
            for cargo in cargos:
                empleados_actuales = Empleado.objects.filter(
                    historialcargo__cargo=cargo,
                    historialcargo__activo=True
                ).select_related('usuario')
                
                cargos_con_empleados.append({
                    'cargo': cargo,
                    'empleados': empleados_actuales,
                    'count_empleados': empleados_actuales.count()
                })
            
            return {
                'area': area,
                'cargos': cargos_con_empleados,
                'subareas': [get_area_tree(subarea) for subarea in area.areaempresa_set.filter(activa=True)]
            }
        
        # Construir desde áreas principales
        return [get_area_tree(area) for area in AreaEmpresa.objects.filter(
            activa=True, area_padre__isnull=True
        )]
    
    def get_max_hierarchy_level(self):
        """Obtener el máximo nivel jerárquico"""
        max_nivel = Cargo.objects.aggregate(
            max_nivel=models.Max('nivel_jerarquico')
        )['max_nivel'] or 1
        return max_nivel

