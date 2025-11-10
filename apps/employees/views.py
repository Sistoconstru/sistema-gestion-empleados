# =============================================================================
# apps/employees/views.py - VISTAS CORREGIDAS DE EMPLEADOS
# =============================================================================

# Importaciones estándar
import json
import logging
from datetime import timedelta, date

# Importaciones de Django
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg, Prefetch
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction

# Importaciones locales
from .exports import export_empleados_excel, export_empleados_pdf, export_empleados_csv, export_empleado_perfil_pdf, export_empleado_excel
from .models import Empleado, TipoDocumento, Escolaridad, EstadoEmpleado, HistorialCargo
from .forms import EmpleadoForm, BusquedaEmpleadoForm
from apps.organizational.models import AreaEmpresa, Cargo, Sede
from apps.training.models import InscripcionCapacitacion
from apps.evaluations.models import AsignacionEvaluacion
from apps.documents.models import DocumentoEmpleado, TipoDocumentoEmpleado
from apps.recognition.models import HistorialPuntos, InsigniaEmpleado


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
                Q(nombres__istartswith=search) |
                Q(apellidos__istartswith=search)
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
        
        return queryset.distinct().order_by('nombres', 'apellidos')
    
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
        
        # Capacitaciones con todas las relaciones necesarias
        try:
            context['capacitaciones'] = InscripcionCapacitacion.objects.filter(
                empleado=empleado
            ).select_related(
                'capacitacion',
                'capacitacion__tipo',
                'inscrito_por',
                'aprobado_por'
            ).prefetch_related(
                'capacitacion__modulocapacitacion_set'
            ).order_by('-fecha_inscripcion')
            
            # Calcular estadísticas de capacitaciones
            capacitaciones = context['capacitaciones']
            context.update({
                'capacitaciones_obligatorias': capacitaciones.filter(
                    capacitacion__tipo__codigo='OBLIGATORIA'
                ).count(),
                'capacitaciones_en_progreso': capacitaciones.filter(
                    estado='en_progreso'
                ).count(),
                'capacitaciones_completadas': capacitaciones.filter(
                    estado='completado'
                ).count()
            })
            
        except Exception as e:
            context['capacitaciones'] = []
            context.update({
                'capacitaciones_obligatorias': 0,
                'capacitaciones_en_progreso': 0,
                'capacitaciones_completadas': 0
            })
        
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
        
        # Obtener cargo actual
        cargo_actual = empleado.historialcargo_set.filter(activo=True).first()
        context['cargo_actual'] = cargo_actual
        
        # Obtener capacitaciones obligatorias del cargo actual
        if cargo_actual:
            try:
                context['capacitaciones_cargo'] = InscripcionCapacitacion.objects.filter(
                    cargo=cargo_actual.cargo,
                    capacitacion__tipo__codigo='OBLIGATORIA'
                ).exclude(
                    empleado=empleado
                ).select_related('capacitacion')
            except:
                context['capacitaciones_cargo'] = []
        
        # Datos de reconocimientos (solo para administradores)
        if self.request.user.is_staff:
            try:
                from django.db.models import Sum, Count, Q
                from django.db.models.functions import Coalesce
                
                # Calcular puntos totales
                puntos_totales = HistorialPuntos.objects.filter(
                    empleado=empleado,
                    validado=True
                ).aggregate(total=Sum('puntos'))['total'] or 0
                
                # Puntos del mes actual
                inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                puntos_mes = HistorialPuntos.objects.filter(
                    empleado=empleado,
                    validado=True,
                    fecha_obtencion__gte=inicio_mes
                ).aggregate(total=Sum('puntos'))['total'] or 0
                
                # Posición en ranking
                from apps.employees.models import Empleado
                empleados_ranking = Empleado.objects.exclude(estado__codigo='inactivo').annotate(
                    puntos_totales=Coalesce(
                        Sum('historialpuntos__puntos', filter=Q(historialpuntos__validado=True)), 
                        0
                    )
                ).order_by('-puntos_totales')
                
                ranking_posicion = None
                for i, emp in enumerate(empleados_ranking, 1):
                    if emp.id == empleado.id:
                        ranking_posicion = i
                        break
                
                # Número de actividades
                actividades_count = HistorialPuntos.objects.filter(
                    empleado=empleado,
                    validado=True
                ).count()
                
                # Historial reciente de puntos (últimos 30 días)
                hace_30_dias = timezone.now() - timedelta(days=30)
                historial_puntos = HistorialPuntos.objects.filter(
                    empleado=empleado,
                    fecha_obtencion__gte=hace_30_dias
                ).select_related('tipo_actividad', 'validado_por').order_by('-fecha_obtencion')[:10]
                
                # Datos de insignias
                insignias_empleado = InsigniaEmpleado.objects.filter(
                    empleado=empleado
                ).select_related('tipo_insignia', 'otorgado_por').order_by('-fecha_otorgamiento')
                
                insignias_count = insignias_empleado.count()
                
                # Insignias del mes
                insignias_mes = insignias_empleado.filter(
                    fecha_otorgamiento__gte=inicio_mes
                ).count()
                
                # Insignias especiales (manualmente otorgadas)
                insignias_especiales = insignias_empleado.filter(
                    otorgado_automaticamente=False
                ).count()
                
                # Agregar al contexto
                context.update({
                    'puntos_totales': puntos_totales,
                    'puntos_mes': puntos_mes,
                    'ranking_posicion': ranking_posicion,
                    'actividades_count': actividades_count,
                    'historial_puntos': historial_puntos,
                    'insignias_empleado': insignias_empleado,
                    'insignias_count': insignias_count,
                    'insignias_mes': insignias_mes,
                    'insignias_especiales': insignias_especiales,
                })
                
                # Agregar datos al empleado para uso en template
                empleado.puntos_totales = puntos_totales
                empleado.puntos_mes = puntos_mes
                empleado.ranking_posicion = ranking_posicion
                empleado.actividades_count = actividades_count
                empleado.insignias_count = insignias_count
                empleado.insignias_mes = insignias_mes
                empleado.insignias_especiales = insignias_especiales
                
            except ImportError:
                # Módulo de reconocimientos no disponible
                pass
            except Exception as e:
                # Error al obtener datos de reconocimientos
                pass
        
        # Agregar datos necesarios para el modal de cambio de cargo
        # Excluir el cargo actual del empleado de la lista
        cargo_actual_id = None
        if cargo_actual and cargo_actual.cargo:
            cargo_actual_id = cargo_actual.cargo.id
        
        if cargo_actual_id:
            context['cargos'] = Cargo.objects.filter(activo=True).exclude(id=cargo_actual_id).order_by('nombre')
        else:
            context['cargos'] = Cargo.objects.filter(activo=True).order_by('nombre')
            
        context['sedes'] = Sede.objects.filter(activa=True).order_by('nombre')
        
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
                        estado_prueba = EstadoEmpleado.objects.get(codigo='p-prue')
                        form.instance.estado = estado_prueba
                    except EstadoEmpleado.DoesNotExist:
                        logger.warning("Estado código 'p-prue' (Periodo de prueba) no encontrado")
                        # Usar el primer estado disponible
                        form.instance.estado = EstadoEmpleado.objects.first()
                else:
                    try:
                        estado_activo = EstadoEmpleado.objects.get(codigo='999')
                        form.instance.estado = estado_activo
                    except EstadoEmpleado.DoesNotExist:
                        logger.warning("Estado código '999' (Activo) no encontrado")
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
    
    def get_initial(self):
        """Preparar datos iniciales del formulario"""
        initial = super().get_initial()
        # Formatear las fechas en el formato correcto para el input type="date"
        if self.object.fecha_ingreso:
            initial['fecha_ingreso'] = self.object.fecha_ingreso.strftime('%Y-%m-%d')
        if self.object.fecha_nacimiento:
            initial['fecha_nacimiento'] = self.object.fecha_nacimiento.strftime('%Y-%m-%d')
        
        # Obtener el cargo actual si existe
        cargo_actual = self.object.historialcargo_set.filter(activo=True).first()
        if cargo_actual:
            initial['cargo'] = cargo_actual.cargo
        
        return initial
    
    def get_success_url(self):
        return reverse_lazy('employees:empleado_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Procesar cambios en el formulario"""
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(
                    self.request, 
                    f'Empleado {self.object.nombre_completo} actualizado exitosamente.'
                )
                return response
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
    

class EmpleadoPerfilView(LoginRequiredMixin, DetailView):
    """Vista del perfil personal del empleado - Dashboard personal"""
    model = Empleado
    template_name = 'employees/empleado_perfil.html'
    context_object_name = 'empleado'
    
    def get_object(self):
        """Obtener el empleado asociado al usuario logueado o por PK"""
        # Si se pasa pk en la URL, usar ese empleado
        if 'pk' in self.kwargs:
            return get_object_or_404(Empleado, pk=self.kwargs['pk'])
        
        # Si no hay pk, buscar empleado del usuario logueado
        try:
            empleado = Empleado.objects.get(usuario=self.request.user)
            return empleado
        except Empleado.DoesNotExist:
            # Si no hay empleado asociado, mostrar error 404
            raise Http404("No se encontró un perfil de empleado asociado a tu usuario.")
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar permisos antes de mostrar la vista"""
        try:
            empleado = self.get_object()
            
            # Verificar si el usuario puede ver este perfil
            if empleado.usuario != request.user and not request.user.is_staff:
                messages.error(
                    request, 
                    'No tienes permisos para ver este perfil.'
                )
                return redirect('core:dashboard')
            
            return super().dispatch(request, *args, **kwargs)
            
        except Http404:
            messages.error(
                request, 
                'No se encontró un perfil de empleado asociado a tu usuario. Contacta al administrador.'
            )
            return redirect('core:dashboard')
        except Exception as e:
            logger.error(f"Error en dispatch de EmpleadoPerfilView: {e}")
            messages.error(request, 'Error al acceder al perfil.')
            return redirect('core:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = self.get_object()
        
        # === INFORMACIÓN BÁSICA ===
        context.update(self.get_informacion_basica(empleado))
        
        # === ESTADO DE DOCUMENTOS ===
        context.update(self.get_estado_documentos(empleado))
        
        # === CAPACITACIONES ===
        context.update(self.get_capacitaciones(empleado))
        
        # === EVALUACIONES ===
        context.update(self.get_evaluaciones(empleado))
        
        # === SISTEMA DE PUNTOS ===
        context.update(self.get_sistema_puntos(empleado))
        
        # === NOTIFICACIONES RECIENTES ===
        context.update(self.get_notificaciones(empleado))
        
        # === ACTIVIDAD RECIENTE ===
        context.update(self.get_actividad_reciente(empleado))
        
        return context
    
    def get_informacion_basica(self, empleado):
        """Obtener información básica del empleado"""
        # Cargo actual
        cargo_actual = empleado.historialcargo_set.filter(activo=True).first()
        
        # Días en la empresa
        dias_empresa = (date.today() - empleado.fecha_ingreso).days
        
        # Formatear tiempo en empresa de forma amigable
        tiempo_empresa_texto = self.formatear_tiempo_empresa(dias_empresa)
        
        # Tiempo en cargo actual
        tiempo_cargo = None
        if cargo_actual:
            tiempo_cargo = (date.today() - cargo_actual.fecha_inicio).days
        
        return {
            'cargo_actual': cargo_actual,
            'dias_empresa': dias_empresa,
            'tiempo_empresa_texto': tiempo_empresa_texto,
            'tiempo_cargo': tiempo_cargo,
            'anos_empresa': dias_empresa // 365,
        }
    
    def formatear_tiempo_empresa(self, dias_totales):
        """
        Formatear el tiempo en la empresa de forma amigable:
        - Menos de 30 días: "X días"
        - Menos de 365 días: "X meses y Y días"
        - 365 días o más: "X años, Y meses y Z días"
        """
        if dias_totales < 30:
            return f"{dias_totales} día{'s' if dias_totales != 1 else ''}"
        
        elif dias_totales < 365:
            meses = dias_totales // 30
            dias_restantes = dias_totales % 30
            
            texto = f"{meses} mes{'es' if meses != 1 else ''}"
            if dias_restantes > 0:
                texto += f" y {dias_restantes} día{'s' if dias_restantes != 1 else ''}"
            
            return texto
        
        else:
            anos = dias_totales // 365
            dias_restantes = dias_totales % 365
            meses = dias_restantes // 30
            dias = dias_restantes % 30
            
            texto = f"{anos} año{'s' if anos != 1 else ''}"
            
            if meses > 0:
                texto += f", {meses} mes{'es' if meses != 1 else ''}"
            
            if dias > 0:
                texto += f" y {dias} día{'s' if dias != 1 else ''}"
            
            return texto
    
    def get_estado_documentos(self, empleado):
        """Obtener estado de documentos del empleado"""
        try:
            # Importar aquí para evitar errores si no existe el módulo
            from apps.documents.models import DocumentoEmpleado, TipoDocumentoEmpleado
            
            # Documentos del empleado
            documentos = DocumentoEmpleado.objects.filter(empleado=empleado)
            
            # Tipos de documentos obligatorios
            tipos_obligatorios = TipoDocumentoEmpleado.objects.filter(
                obligatorio=True, 
                activo=True
            )
            
            # Documentos aprobados
            docs_aprobados = documentos.filter(estado_aprobacion='aprobado')
            
            # Documentos pendientes
            docs_pendientes = documentos.filter(estado_aprobacion='pendiente')
            
            # Documentos próximos a vencer (30 días)
            fecha_limite = date.today() + timedelta(days=30)
            docs_por_vencer = docs_aprobados.filter(
                fecha_vencimiento__isnull=False,
                fecha_vencimiento__lte=fecha_limite,
                fecha_vencimiento__gte=date.today()
            )
            
            # Documentos vencidos
            docs_vencidos = docs_aprobados.filter(
                fecha_vencimiento__isnull=False,
                fecha_vencimiento__lt=date.today()
            )
            
            # Documentos faltantes (obligatorios no subidos)
            tipos_subidos = documentos.values_list('tipo_documento_id', flat=True)
            tipos_faltantes = tipos_obligatorios.exclude(id__in=tipos_subidos)
            
            # Calcular progreso de documentación
            total_obligatorios = tipos_obligatorios.count()
            aprobados_obligatorios = docs_aprobados.filter(
                tipo_documento__in=tipos_obligatorios
            ).count()
            
            progreso_documentos = 0
            if total_obligatorios > 0:
                progreso_documentos = round((aprobados_obligatorios / total_obligatorios) * 100)
            
            return {
                'documentos': {
                    'total': documentos.count(),
                    'aprobados': docs_aprobados.count(),
                    'pendientes': docs_pendientes.count(),
                    'por_vencer': docs_por_vencer.count(),
                    'vencidos': docs_vencidos.count(),
                    'faltantes': tipos_faltantes.count(),
                    'progreso': progreso_documentos,
                    'lista_por_vencer': docs_por_vencer[:5],  # Primeros 5
                    'lista_vencidos': docs_vencidos[:5],
                    'lista_faltantes': tipos_faltantes[:5],
                    'documentacion_completa': tipos_faltantes.count() == 0 and docs_pendientes.count() == 0
                }
            }
        except ImportError:
            logger.info("Módulo de documentos no disponible")
            return {
                'documentos': {
                    'total': 0, 'aprobados': 0, 'pendientes': 0,
                    'por_vencer': 0, 'vencidos': 0, 'faltantes': 0,
                    'progreso': 0, 'documentacion_completa': True,
                    'lista_por_vencer': [], 'lista_vencidos': [], 'lista_faltantes': []
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo estado de documentos: {e}")
            return {
                'documentos': {
                    'total': 0, 'aprobados': 0, 'pendientes': 0,
                    'por_vencer': 0, 'vencidos': 0, 'faltantes': 0,
                    'progreso': 0, 'documentacion_completa': False,
                    'lista_por_vencer': [], 'lista_vencidos': [], 'lista_faltantes': []
                }
            }
    
    def get_capacitaciones(self, empleado):
        """Obtener estado de capacitaciones del empleado"""
        try:
            from apps.training.models import InscripcionCapacitacion, Capacitacion
            
            # Capacitaciones asignadas
            inscripciones = InscripcionCapacitacion.objects.filter(
                empleado=empleado
            ).select_related('capacitacion')
            
            # Estados
            completadas = inscripciones.filter(estado='completado')
            en_progreso = inscripciones.filter(estado='en_progreso')
            pendientes = inscripciones.filter(
                estado='no_iniciado'
            )
            
            # Próximas a vencer (si tienen fecha límite)
            fecha_limite = date.today() + timedelta(days=7)
            proximas_vencer = en_progreso.filter(
                fecha_limite__isnull=False,
                fecha_limite__lte=fecha_limite
            )
            
            # Progreso general
            total_capacitaciones = inscripciones.count()
            capacitaciones_completadas = completadas.count()
            
            progreso_capacitaciones = 0
            if total_capacitaciones > 0:
                progreso_capacitaciones = round(
                    (capacitaciones_completadas / total_capacitaciones) * 100
                )
            
            return {
                'capacitaciones': {
                    'total': total_capacitaciones,
                    'completadas': capacitaciones_completadas,
                    'en_progreso': en_progreso.count(),
                    'pendientes': pendientes.count(),
                    'proximas_vencer': proximas_vencer.count(),
                    'progreso': progreso_capacitaciones,
                    'lista_pendientes': pendientes[:5],
                    'lista_en_progreso': en_progreso[:5],
                    'lista_proximas_vencer': proximas_vencer[:3],
                }
            }
        except ImportError:
            logger.info("Módulo de capacitaciones no disponible")
            return {
                'capacitaciones': {
                    'total': 0, 'completadas': 0, 'en_progreso': 0,
                    'pendientes': 0, 'progreso': 100,
                    'lista_pendientes': [], 'lista_en_progreso': [], 'lista_proximas_vencer': []
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo capacitaciones: {e}")
            return {
                'capacitaciones': {
                    'total': 0, 'completadas': 0, 'en_progreso': 0,
                    'pendientes': 0, 'progreso': 0,
                    'lista_pendientes': [], 'lista_en_progreso': [], 'lista_proximas_vencer': []
                }
            }
    
    def get_evaluaciones(self, empleado):
        """Obtener estado de evaluaciones del empleado"""
        try:
            from apps.evaluations.models import AsignacionEvaluacion
            
            # Evaluaciones asignadas
            evaluaciones = AsignacionEvaluacion.objects.filter(
                empleado_evaluado=empleado
            ).select_related('evaluacion', 'evaluador')
            
            # Pendientes (no completadas y no vencidas)
            pendientes = evaluaciones.filter(
                fecha_completada__isnull=True,
                fecha_vencimiento__gte=date.today()
            )
            
            # Vencidas (no completadas y vencidas)
            vencidas = evaluaciones.filter(
                fecha_completada__isnull=True,
                fecha_vencimiento__lt=date.today()
            )
            
            # Completadas este año
            completadas_año = evaluaciones.filter(
                fecha_completada__year=date.today().year
            )
            
            # Próximas (siguientes 15 días)
            fecha_limite = date.today() + timedelta(days=15)
            proximas = pendientes.filter(fecha_vencimiento__lte=fecha_limite)
            
            return {
                'evaluaciones': {
                    'pendientes': pendientes.count(),
                    'vencidas': vencidas.count(),
                    'completadas_año': completadas_año.count(),
                    'proximas': proximas.count(),
                    'lista_pendientes': pendientes[:5],
                    'lista_proximas': proximas[:3],
                    'ultima_evaluacion': evaluaciones.filter(fecha_completada__isnull=False).order_by('-fecha_completada').first()
                }
            }
        except ImportError:
            logger.info("Módulo de evaluaciones no disponible")
            return {
                'evaluaciones': {
                    'pendientes': 0, 'vencidas': 0, 'completadas_año': 0,
                    'proximas': 0, 'lista_pendientes': [], 'lista_proximas': [],
                    'ultima_evaluacion': None
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo evaluaciones: {e}")
            return {
                'evaluaciones': {
                    'pendientes': 0, 'vencidas': 0, 'completadas_año': 0,
                    'proximas': 0, 'lista_pendientes': [], 'lista_proximas': [],
                    'ultima_evaluacion': None
                }
            }
    
    def get_sistema_puntos(self, empleado):
        """Obtener información del sistema de puntos y reconocimientos"""
        try:
            from apps.recognition.models import HistorialPuntos, InsigniaEmpleado
            from django.db import models
            
            # Puntos totales
            puntos_totales = HistorialPuntos.objects.filter(
                empleado=empleado,
                validado=True
            ).aggregate(
                total=models.Sum('puntos')
            )['total'] or 0
            
            # Puntos este mes
            inicio_mes = date.today().replace(day=1)
            puntos_mes = HistorialPuntos.objects.filter(
                empleado=empleado,
                validado=True,
                fecha_obtencion__gte=inicio_mes
            ).aggregate(
                total=models.Sum('puntos')
            )['total'] or 0
            
            # Insignias obtenidas
            insignias = InsigniaEmpleado.objects.filter(
                empleado=empleado
            ).select_related('tipo_insignia')
            
            # Posición en ranking (aproximada)
            empleados_mas_puntos = HistorialPuntos.objects.filter(
                validado=True
            ).values('empleado').annotate(
                total_puntos=models.Sum('puntos')
            ).filter(
                total_puntos__gt=puntos_totales
            ).count()
            
            posicion_ranking = empleados_mas_puntos + 1 if puntos_totales > 0 else 0
            
            return {
                'puntos': {
                    'total': puntos_totales,
                    'este_mes': puntos_mes,
                    'insignias': insignias.count(),
                    'lista_insignias': insignias[:10],
                    'ranking_posicion': posicion_ranking,
                    'puntos_disponibles': puntos_totales  # Para canje
                }
            }
        except ImportError:
            logger.info("Módulo de reconocimientos no disponible")
            return {
                'puntos': {
                    'total': 0, 'este_mes': 0, 'insignias': 0,
                    'ranking_posicion': 0, 'lista_insignias': [],
                    'puntos_disponibles': 0
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo sistema de puntos: {e}")
            return {
                'puntos': {
                    'total': 0, 'este_mes': 0, 'insignias': 0,
                    'ranking_posicion': 0, 'lista_insignias': [],
                    'puntos_disponibles': 0
                }
            }
    
    def get_notificaciones(self, empleado):
        """Obtener notificaciones recientes del empleado"""
        try:
            from apps.notifications.models import NotificacionEmpleado
            
            # Notificaciones recientes (últimos 7 días)
            fecha_limite = timezone.now() - timedelta(days=7)
            notificaciones = NotificacionEmpleado.objects.filter(
                empleado=empleado,
                fecha_creacion__gte=fecha_limite
            ).order_by('-fecha_creacion')[:10]
            
            # No leídas
            no_leidas = NotificacionEmpleado.objects.filter(
                empleado=empleado,
                leida=False
            ).count()
            
            return {
                'notificaciones': {
                    'recientes': notificaciones,
                    'no_leidas': no_leidas,
                    'total_recientes': notificaciones.count()
                }
            }
        except ImportError:
            logger.info("Módulo de notificaciones no disponible")
            return {
                'notificaciones': {
                    'recientes': [], 'no_leidas': 0, 'total_recientes': 0
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo notificaciones: {e}")
            return {
                'notificaciones': {
                    'recientes': [], 'no_leidas': 0, 'total_recientes': 0
                }
            }
    
    def get_actividad_reciente(self, empleado):
        """Obtener actividad reciente del empleado"""
        actividades = []
        
        try:
            # Documentos subidos recientemente
            try:
                from apps.documents.models import DocumentoEmpleado
                
                docs_recientes = DocumentoEmpleado.objects.filter(
                    empleado=empleado,
                    fecha_carga__gte=timezone.now() - timedelta(days=15)
                ).order_by('-fecha_carga')[:3]
                
                for doc in docs_recientes:
                    actividades.append({
                        'tipo': 'documento',
                        'icono': 'fas fa-file-upload',
                        'titulo': f'Documento subido: {doc.tipo_documento.nombre}',
                        'fecha': doc.fecha_carga,
                        'estado': doc.estado_aprobacion
                    })
            except ImportError:
                pass
            
            # Capacitaciones completadas recientemente
            try:
                from apps.training.models import InscripcionCapacitacion
                
                caps_completadas = InscripcionCapacitacion.objects.filter(
                    empleado=empleado,
                    estado='completado',
                    fecha_finalizacion__gte=timezone.now() - timedelta(days=15)
                ).order_by('-fecha_finalizacion')[:3]
                
                for cap in caps_completadas:
                    actividades.append({
                        'tipo': 'capacitacion',
                        'icono': 'fas fa-graduation-cap',
                        'titulo': f'Capacitación completada: {cap.capacitacion.nombre}',
                        'fecha': cap.fecha_finalizacion,
                        'estado': 'completado'
                    })
            except ImportError:
                pass
            
            # Ordenar por fecha
            actividades.sort(key=lambda x: x['fecha'], reverse=True)
            
            return {
                'actividades_recientes': actividades[:10]
            }
        except Exception as e:
            logger.error(f"Error obteniendo actividad reciente: {e}")
            return {
                'actividades_recientes': []
            }


@login_required
def empleado_perfil_redirect(request):
    """Vista para redirigir al perfil del empleado logueado"""
    try:
        empleado = get_object_or_404(Empleado, usuario=request.user)
        return redirect('employees:empleado_perfil_detail', pk=empleado.pk)
    except Empleado.DoesNotExist:
        messages.error(
            request, 
            'No se encontró un perfil de empleado asociado a tu usuario. Contacta al administrador.'
        )
        return redirect('core:dashboard')
    except Exception as e:
        logger.error(f"Error en empleado_perfil_redirect: {e}")
        messages.error(request, 'Error al acceder al perfil del empleado.')
        return redirect('core:dashboard')


@login_required
@require_POST
def cambiar_cargo_empleado(request, pk):
    """Vista para cambiar el cargo de un empleado"""
    try:
        empleado = get_object_or_404(Empleado, pk=pk)
        
        # Verificar permisos (solo staff puede cambiar cargos)
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'No tienes permisos para realizar esta acción'})
        
        # Obtener datos del formulario
        nuevo_cargo_id = request.POST.get('nuevo_cargo')
        nueva_sede_id = request.POST.get('nueva_sede')
        fecha_inicio = request.POST.get('fecha_inicio')
        salario = request.POST.get('salario')
        motivo = request.POST.get('motivo', '')
        
        # Validaciones
        if not all([nuevo_cargo_id, nueva_sede_id, fecha_inicio]):
            return JsonResponse({'success': False, 'message': 'Todos los campos obligatorios deben ser completados'})
        
        try:
            nuevo_cargo = Cargo.objects.get(pk=nuevo_cargo_id, activo=True)
            nueva_sede = Sede.objects.get(pk=nueva_sede_id, activa=True)
            
            # Salario es opcional
            salario_valor = None
            if salario and salario.strip():
                salario_valor = float(salario)
                if salario_valor <= 0:
                    return JsonResponse({'success': False, 'message': 'El salario debe ser mayor a 0'})
            else:
                # Si no se proporciona salario, mantener el actual
                cargo_actual = empleado.historialcargo_set.filter(activo=True).first()
                if cargo_actual and cargo_actual.salario:
                    salario_valor = cargo_actual.salario
                
        except (Cargo.DoesNotExist, Sede.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Cargo o sede no válidos'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Salario no válido'})
        
        # Verificar que no sea el mismo cargo actual
        cargo_actual_check = empleado.historialcargo_set.filter(activo=True).first()
        if cargo_actual_check and cargo_actual_check.cargo.id == int(nuevo_cargo_id):
            return JsonResponse({'success': False, 'message': 'El empleado ya tiene asignado este cargo'})
        
        # Realizar el cambio de cargo en una transacción
        with transaction.atomic():
            # Desactivar cargo actual
            if cargo_actual_check:
                cargo_actual_check.activo = False
                cargo_actual_check.fecha_fin = fecha_inicio
                cargo_actual_check.save()
            
            # Crear nuevo historial de cargo
            nuevo_historial = HistorialCargo.objects.create(
                empleado=empleado,
                cargo=nuevo_cargo,
                fecha_inicio=fecha_inicio,
                salario=salario_valor,
                motivo_cambio=motivo,
                activo=True,
                creado_por=request.user
            )
            
            # Actualizar datos del empleado
            empleado.cargo = nuevo_cargo
            empleado.sede = nueva_sede
            if salario_valor:
                empleado.salario = salario_valor
            empleado.modificado_por = request.user
            empleado.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Cargo cambiado exitosamente a {nuevo_cargo.nombre}'
        })
        
    except Exception as e:
        logger.error(f"Error al cambiar cargo del empleado {pk}: {e}")
        return JsonResponse({'success': False, 'message': 'Error interno del servidor'})


@login_required
def empleados_periodo_prueba_reporte(request):
    """Vista para mostrar empleados en periodo de prueba y sus fechas de activación automática"""
    
    try:
        # Obtener estado de periodo de prueba
        estado_prueba = EstadoEmpleado.objects.get(codigo='p-prue')
    except EstadoEmpleado.DoesNotExist:
        messages.error(request, 'No se encontró el estado de periodo de prueba')
        return redirect('employees:empleado_list')
    
    # Obtener días de antelación de los parámetros GET o usar 7 por defecto
    dias_antelacion = int(request.GET.get('dias_antelacion', 7))
    if dias_antelacion < 1 or dias_antelacion > 30:
        dias_antelacion = 7
    
    # Obtener empleados en periodo de prueba
    empleados_prueba = Empleado.objects.filter(
        estado=estado_prueba
    ).select_related(
        'sede', 'tipo_documento', 'estado'
    ).prefetch_related(
        'historialcargo_set__cargo__area'
    ).order_by('fecha_ingreso')
    
    # Calcular información de activación para cada empleado
    empleados_info = []
    hoy = timezone.now().date()
    
    for empleado in empleados_prueba:
        dias_transcurridos = (hoy - empleado.fecha_ingreso).days
        dias_restantes = 90 - dias_transcurridos
        fecha_activacion = empleado.fecha_ingreso + timedelta(days=90)
        
        # Determinar estado de activación
        if dias_transcurridos >= 90:
            estado_activacion = 'Listo para activar'
        elif dias_restantes <= dias_antelacion:
            estado_activacion = f'Próximo a activar'
        else:
            estado_activacion = f'En período de prueba'
        
        empleados_info.append({
            'empleado': empleado,
            'dias_transcurridos': dias_transcurridos,
            'dias_restantes': max(0, dias_restantes),
            'fecha_activacion': fecha_activacion,
            'estado_activacion': estado_activacion,
            'cargo_actual': empleado.cargo_actual,
        })
    
    # Estadísticas generales
    total_empleados = len(empleados_info)
    listos_activar = len([e for e in empleados_info if e['dias_restantes'] == 0])
    proximos_activar = len([e for e in empleados_info if 0 < e['dias_restantes'] <= dias_antelacion])
    
    context = {
        'empleados_info': empleados_info,
        'total_empleados': total_empleados,
        'listos_activar': listos_activar,
        'proximos_activar': proximos_activar,
        'fecha_actual': hoy,
        'dias_antelacion': dias_antelacion,
    }
    
    return render(request, 'employees/periodo_prueba_reporte.html', context)


# Agregar import para agregaciones
from django.db import models