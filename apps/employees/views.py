# =============================================================================
# apps/employees/views.py - VISTAS COMPLETAS DE EMPLEADOS
# =============================================================================

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
from datetime import timedelta, date
import json

from .models import Empleado, TipoDocumento, Escolaridad, EstadoEmpleado, HistorialCargo
from .forms import EmpleadoForm, BusquedaEmpleadoForm
from apps.organizational.models import AreaEmpresa, Cargo, Sede
from apps.training.models import InscripcionCapacitacion
from apps.evaluations.models import AsignacionEvaluacion


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
        context['capacitaciones'] = InscripcionCapacitacion.objects.filter(
            empleado=empleado
        ).select_related('capacitacion').order_by('-fecha_inscripcion')[:10]
        
        # Evaluaciones
        context['evaluaciones'] = AsignacionEvaluacion.objects.filter(
            empleado_evaluado=empleado
        ).select_related('evaluacion', 'evaluador').order_by('-fecha_asignacion')[:5]
        
        # Simulación de documentos (implementar cuando esté el módulo de documentos)
        context['documentos_completos'] = 3
        context['documentos_pendientes'] = 1
        
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
        """Procesar formulario válido"""
        # Asignar usuario creador
        form.instance.creado_por = self.request.user
        
        # Determinar estado inicial basado en fecha de ingreso
        dias_desde_ingreso = (date.today() - form.instance.fecha_ingreso).days
        
        if dias_desde_ingreso <= 60:  # Período de prueba
            try:
                estado_prueba = EstadoEmpleado.objects.get(codigo='PRUEBA')
                form.instance.estado = estado_prueba
            except EstadoEmpleado.DoesNotExist:
                pass
        else:
            try:
                estado_activo = EstadoEmpleado.objects.get(codigo='ACTIVO')
                form.instance.estado = estado_activo
            except EstadoEmpleado.DoesNotExist:
                pass
        
        # Crear usuario del sistema si tiene email
        if form.instance.correo_electronico:
            self.crear_usuario_sistema(form.instance)
        
        response = super().form_valid(form)
        
        # Crear historial de cargo inicial
        cargo = form.cleaned_data.get('cargo')
        if cargo:
            HistorialCargo.objects.create(
                empleado=form.instance,
                cargo=cargo,
                fecha_inicio=form.instance.fecha_ingreso,
                activo=True,
                motivo_cambio='Cargo inicial',
                creado_por=self.request.user
            )
        
        messages.success(
            self.request, 
            f'Empleado {form.instance.nombre_completo} creado exitosamente.'
        )
        
        return response
    
    def crear_usuario_sistema(self, empleado):
        """Crear usuario del sistema para el empleado"""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Verificar que no exista el usuario
        if User.objects.filter(email=empleado.correo_electronico).exists():
            return None
        
        # Generar username único
        base_username = f"{empleado.nombres.split()[0].lower()}.{empleado.apellidos.split()[0].lower()}"
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=empleado.correo_electronico,
            first_name=empleado.nombres,
            last_name=empleado.apellidos,
            password='temporal123',  # TODO: Implementar generador seguro
            is_active=True
        )
        
        empleado.usuario = user
        empleado.save(update_fields=['usuario'])
        
        return user


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
        # Verificar cambio de cargo
        cargo_nuevo = form.cleaned_data.get('cargo')
        cargo_actual = None
        
        try:
            historial_actual = self.object.historialcargo_set.filter(activo=True).first()
            if historial_actual:
                cargo_actual = historial_actual.cargo
        except:
            pass
        
        response = super().form_valid(form)
        
        # Si cambió el cargo, crear nuevo historial
        if cargo_nuevo and cargo_nuevo != cargo_actual:
            # Finalizar cargo actual
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
                motivo_cambio='Cambio de cargo',
                creado_por=self.request.user
            )
        
        return response


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
    ).select_related('usuario')[:limit]
    
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


@login_required 
def empleado_export(request):
    """Exportar lista de empleados"""
    formato = request.GET.get('export', 'excel')
    
    # Obtener empleados con los mismos filtros de la lista
    view = EmpleadoListView()
    view.request = request
    empleados = view.get_queryset()
    
    if formato == 'excel':
        return export_empleados_excel(empleados)
    elif formato == 'pdf':
        return export_empleados_pdf(empleados)
    
    return redirect('employees:empleado_list')


def export_empleados_excel(empleados):
    """Exportar empleados a Excel"""
    import openpyxl
    from django.http import HttpResponse
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Empleados'
    
    # Encabezados
    headers = [
        'Documento', 'Nombres', 'Apellidos', 'Email', 'Teléfono',
        'Cargo', 'Área', 'Sede', 'Fecha Ingreso', 'Estado'
    ]
    
    for col, header in enumerate(headers, 1):
        worksheet.cell(row=1, column=col, value=header)
    
    # Datos
    for row, empleado in enumerate(empleados, 2):
        cargo_actual = empleado.historialcargo_set.filter(activo=True).first()
        
        worksheet.cell(row=row, column=1, value=empleado.numero_documento)
        worksheet.cell(row=row, column=2, value=empleado.nombres)
        worksheet.cell(row=row, column=3, value=empleado.apellidos)
        worksheet.cell(row=row, column=4, value=empleado.correo_electronico)
        worksheet.cell(row=row, column=5, value=empleado.telefono_contacto)
        worksheet.cell(row=row, column=6, value=cargo_actual.cargo.nombre if cargo_actual else '')
        worksheet.cell(row=row, column=7, value=cargo_actual.cargo.area.nombre if cargo_actual else '')
        worksheet.cell(row=row, column=8, value=empleado.sede.nombre)
        worksheet.cell(row=row, column=9, value=empleado.fecha_ingreso.strftime('%d/%m/%Y'))
        worksheet.cell(row=row, column=10, value=empleado.estado.nombre)
    
    # Preparar respuesta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="empleados.xlsx"'
    
    workbook.save(response)
    return response


def export_empleados_pdf(empleados):
    """Exportar empleados a PDF"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="empleados.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, "Lista de Empleados")
    
    # Contenido básico (mejorar con reportlab más avanzado)
    y = 750
    p.setFont("Helvetica", 10)
    
    for empleado in empleados[:50]:  # Limitar para ejemplo
        if y < 50:
            p.showPage()
            y = 800
        
        cargo_actual = empleado.historialcargo_set.filter(activo=True).first()
        cargo_texto = cargo_actual.cargo.nombre if cargo_actual else 'Sin cargo'
        
        texto = f"{empleado.nombre_completo} - {empleado.numero_documento} - {cargo_texto}"
        p.drawString(50, y, texto)
        y -= 20
    
    p.showPage()
    p.save()
    
    return response