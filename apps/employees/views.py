# =============================================================================
# apps/employees/views.py - VISTAS CORREGIDAS DE EMPLEADOS
# =============================================================================


from .exports import export_empleados_excel, export_empleados_pdf, export_empleados_csv, export_empleado_perfil_pdf, export_empleado_excel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Avg, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import timedelta, date
import json
import logging

from .models import Empleado, TipoDocumento, Escolaridad, EstadoEmpleado, HistorialCargo
from .forms import EmpleadoForm, BusquedaEmpleadoForm
from apps.organizational.models import AreaEmpresa, Cargo, Sede
from apps.training.models import InscripcionCapacitacion
from apps.evaluations.models import AsignacionEvaluacion

# Configurar logging
logger = logging.getLogger(__name__)
User = get_user_model()


class EmpleadoListView(LoginRequiredMixin, ListView):
    """Vista para listar empleados con filtros y búsqueda"""
    model = Empleado
    template_name = 'employees/empleado_list.html'
    context_object_name = 'empleados'
    paginate_by = 20
    
    def get_queryset(self):
        """Obtener empleados con filtros aplicados"""
        queryset = Empleado.objects.select_related(
            'estado', 'sede', 'tipo_documento', 'usuario', 'escolaridad'
        ).prefetch_related(
            Prefetch(
                'historialcargo_set',
                queryset=HistorialCargo.objects.filter(activo=True).select_related('cargo__area'),
                to_attr='cargo_actual_list'
            )
        )
        
        # Obtener parámetros de filtros
        search = self.request.GET.get('search', '').strip()
        estado = self.request.GET.get('estado')
        area = self.request.GET.get('area')
        cargo = self.request.GET.get('cargo')
        sede = self.request.GET.get('sede')
        
        # Aplicar filtro de búsqueda
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) |
                Q(apellidos__icontains=search) |
                Q(numero_documento__icontains=search) |
                Q(correo_electronico__icontains=search)
            )
        
        # Aplicar filtros específicos
        if estado:
            queryset = queryset.filter(estado_id=estado)
        
        if sede:
            queryset = queryset.filter(sede_id=sede)
        
        if area:
            queryset = queryset.filter(
                historialcargo__cargo__area_id=area,
                historialcargo__activo=True
            )
        
        if cargo:
            queryset = queryset.filter(
                historialcargo__cargo_id=cargo,
                historialcargo__activo=True
            )
        
        return queryset.distinct().order_by('apellidos', 'nombres')
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional"""
        context = super().get_context_data(**kwargs)
        
        # Formulario de búsqueda
        form_data = self.request.GET.copy()
        context['form'] = BusquedaEmpleadoForm(form_data)
        
        # Estadísticas generales
        context.update(self.get_estadisticas())
        
        return context
    
    def get_estadisticas(self):
        """Calcular estadísticas para el dashboard"""
        # Totales generales
        total_empleados = Empleado.objects.count()
        
        # Por estado
        try:
            estado_activo = EstadoEmpleado.objects.get(codigo='ACTIVO')
            empleados_activos = Empleado.objects.filter(estado=estado_activo).count()
        except EstadoEmpleado.DoesNotExist:
            empleados_activos = 0
        
        try:
            estado_prueba = EstadoEmpleado.objects.get(codigo='PRUEBA')
            empleados_prueba = Empleado.objects.filter(estado=estado_prueba).count()
        except EstadoEmpleado.DoesNotExist:
            empleados_prueba = 0
        
        # Nuevos empleados este mes
        inicio_mes = timezone.now().replace(day=1).date()
        nuevos_mes = Empleado.objects.filter(fecha_ingreso__gte=inicio_mes).count()
        
        return {
            'total_empleados': total_empleados,
            'empleados_activos': empleados_activos,
            'empleados_prueba': empleados_prueba,
            'nuevos_mes': nuevos_mes,
        }


class EmpleadoDetailView(LoginRequiredMixin, DetailView):
    """Vista de detalle completo del empleado"""
    model = Empleado
    template_name = 'employees/empleado_detail.html'
    context_object_name = 'empleado'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = self.get_object()
        
        # Historial de cargos
        context['historial_cargos'] = empleado.historialcargo_set.select_related(
            'cargo__area'
        ).order_by('-fecha_inicio')
        
        # Capacitaciones recientes
        try:
            context['capacitaciones'] = InscripcionCapacitacion.objects.filter(
                empleado=empleado
            ).select_related('capacitacion').order_by('-fecha_inscripcion')[:10]
        except:
            context['capacitaciones'] = []
        
        # Evaluaciones
        try:
            context['evaluaciones'] = AsignacionEvaluacion.objects.filter(
                empleado_evaluado=empleado
            ).select_related('evaluacion', 'evaluador').order_by('-fecha_asignacion')[:5]
        except:
            context['evaluaciones'] = []
        
        # Estadísticas reales de documentos
        documentos = empleado.documentoempleado_set.all()
        context['documentos_completos'] = documentos.filter(estado_aprobacion='aprobado').count()
        context['documentos_pendientes'] = documentos.filter(estado_aprobacion='pendiente').count()
        
        return context


class EmpleadoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Vista para crear nuevo empleado"""
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'employees/empleado_form.html'
    permission_required = 'employees.add_empleado'
    success_url = reverse_lazy('employees:empleado_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Nuevo Empleado'
        return context
    
    def form_valid(self, form):
        """Procesar formulario válido y crear usuario automáticamente"""
        try:
            with transaction.atomic():
                # Asignar usuario creador
                form.instance.creado_por = self.request.user
                
                # Determinar estado inicial basado en fecha de ingreso
                dias_desde_ingreso = (date.today() - form.instance.fecha_ingreso).days
                
                if dias_desde_ingreso <= 60:  # Período de prueba
                    try:
                        estado_prueba = EstadoEmpleado.objects.get(codigo='PRUEBA')
                        form.instance.estado = estado_prueba
                    except EstadoEmpleado.DoesNotExist:
                        logger.warning("Estado PRUEBA no encontrado")
                        # Usar el primer estado disponible
                        form.instance.estado = EstadoEmpleado.objects.first()
                else:
                    try:
                        estado_activo = EstadoEmpleado.objects.get(codigo='ACTIVO')
                        form.instance.estado = estado_activo
                    except EstadoEmpleado.DoesNotExist:
                        logger.warning("Estado ACTIVO no encontrado")
                        form.instance.estado = EstadoEmpleado.objects.first()
                
                # Guardar empleado primero
                empleado = form.save()
                
                # Crear usuario automáticamente si tiene email
                if empleado.numero_documento:
                    usuario_creado = self.crear_usuario_automatico(empleado)
                    if usuario_creado:
                        empleado.usuario = usuario_creado
                        empleado.save()
                
                # Crear historial de cargo si se especificó cargo
                cargo = form.cleaned_data.get('cargo')
                if cargo:
                    HistorialCargo.objects.create(
                        empleado=empleado,
                        cargo=cargo,
                        fecha_inicio=empleado.fecha_ingreso,
                        activo=True,
                        creado_por=self.request.user
                    )
                
                messages.success(
                    self.request, 
                    f'✅ Empleado {empleado.nombre_completo} creado exitosamente.'
                )
                
                return super().form_valid(form)
                
        except Exception as e:
            logger.error(f"Error creando empleado: {str(e)}")
            messages.error(
                self.request,
                f'❌ Error al crear el empleado: {str(e)}'
            )
            return self.form_invalid(form)
    
    def crear_usuario_automatico(self, empleado):
        """Crear usuario automáticamente con nombre y documento"""
        try:
            # Generar username: primer_nombre.primer_apellido
            primer_nombre = empleado.nombres.split()[0].lower()
            primer_apellido = empleado.apellidos.split()[0].lower()
            username_base = f"{primer_nombre}.{primer_apellido}"
            
            # Asegurar username único
            username = username_base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            
            # Generar password: Primer nombre + documento
            password = f"{primer_nombre.capitalize()}{empleado.numero_documento}"
            
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=empleado.correo_electronico,
                first_name=empleado.nombres,
                last_name=empleado.apellidos,
                password=password,
                is_active=True
            )
            
            # Mostrar mensaje con credenciales
            messages.success(
                self.request,
                f"✅ Usuario creado automáticamente:\n"
                f"👤 Usuario: {username}\n"
                f"🔑 Contraseña: {password}\n"
                f"📧 Email: {empleado.correo_electronico}\n"
                f"(Comunicar estas credenciales al empleado)"
            )
            
            logger.info(f"Usuario creado para empleado {empleado.numero_documento}: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error creando usuario para empleado {empleado.numero_documento}: {str(e)}")
            messages.warning(
                self.request,
                f"⚠️ No se pudo crear usuario automáticamente: {str(e)}"
            )
            return None
    
    def form_invalid(self, form):
        """Manejar formulario inválido"""
        logger.warning(f"Formulario inválido: {form.errors}")
        
        # Agregar errores específicos a los mensajes
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        
        return super().form_invalid(form)


class EmpleadoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Vista para editar empleado"""
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'employees/empleado_form.html'
    permission_required = 'employees.change_empleado'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Empleado - {self.object.nombre_completo}'
        return context
    
    def get_success_url(self):
        messages.success(
            self.request, 
            f'Empleado {self.object.nombre_completo} actualizado exitosamente.'
        )
        return reverse_lazy('employees:empleado_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Procesar cambios en el formulario"""
        try:
            with transaction.atomic():
                # Verificar si cambió el cargo
                cargo_nuevo = form.cleaned_data.get('cargo')
                cargo_actual = None
                
                # Obtener cargo actual
                historial_actual = self.object.historialcargo_set.filter(activo=True).first()
                if historial_actual:
                    cargo_actual = historial_actual.cargo
                
                # Si cambió el cargo, crear nuevo historial
                if cargo_nuevo and cargo_nuevo != cargo_actual:
                    # Desactivar cargo actual
                    if historial_actual:
                        historial_actual.activo = False
                        historial_actual.fecha_fin = date.today()
                        historial_actual.save()
                    
                    # Crear nuevo historial
                    HistorialCargo.objects.create(
                        empleado=self.object,
                        cargo=cargo_nuevo,
                        fecha_inicio=date.today(),
                        activo=True,
                        motivo_cambio="Actualización de cargo",
                        creado_por=self.request.user
                    )
                
                response = super().form_valid(form)
                
                messages.success(
                    self.request, 
                    f'Empleado {self.object.nombre_completo} actualizado exitosamente.'
                )
                
                return response
                
        except Exception as e:
            logger.error(f"Error actualizando empleado: {str(e)}")
            messages.error(
                self.request,
                f'Error al actualizar el empleado: {str(e)}'
            )
            return self.form_invalid(form)


