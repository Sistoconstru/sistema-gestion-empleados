from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Avg, Count, Q, F, Case, When, IntegerField
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta, datetime

# Importar modelos que ya funcionan
from apps.employees.models import Empleado
from apps.training.models import Capacitacion
from apps.evaluations.models import AsignacionEvaluacion, PlanMejoraPredefinido, SeguimientoBimensual

# Importar bibliotecas para exportación
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """Dashboard de reportes con datos reales"""
    template_name = 'reports/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Datos reales de módulos que funcionan
        context.update({
            'total_empleados': Empleado.objects.count(),
            'capacitaciones_activas': Capacitacion.objects.filter(activa=True).count(),
            'evaluaciones_pendientes': AsignacionEvaluacion.objects.filter(estado='pendiente').count(),

            # Placeholders para módulos no implementados
            'satisfaccion_general': 0.0,  # Pendiente: módulo surveys
            'reconocimientos_mes': 0,     # Pendiente: módulo recognition
        })

        return context


@method_decorator(login_required, name='dispatch')
class PerformanceReportView(TemplateView):
    """Reporte específico de evaluaciones de desempeño"""
    template_name = 'reports/evaluations_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ============ 1. KPIs PRINCIPALES ============

        # Total de empleados activos (con estado que permite acceso al sistema)
        total_empleados = Empleado.objects.filter(estado__permite_acceso_sistema=True).count()

        # Evaluaciones completadas (con puntaje calculado)
        # IMPORTANTE: Solo evaluaciones de DESEMPEÑO ANUAL (escala 1-5, puntaje en porcentaje)
        # Excluimos evaluaciones de PERÍODO DE PRUEBA (escala 1-3, puntaje 1-21)
        evaluaciones_completadas = AsignacionEvaluacion.objects.filter(
            estado='completada',
            puntaje_total__isnull=False,
            evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_'  # Solo evaluaciones anuales
        )

        # Promedio General de Desempeño (basado en porcentaje de evaluación)
        promedio_desempeño = evaluaciones_completadas.aggregate(
            promedio=Avg('puntaje_total')
        )['promedio'] or 0

        # Tasa de Evaluaciones Completas (completadas vs total)
        total_evaluaciones = AsignacionEvaluacion.objects.count()
        tasa_completadas = (evaluaciones_completadas.count() / total_evaluaciones * 100) if total_evaluaciones > 0 else 0

        # ============ 2. DISTRIBUCIÓN DE NIVELES ============

        # Clasificar evaluaciones por nivel según puntaje
        distribucion_niveles = {
            'muy_alto': evaluaciones_completadas.filter(puntaje_total__gte=90).count(),
            'alto': evaluaciones_completadas.filter(puntaje_total__gte=75, puntaje_total__lt=90).count(),
            'moderado': evaluaciones_completadas.filter(puntaje_total__gte=60, puntaje_total__lt=75).count(),
            'bajo': evaluaciones_completadas.filter(puntaje_total__gte=40, puntaje_total__lt=60).count(),
            'muy_bajo': evaluaciones_completadas.filter(puntaje_total__lt=40).count(),
        }

        # ============ 3. ALERTAS CRÍTICAS ============

        # Empleados con desempeño bajo (menos de 60 puntos)
        empleados_bajo_desempeño = AsignacionEvaluacion.objects.filter(
            estado='completada',
            puntaje_total__lt=60
        ).select_related('empleado_evaluado').order_by('puntaje_total')[:10]

        # Evaluaciones vencidas
        evaluaciones_vencidas = AsignacionEvaluacion.objects.filter(
            estado__in=['pendiente', 'en_progreso'],
            fecha_vencimiento__lt=timezone.now().date()
        ).select_related('empleado_evaluado').order_by('fecha_vencimiento')[:10]

        # Seguimientos atrasados
        seguimientos_atrasados = SeguimientoBimensual.objects.filter(
            estado='atrasado'
        ).select_related('plan_mejora__asignacion_evaluacion__empleado_evaluado').order_by('fecha_limite')[:10]

        # ============ 4. ANÁLISIS POR CARGO ============

        # Obtener evaluaciones con cargo del empleado
        from apps.organizational.models import Cargo, AreaEmpresa

        analisis_por_cargo = []
        cargos = Cargo.objects.all()

        for cargo in cargos:
            # Obtener IDs de empleados con este cargo activo
            empleados_ids = list(Empleado.objects.filter(
                historialcargo__cargo_id=cargo.id,
                historialcargo__activo=True
            ).values_list('id', flat=True).distinct())

            if not empleados_ids:
                continue

            # Evaluaciones de estos empleados
            evals_cargo = evaluaciones_completadas.filter(
                empleado_evaluado_id__in=empleados_ids
            )

            if evals_cargo.exists():
                promedio = evals_cargo.aggregate(promedio=Avg('puntaje_total'))['promedio']
                cantidad = evals_cargo.count()

                analisis_por_cargo.append({
                    'cargo': cargo,
                    'promedio': round(promedio, 2) if promedio else 0,
                    'cantidad_evaluados': cantidad,
                })

        # Ordenar por promedio (mejor → peor)
        analisis_por_cargo = sorted(analisis_por_cargo, key=lambda x: x['promedio'], reverse=True)

        # ============ 5. ANÁLISIS POR ÁREA ============

        analisis_por_area = []
        areas = AreaEmpresa.objects.all()

        for area in areas:
            # Obtener IDs de cargos del área
            cargos_ids = list(Cargo.objects.filter(area_id=area.id).values_list('id', flat=True))

            if not cargos_ids:
                continue

            # IDs de empleados con cargos de esta área
            empleados_ids = list(Empleado.objects.filter(
                historialcargo__cargo_id__in=cargos_ids,
                historialcargo__activo=True
            ).values_list('id', flat=True).distinct())

            if not empleados_ids:
                continue

            # Evaluaciones de estos empleados
            evals_area = evaluaciones_completadas.filter(
                empleado_evaluado_id__in=empleados_ids
            )

            if evals_area.exists():
                promedio = evals_area.aggregate(promedio=Avg('puntaje_total'))['promedio']
                cantidad = evals_area.count()

                analisis_por_area.append({
                    'area': area,
                    'promedio': round(promedio, 2) if promedio else 0,
                    'cantidad_evaluados': cantidad,
                })

        # Ordenar por promedio
        analisis_por_area = sorted(analisis_por_area, key=lambda x: x['promedio'], reverse=True)

        # ============ 6. ANÁLISIS POR SEDE ============

        from apps.organizational.models import Sede

        analisis_por_sede = []
        sedes = Sede.objects.filter(activa=True)

        for sede in sedes:
            # Obtener IDs de empleados de esta sede
            empleados_ids = list(Empleado.objects.filter(
                sede_id=sede.id,
                estado__permite_acceso_sistema=True
            ).values_list('id', flat=True).distinct())

            if not empleados_ids:
                continue

            # Evaluaciones de estos empleados
            evals_sede = evaluaciones_completadas.filter(
                empleado_evaluado_id__in=empleados_ids
            )

            if evals_sede.exists():
                promedio = evals_sede.aggregate(promedio=Avg('puntaje_total'))['promedio']
                cantidad = evals_sede.count()

                analisis_por_sede.append({
                    'sede': sede,
                    'promedio': round(promedio, 2) if promedio else 0,
                    'cantidad_evaluados': cantidad,
                })

        # Ordenar por promedio
        analisis_por_sede = sorted(analisis_por_sede, key=lambda x: x['promedio'], reverse=True)

        # ============ 7. ANÁLISIS DE PLANES DE MEJORA ============

        total_planes = PlanMejoraPredefinido.objects.count()
        planes_por_estado = {
            'pendiente_aprobacion': PlanMejoraPredefinido.objects.filter(estado='pendiente_aprobacion').count(),
            'aprobado': PlanMejoraPredefinido.objects.filter(estado='aprobado').count(),
            'en_seguimiento': PlanMejoraPredefinido.objects.filter(estado='en_seguimiento').count(),
            'completado': PlanMejoraPredefinido.objects.filter(estado='completado').count(),
            'rechazado': PlanMejoraPredefinido.objects.filter(estado='rechazado').count(),
        }

        # Tasa de aceptación de empleados
        planes_aceptados = PlanMejoraPredefinido.objects.filter(aceptado_por_empleado=True).count()
        tasa_aceptacion = (planes_aceptados / total_planes * 100) if total_planes > 0 else 0

        # ============ AGREGAR TODO AL CONTEXT ============

        context.update({
            # KPIs
            'total_empleados': total_empleados,
            'promedio_desempeño': round(promedio_desempeño, 2),
            'tasa_completadas': round(tasa_completadas, 2),
            'total_evaluaciones': total_evaluaciones,
            'evaluaciones_completadas_count': evaluaciones_completadas.count(),

            # Distribución
            'distribucion_niveles': distribucion_niveles,

            # Alertas
            'empleados_bajo_desempeño': empleados_bajo_desempeño,
            'evaluaciones_vencidas': evaluaciones_vencidas,
            'seguimientos_atrasados': seguimientos_atrasados,

            # Análisis
            'analisis_por_cargo': analisis_por_cargo,
            'analisis_por_area': analisis_por_area,
            'analisis_por_sede': analisis_por_sede,

            # Planes
            'total_planes': total_planes,
            'planes_por_estado': planes_por_estado,
            'tasa_aceptacion': round(tasa_aceptacion, 2),
        })

        return context


# =============================================================================
# VISTAS DE EXPORTACIÓN
# =============================================================================

@method_decorator(login_required, name='dispatch')
class ExportEvaluationsExcelView(View):
    """Exportar reporte de evaluaciones a Excel"""

    def get(self, request, *args, **kwargs):
        # Crear workbook
        wb = Workbook()

        # Obtener datos (reutilizamos la misma lógica)
        total_empleados = Empleado.objects.filter(estado__permite_acceso_sistema=True).count()

        # Solo evaluaciones de DESEMPEÑO ANUAL (puntaje en porcentaje 0-100)
        evaluaciones_completadas = AsignacionEvaluacion.objects.filter(
            estado='completada',
            puntaje_total__isnull=False,
            evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_'
        )

        promedio_desempeño = evaluaciones_completadas.aggregate(
            promedio=Avg('puntaje_total')
        )['promedio'] or 0

        total_evaluaciones = AsignacionEvaluacion.objects.filter(
            evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_'
        ).count()
        tasa_completadas = (evaluaciones_completadas.count() / total_evaluaciones * 100) if total_evaluaciones > 0 else 0

        # Análisis por cargo
        from apps.organizational.models import Cargo, AreaEmpresa

        analisis_por_cargo = []
        cargos = Cargo.objects.all()

        for cargo in cargos:
            empleados_ids = list(Empleado.objects.filter(
                historialcargo__cargo_id=cargo.id,
                historialcargo__activo=True
            ).values_list('id', flat=True).distinct())

            if not empleados_ids:
                continue

            evals_cargo = evaluaciones_completadas.filter(
                empleado_evaluado_id__in=empleados_ids
            )

            if evals_cargo.exists():
                promedio = evals_cargo.aggregate(promedio=Avg('puntaje_total'))['promedio']
                cantidad = evals_cargo.count()

                analisis_por_cargo.append({
                    'cargo': cargo,
                    'promedio': round(promedio, 2) if promedio else 0,
                    'cantidad_evaluados': cantidad,
                })

        analisis_por_cargo = sorted(analisis_por_cargo, key=lambda x: x['promedio'], reverse=True)

        # Análisis por área
        analisis_por_area = []
        areas = AreaEmpresa.objects.all()

        for area in areas:
            cargos_ids = list(Cargo.objects.filter(area_id=area.id).values_list('id', flat=True))

            if not cargos_ids:
                continue

            empleados_ids = list(Empleado.objects.filter(
                historialcargo__cargo_id__in=cargos_ids,
                historialcargo__activo=True
            ).values_list('id', flat=True).distinct())

            if not empleados_ids:
                continue

            evals_area = evaluaciones_completadas.filter(
                empleado_evaluado_id__in=empleados_ids
            )

            if evals_area.exists():
                promedio = evals_area.aggregate(promedio=Avg('puntaje_total'))['promedio']
                cantidad = evals_area.count()

                analisis_por_area.append({
                    'area': area,
                    'promedio': round(promedio, 2) if promedio else 0,
                    'cantidad_evaluados': cantidad,
                })

        analisis_por_area = sorted(analisis_por_area, key=lambda x: x['promedio'], reverse=True)

        # ===== HOJA 1: RESUMEN EJECUTIVO =====
        ws1 = wb.active
        ws1.title = "Resumen Ejecutivo"

        # Estilos
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=12)
        title_font = Font(bold=True, size=14, color="1F4E78")

        # Título
        ws1['A1'] = 'REPORTE DE EVALUACIONES DE DESEMPEÑO'
        ws1['A1'].font = Font(bold=True, size=16, color="1F4E78")
        ws1.merge_cells('A1:D1')

        ws1['A2'] = f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'
        ws1.merge_cells('A2:D2')

        # KPIs
        row = 4
        ws1[f'A{row}'] = 'INDICADORES CLAVE'
        ws1[f'A{row}'].font = title_font
        row += 1

        kpis = [
            ('Promedio General de Desempeño', f'{round(promedio_desempeño, 2)} / 100'),
            ('Tasa de Completación', f'{round(tasa_completadas, 2)}%'),
            ('Total Empleados Activos', total_empleados),
            ('Evaluaciones Completadas', f'{evaluaciones_completadas.count()} de {total_evaluaciones}'),
        ]

        for indicador, valor in kpis:
            ws1[f'A{row}'] = indicador
            ws1[f'B{row}'] = valor
            ws1[f'A{row}'].font = Font(bold=True)
            row += 1

        # ===== HOJA 2: ANÁLISIS POR CARGO =====
        ws2 = wb.create_sheet("Análisis por Cargo")

        # Headers
        headers = ['Ranking', 'Cargo', 'Área', 'Promedio', 'Cantidad Evaluados', 'Nivel']
        ws2.append(headers)

        for col_num, header in enumerate(headers, 1):
            cell = ws2.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Datos
        for idx, item in enumerate(analisis_por_cargo, 1):
            nivel = ''
            if item['promedio'] >= 90:
                nivel = 'Muy Alto'
            elif item['promedio'] >= 75:
                nivel = 'Alto'
            elif item['promedio'] >= 60:
                nivel = 'Moderado'
            elif item['promedio'] >= 40:
                nivel = 'Bajo'
            else:
                nivel = 'Muy Bajo'

            ws2.append([
                idx,
                item['cargo'].nombre,
                item['cargo'].area.nombre,
                item['promedio'],
                item['cantidad_evaluados'],
                nivel
            ])

        # Ajustar anchos de columna
        for col in range(1, 7):
            ws2.column_dimensions[get_column_letter(col)].width = 20

        # ===== HOJA 3: ANÁLISIS POR ÁREA =====
        ws3 = wb.create_sheet("Análisis por Área")

        # Headers
        headers = ['Área', 'Promedio', 'Cantidad Evaluados', 'Nivel']
        ws3.append(headers)

        for col_num, header in enumerate(headers, 1):
            cell = ws3.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Datos
        for item in analisis_por_area:
            nivel = ''
            if item['promedio'] >= 90:
                nivel = 'Muy Alto'
            elif item['promedio'] >= 75:
                nivel = 'Alto'
            elif item['promedio'] >= 60:
                nivel = 'Moderado'
            elif item['promedio'] >= 40:
                nivel = 'Bajo'
            else:
                nivel = 'Muy Bajo'

            ws3.append([
                item['area'].nombre,
                item['promedio'],
                item['cantidad_evaluados'],
                nivel
            ])

        # Ajustar anchos
        for col in range(1, 5):
            ws3.column_dimensions[get_column_letter(col)].width = 25

        # ===== HOJA 4: ANÁLISIS POR SEDE =====

        # Calcular análisis por sede para Excel (reutilizando lógica)
        from apps.organizational.models import Sede

        analisis_por_sede_excel = []
        sedes = Sede.objects.filter(activa=True)

        for sede in sedes:
            empleados_ids = list(Empleado.objects.filter(
                sede_id=sede.id,
                estado__permite_acceso_sistema=True
            ).values_list('id', flat=True).distinct())

            if not empleados_ids:
                continue

            evals_sede = evaluaciones_completadas.filter(
                empleado_evaluado_id__in=empleados_ids
            )

            if evals_sede.exists():
                promedio = evals_sede.aggregate(promedio=Avg('puntaje_total'))['promedio']
                cantidad = evals_sede.count()

                analisis_por_sede_excel.append({
                    'sede': sede,
                    'promedio': round(promedio, 2) if promedio else 0,
                    'cantidad_evaluados': cantidad,
                })

        analisis_por_sede_excel = sorted(analisis_por_sede_excel, key=lambda x: x['promedio'], reverse=True)

        ws4 = wb.create_sheet("Análisis por Sede")

        # Headers
        headers = ['Sede', 'Ciudad', 'Promedio', 'Cantidad Evaluados', 'Nivel']
        ws4.append(headers)

        for col_num, header in enumerate(headers, 1):
            cell = ws4.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Datos
        for item in analisis_por_sede_excel:
            nivel = ''
            if item['promedio'] >= 90:
                nivel = 'Muy Alto'
            elif item['promedio'] >= 75:
                nivel = 'Alto'
            elif item['promedio'] >= 60:
                nivel = 'Moderado'
            elif item['promedio'] >= 40:
                nivel = 'Bajo'
            else:
                nivel = 'Muy Bajo'

            ws4.append([
                item['sede'].nombre,
                item['sede'].ciudad,
                item['promedio'],
                item['cantidad_evaluados'],
                nivel
            ])

        # Ajustar anchos
        for col in range(1, 6):
            ws4.column_dimensions[get_column_letter(col)].width = 25

        # Preparar respuesta HTTP
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=Reporte_Evaluaciones_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'

        wb.save(response)
        return response