@login_required
def empleado_search_api(request):
    """API para búsqueda de empleados (autocompletado)"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    empleados = Empleado.objects.filter(
        Q(nombres__icontains=query) | 
        Q(apellidos__icontains=query) |
        Q(numero_documento__icontains=query)
    ).select_related('usuario', 'estado')[:limit]
    
    results = []
    for emp in empleados:
        results.append({
            'id': str(emp.pk),
            'text': emp.nombre_completo,
            'email': emp.correo_electronico,
            'documento': emp.numero_documento,
            'estado': emp.estado.nombre
        })
    
    return JsonResponse({'results': results})



def empleado_export(request):
    """Exportar lista de empleados - VERSIÓN MEJORADA"""
    formato = request.GET.get('export', 'excel')
    
    # Obtener empleados con los mismos filtros de la lista
    view = EmpleadoListView()
    view.request = request
    empleados = list(view.get_queryset())
    
    try:
        if formato == 'excel':
            return export_empleados_excel(empleados)
        elif formato == 'pdf':
            return export_empleados_pdf(empleados)
        elif formato == 'csv':
            return export_empleados_csv(empleados)
        else:
            messages.error(request, 'Formato de exportación no válido')
            return redirect('employees:empleado_list')
            
    except Exception as e:
        logger.error(f"Error en exportación {formato}: {e}")
        messages.error(request, f'Error al exportar: {str(e)}')
        return redirect('employees:empleado_list')

@login_required
def empleado_export_individual(request, pk):
    """Exportar perfil individual de empleado"""
    empleado = get_object_or_404(Empleado, pk=pk)
    formato = request.GET.get('format', 'pdf')
    
    try:
        if formato == 'pdf':
            return export_empleado_perfil_pdf(empleado)
        elif formato == 'excel':
            return export_empleado_excel(empleado)
        else:
            messages.error(request, 'Formato no válido')
            return redirect('employees:empleado_detail', pk=pk)
            
    except Exception as e:
        logger.error(f"Error en exportación individual {formato}: {e}")
        messages.error(request, f'Error al generar {formato.upper()}: {str(e)}')
        return redirect('employees:empleado_detail', pk=pk)


@login_required
def empleado_print_view(request, pk):
    """Vista optimizada para impresión del empleado"""
    empleado = get_object_or_404(Empleado, pk=pk)
    
    # Obtener datos adicionales
    historial_cargos = empleado.historialcargo_set.select_related(
        'cargo__area'
    ).order_by('-fecha_inicio')
    
    context = {
        'empleado': empleado,
        'historial_cargos': historial_cargos,
        'fecha_generacion': timezone.now(),
    }
    
    return render(request, 'employees/empleado_print.html', context)


@login_required
def empleado_historial_export(request, pk):
    """Exportar historial completo de cambios del empleado"""
    empleado = get_object_or_404(Empleado, pk=pk)
    formato = request.GET.get('format', 'pdf')
    
    try:
        historial_cargos = empleado.historialcargo_set.all().order_by('-fecha_inicio')
        
        if formato == 'excel':
            return export_historial_excel(empleado, historial_cargos)
        else:  # PDF por defecto
            return export_historial_pdf(empleado, historial_cargos)
            
    except Exception as e:
        logger.error(f"Error exportando historial: {e}")
        messages.error(request, f'Error al exportar historial: {str(e)}')
        return redirect('employees:empleado_detail', pk=pk)


# Funciones auxiliares para historial
def export_historial_excel(empleado, historial_cargos):
    """Exportar historial de cargos a Excel"""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Border, Side
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Historial de Cargos'
        
        # Título
        worksheet.merge_cells('A1:F1')
        title_cell = worksheet['A1']
        title_cell.value = f"HISTORIAL DE CARGOS - {empleado.nombre_completo.upper()}"
        title_cell.font = Font(bold=True, size=14)
        
        # Encabezados
        headers = ['Cargo', 'Área', 'Fecha Inicio', 'Fecha Fin', 'Estado', 'Motivo del Cambio']
        
        for col, header in enumerate(headers, 1):
            cell = worksheet.cell(row=3, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Datos
        for row, hist in enumerate(historial_cargos, 4):
            worksheet.cell(row=row, column=1, value=hist.cargo.nombre)
            worksheet.cell(row=row, column=2, value=hist.cargo.area.nombre)
            worksheet.cell(row=row, column=3, value=hist.fecha_inicio)
            worksheet.cell(row=row, column=4, value=hist.fecha_fin or 'Actual')
            worksheet.cell(row=row, column=5, value='Activo' if hist.activo else 'Finalizado')
            worksheet.cell(row=row, column=6, value=hist.motivo_cambio or '-')
        
        # Ajustar columnas
        for col in range(1, 7):
            worksheet.column_dimensions[chr(64 + col)].width = 20
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'historial_{empleado.nombres}_{empleado.apellidos}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        workbook.save(response)
        return response
        
    except Exception as e:
        return HttpResponse(f"Error: {e}", content_type="text/plain", status=500)


def export_historial_pdf(empleado, historial_cargos):
    """Exportar historial de cargos a PDF"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        response = HttpResponse(content_type='application/pdf')
        filename = f'historial_{empleado.nombres}_{empleado.apellidos}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph(f"HISTORIAL DE CARGOS<br/>{empleado.nombre_completo}", styles['Title'])
        elements.append(title)
        
        # Datos
        data = [['Cargo', 'Área', 'Fecha Inicio', 'Fecha Fin', 'Estado', 'Motivo']]
        
        for hist in historial_cargos:
            data.append([
                hist.cargo.nombre,
                hist.cargo.area.nombre,
                hist.fecha_inicio.strftime('%d/%m/%Y'),
                hist.fecha_fin.strftime('%d/%m/%Y') if hist.fecha_fin else 'Actual',
                'Activo' if hist.activo else 'Finalizado',
                hist.motivo_cambio or '-'
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error: {e}", content_type="text/plain", status=500)