@method_decorator(login_required, name='dispatch')
class ExportEvaluationsPDFView(View):
    """Exportar reporte de evaluaciones a PDF"""

    def get(self, request, *args, **kwargs):
        # Crear respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=Reporte_Evaluaciones_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'

        # Crear documento PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        elementos = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1F4E78'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1F4E78'),
            spaceAfter=12,
        )

        # Título
        elementos.append(Paragraph('REPORTE DE EVALUACIONES DE DESEMPEÑO', title_style))
        elementos.append(Paragraph(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
        elementos.append(Spacer(1, 20))

        # Obtener datos
        total_empleados = Empleado.objects.filter(estado__permite_acceso_sistema=True).count()

        # Solo evaluaciones de DESEMPEÑO ANUAL (puntaje en porcentaje 0-100)
        evaluaciones_completadas = AsignacionEvaluacion.objects.filter(
            estado='completada',
            puntaje_total__isnull=False,
            evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_'
        )

        promedio_desempeño = evaluaciones_completadas.aggregate(
            promedio=Avg('puntaje_total')
        )['promedio'] or 0

        total_evaluaciones = AsignacionEvaluacion.objects.filter(
            evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_'
        ).count()
        tasa_completadas = (evaluaciones_completadas.count() / total_evaluaciones * 100) if total_evaluaciones > 0 else 0

        # KPIs
        elementos.append(Paragraph('INDICADORES CLAVE', heading_style))

        kpi_data = [
            ['Indicador', 'Valor'],
            ['Promedio General de Desempeño', f'{round(promedio_desempeño, 2)} / 100'],
            ['Tasa de Completación', f'{round(tasa_completadas, 2)}%'],
            ['Total Empleados Activos', str(total_empleados)],
            ['Evaluaciones Completadas', f'{evaluaciones_completadas.count()} de {total_evaluaciones}'],
        ]

        kpi_table = Table(kpi_data, colWidths=[4*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elementos.append(kpi_table)
        elementos.append(Spacer(1, 20))

        # Análisis por cargo
        from apps.organizational.models import Cargo, AreaEmpresa

        analisis_por_cargo = []
        cargos = Cargo.objects.all()

        for cargo in cargos:
            empleados_ids = list(Empleado.objects.filter(
                historialcargo__cargo_id=cargo.id,
                historialcargo__activo=True
            ).values_list('id', flat=True).distinct())

            if not empleados_ids:
                continue

            evals_cargo = evaluaciones_completadas.filter(
                empleado_evaluado_id__in=empleados_ids
            )

            if evals_cargo.exists():
                promedio = evals_cargo.aggregate(promedio=Avg('puntaje_total'))['promedio']
                cantidad = evals_cargo.count()

                analisis_por_cargo.append({
                    'cargo': cargo,
                    'promedio': round(promedio, 2) if promedio else 0,
                    'cantidad_evaluados': cantidad,
                })

        analisis_por_cargo = sorted(analisis_por_cargo, key=lambda x: x['promedio'], reverse=True)

        if analisis_por_cargo:
            elementos.append(PageBreak())
            elementos.append(Paragraph('ANÁLISIS POR CARGO (Top 10)', heading_style))

            cargo_data = [['Ranking', 'Cargo', 'Promedio', 'Evaluados']]

            for idx, item in enumerate(analisis_por_cargo[:10], 1):
                cargo_data.append([
                    str(idx),
                    item['cargo'].nombre,
                    str(item['promedio']),
                    str(item['cantidad_evaluados'])
                ])

            cargo_table = Table(cargo_data, colWidths=[0.8*inch, 3*inch, 1.2*inch, 1*inch])
            cargo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elementos.append(cargo_table)

        # Análisis por sede
        from apps.organizational.models import Sede

        analisis_por_sede_pdf = []
        sedes = Sede.objects.filter(activa=True)

        for sede in sedes:
            empleados_ids = list(Empleado.objects.filter(
                sede_id=sede.id,
                estado__permite_acceso_sistema=True
            ).values_list('id', flat=True).distinct())

            if not empleados_ids:
                continue

            evals_sede = evaluaciones_completadas.filter(
                empleado_evaluado_id__in=empleados_ids
            )

            if evals_sede.exists():
                promedio = evals_sede.aggregate(promedio=Avg('puntaje_total'))['promedio']
                cantidad = evals_sede.count()

                analisis_por_sede_pdf.append({
                    'sede': sede,
                    'promedio': round(promedio, 2) if promedio else 0,
                    'cantidad_evaluados': cantidad,
                })

        analisis_por_sede_pdf = sorted(analisis_por_sede_pdf, key=lambda x: x['promedio'], reverse=True)

        if analisis_por_sede_pdf:
            elementos.append(Spacer(1, 20))
            elementos.append(Paragraph('ANÁLISIS POR SEDE', heading_style))

            sede_data = [['Sede', 'Ciudad', 'Promedio', 'Evaluados']]

            for item in analisis_por_sede_pdf:
                sede_data.append([
                    item['sede'].nombre,
                    item['sede'].ciudad,
                    str(item['promedio']),
                    str(item['cantidad_evaluados'])
                ])

            sede_table = Table(sede_data, colWidths=[2*inch, 1.5*inch, 1.2*inch, 1.3*inch])
            sede_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elementos.append(sede_table)

        # Generar PDF
        doc.build(elementos)

        return response