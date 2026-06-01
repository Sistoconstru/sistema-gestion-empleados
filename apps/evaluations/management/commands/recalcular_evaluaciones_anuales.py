"""
Comando para recalcular el puntaje de evaluaciones anuales con la fórmula corregida
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.evaluations.models import AsignacionEvaluacion, RespuestaEvaluacion, ResultadoEvaluacion
from decimal import Decimal


class Command(BaseCommand):
    help = 'Recalcula el puntaje ponderado de evaluaciones anuales completadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empleado-id',
            type=int,
            help='Recalcular solo para un empleado específico',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar cambios sin guardarlos',
        )

    def handle(self, *args, **options):
        empleado_id = options.get('empleado_id')
        dry_run = options.get('dry_run', False)

        # Obtener evaluaciones anuales completadas
        evaluaciones = AsignacionEvaluacion.objects.filter(
            evaluacion__tipo_evaluacion__codigo__in=[
                'ANUAL_DIRECTOR', 'ANUAL_ASESOR_COMER', 'ANUAL_COORD_ADMIN',
                'ANUAL_AUX_PROCESOS', 'ANUAL_MANTENIMIENTO', 'ANUAL_OPERARIOS_PROD',
                'ANUAL_COORD_PROC', 'ANUAL_AFILADORES', 'ANUAL_SERV_GRAL',
                'ANUAL_AUX_ADMIN', 'ANUAL_AUX_TESORERIA', 'ANUAL_AUX_RRHH',
                'ANUAL_AUX_CONTABLE', 'ANUAL_ANALISTA_CONT', 'ANUAL_ANALISTA_INV',
                'ANUAL_MENSAJERO', 'ANUAL_AUX_SST'
            ],
            estado='completada'
        ).select_related('empleado_evaluado', 'evaluacion__tipo_evaluacion')

        if empleado_id:
            evaluaciones = evaluaciones.filter(empleado_evaluado_id=empleado_id)

        total = evaluaciones.count()
        self.stdout.write(f"\n{'=' * 80}")
        self.stdout.write(f"Evaluaciones anuales completadas encontradas: {total}")
        self.stdout.write(f"{'=' * 80}\n")

        if total == 0:
            self.stdout.write(self.style.WARNING('No se encontraron evaluaciones para recalcular'))
            return

        actualizadas = 0
        sin_cambios = 0

        with transaction.atomic():
            for asignacion in evaluaciones:
                respuestas = RespuestaEvaluacion.objects.filter(
                    asignacion=asignacion
                ).select_related('pregunta', 'opcion_seleccionada')

                if not respuestas.exists():
                    continue

                # Debug: Mostrar preguntas
                self.stdout.write(f"\n{'-' * 80}")
                self.stdout.write(f"Empleado: {asignacion.empleado_evaluado.nombre_completo}")
                self.stdout.write(f"\nPreguntas y categorías:")
                for r in respuestas:
                    self.stdout.write(f"  P{r.pregunta.orden}: '{r.pregunta.pregunta}' - Cat: {r.pregunta.categoria}")

                tipo_evaluacion_codigo = asignacion.evaluacion.tipo_evaluacion.codigo

                # Recalcular según tipo
                if tipo_evaluacion_codigo == 'ANUAL_DIRECTOR':
                    from apps.evaluations.utils.respuestas_predefinidas_director import calcular_puntaje_ponderado_director
                    resultado_calc = calcular_puntaje_ponderado_director(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_ASESOR_COMER':
                    from apps.evaluations.utils.respuestas_predefinidas_asesor_comercial import calcular_puntaje_ponderado_asesor_comercial
                    resultado_calc = calcular_puntaje_ponderado_asesor_comercial(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_COORD_ADMIN':
                    from apps.evaluations.utils.respuestas_predefinidas_coordinador_administrativo import calcular_puntaje_ponderado_coordinador_administrativo
                    resultado_calc = calcular_puntaje_ponderado_coordinador_administrativo(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_AUX_PROCESOS':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliar_procesos import calcular_puntaje_ponderado_auxiliar_procesos
                    resultado_calc = calcular_puntaje_ponderado_auxiliar_procesos(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_MANTENIMIENTO':
                    from apps.evaluations.utils.respuestas_predefinidas_mantenimiento import calcular_puntaje_ponderado_mantenimiento
                    resultado_calc = calcular_puntaje_ponderado_mantenimiento(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_OPERARIOS_PROD':
                    from apps.evaluations.utils.respuestas_predefinidas_operarios_produccion import calcular_puntaje_ponderado_operarios_produccion
                    resultado_calc = calcular_puntaje_ponderado_operarios_produccion(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_COORD_PROC':
                    from apps.evaluations.utils.respuestas_predefinidas_coordinadores_procesos import calcular_puntaje_ponderado_coordinadores_procesos
                    resultado_calc = calcular_puntaje_ponderado_coordinadores_procesos(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_AFILADORES':
                    from apps.evaluations.utils.respuestas_predefinidas_afiladores import calcular_puntaje_ponderado_afiladores
                    resultado_calc = calcular_puntaje_ponderado_afiladores(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_SERV_GRAL':
                    from apps.evaluations.utils.respuestas_predefinidas_servicios_generales import calcular_puntaje_ponderado_servicios_generales
                    resultado_calc = calcular_puntaje_ponderado_servicios_generales(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_AUX_ADMIN':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliares_administrativos import calcular_puntaje_ponderado_auxiliares_administrativos
                    resultado_calc = calcular_puntaje_ponderado_auxiliares_administrativos(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_AUX_TESORERIA':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliar_tesoreria import calcular_puntaje_ponderado_auxiliar_tesoreria
                    resultado_calc = calcular_puntaje_ponderado_auxiliar_tesoreria(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_AUX_RRHH':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliar_rrhh import calcular_puntaje_ponderado_auxiliar_rrhh
                    resultado_calc = calcular_puntaje_ponderado_auxiliar_rrhh(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_AUX_CONTABLE':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliar_contable import calcular_puntaje_ponderado_auxiliar_contable
                    resultado_calc = calcular_puntaje_ponderado_auxiliar_contable(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_ANALISTA_CONT':
                    from apps.evaluations.utils.respuestas_predefinidas_analista_contable import calcular_puntaje_ponderado_analista_contable
                    resultado_calc = calcular_puntaje_ponderado_analista_contable(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_ANALISTA_INV':
                    from apps.evaluations.utils.respuestas_predefinidas_analista_inventario import calcular_puntaje_ponderado_analista_inventario
                    resultado_calc = calcular_puntaje_ponderado_analista_inventario(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_MENSAJERO':
                    from apps.evaluations.utils.respuestas_predefinidas_mensajero import calcular_puntaje_ponderado_mensajero
                    resultado_calc = calcular_puntaje_ponderado_mensajero(respuestas)
                elif tipo_evaluacion_codigo == 'ANUAL_AUX_SST':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliar_sst import calcular_puntaje_ponderado_auxiliar_sst
                    resultado_calc = calcular_puntaje_ponderado_auxiliar_sst(respuestas)
                else:
                    self.stdout.write(self.style.WARNING(f"Tipo no soportado: {tipo_evaluacion_codigo}"))
                    continue

                # Obtener nuevo puntaje
                nuevo_puntaje = Decimal(str(resultado_calc['puntaje_porcentaje']))
                puntaje_anterior = asignacion.puntaje_total or Decimal('0.00')

                # Mostrar información
                evaluacion = asignacion.evaluacion.nombre

                self.stdout.write(f"Evaluación: {evaluacion}")
                self.stdout.write(f"Puntaje anterior: {puntaje_anterior:.2f}%")
                self.stdout.write(f"Puntaje nuevo: {nuevo_puntaje:.2f}%")

                # Mostrar detalle por categorías
                detalle = resultado_calc.get('detalle_categorias', {})
                if detalle:
                    self.stdout.write("\nDetalle por categorías:")
                    for cat, datos in detalle.items():
                        # Manejar diferentes estructuras de datos
                        if 'promedio' in datos and 'ponderacion' in datos and 'contribucion' in datos:
                            # Estructura completa
                            self.stdout.write(
                                f"  • {cat}: promedio={datos['promedio']}/5 → "
                                f"{datos['porcentaje']:.1f}% × {datos['ponderacion']:.0f}% = "
                                f"{datos['contribucion']:.2f}% de contribución"
                            )
                        elif 'porcentaje' in datos:
                            # Estructura mínima (solo porcentaje)
                            self.stdout.write(f"  • {cat}: {datos['porcentaje']:.1f}%")
                        else:
                            # Estructura desconocida
                            self.stdout.write(f"  • {cat}: {datos}")

                # Verificar si hay diferencia
                diferencia = abs(nuevo_puntaje - puntaje_anterior)
                if diferencia >= Decimal('0.01'):
                    self.stdout.write(
                        self.style.SUCCESS(f"\n✓ Diferencia: {diferencia:.2f}%")
                    )

                    if not dry_run:
                        # Actualizar puntaje en asignación
                        asignacion.puntaje_total = nuevo_puntaje
                        asignacion.porcentaje_completado = nuevo_puntaje
                        asignacion.save()
                        self.stdout.write(self.style.SUCCESS("  → Puntaje actualizado en asignación"))

                        # Crear o actualizar ResultadoEvaluacion
                        puntaje_final = resultado_calc.get('puntaje_escala', 0)
                        nivel_desempeno = resultado_calc.get('nivel_desempeno', 'Moderado')

                        # Mapear nivel a clasificación
                        mapeo_clasificacion = {
                            'Muy alto': 'excelente',
                            'Alto': 'sobresaliente',
                            'Moderado': 'satisfactorio',
                            'Bajo': 'mejorable',
                            'Muy bajo': 'insatisfactorio'
                        }
                        clasificacion = mapeo_clasificacion.get(nivel_desempeno, 'satisfactorio')

                        # Generar aspectos según nivel
                        if nuevo_puntaje >= 91:
                            aspectos_positivos = "• Desempeño excepcional en todas las competencias evaluadas\n• Supera consistentemente las expectativas"
                            areas_mejora = "• Continuar siendo modelo de excelencia\n• Liderar programas de mejora"
                        elif nuevo_puntaje >= 76:
                            aspectos_positivos = "• Desempeño destacado en la mayoría de competencias\n• Supera las expectativas del cargo"
                            areas_mejora = "• Fortalecer competencias con calificación moderada\n• Incrementar participación en proyectos"
                        elif nuevo_puntaje >= 61:
                            aspectos_positivos = "• Cumple satisfactoriamente con las responsabilidades del cargo"
                            areas_mejora = "• Mejorar competencias con calificación baja\n• Incrementar eficiencia"
                        elif nuevo_puntaje >= 41:
                            aspectos_positivos = "• Muestra disposición para aprender y mejorar"
                            areas_mejora = "• Requiere capacitación urgente en competencias críticas"
                        else:
                            aspectos_positivos = "• Asiste a sus labores"
                            areas_mejora = "• Requiere mejora urgente en todas las competencias"

                        # Detalle por categorías
                        detalle_categorias = resultado_calc.get('detalle_categorias', {})
                        comentarios_detalle = "DESEMPEÑO POR CATEGORÍAS:\n"
                        for cat, datos in detalle_categorias.items():
                            if 'promedio' in datos and 'porcentaje' in datos:
                                comentarios_detalle += f"• {cat}: {datos.get('promedio', 0)}/5 ({datos.get('porcentaje', 0):.1f}%)\n"
                            elif 'porcentaje' in datos:
                                comentarios_detalle += f"• {cat}: {datos.get('porcentaje', 0):.1f}%\n"

                        comentarios_generales = f'Evaluación anual recalculada con {nuevo_puntaje:.1f}% de cumplimiento.\n\n{comentarios_detalle}'

                        # Determinar recomendación
                        if nuevo_puntaje >= 76:
                            recomendaciones = 'Desempeño destacado. Se recomienda considerar para promociones.'
                        elif nuevo_puntaje >= 61:
                            recomendaciones = 'Desempeño satisfactorio. El empleado continúa con seguimiento.'
                        else:
                            recomendaciones = 'Desempeño por debajo de expectativas. Requiere plan de mejora.'

                        # Obtener el usuario generador (evaluador o primer superusuario)
                        generado_por = asignacion.evaluador.usuario if asignacion.evaluador and hasattr(asignacion.evaluador, 'usuario') else None
                        if not generado_por:
                            # Si no hay evaluador, usar el primer superusuario
                            from apps.authentication.models import Usuario
                            generado_por = Usuario.objects.filter(is_superuser=True).first()

                        if not generado_por:
                            self.stdout.write(self.style.ERROR(f"  ✗ No se pudo determinar el usuario generador para {asignacion.empleado_evaluado.nombre_completo}"))
                            continue

                        # Crear o actualizar ResultadoEvaluacion
                        resultado_eval, created = ResultadoEvaluacion.objects.update_or_create(
                            asignacion=asignacion,
                            defaults={
                                'puntaje_final': Decimal(str(puntaje_final)),
                                'porcentaje_obtenido': nuevo_puntaje,
                                'nivel_desempeño': clasificacion,
                                'aspectos_positivos': aspectos_positivos,
                                'areas_mejora': areas_mejora,
                                'comentarios_generales': comentarios_generales,
                                'recomendaciones': recomendaciones,
                                'generado_por': generado_por,
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS("  → ResultadoEvaluacion creado"))
                        else:
                            self.stdout.write(self.style.SUCCESS("  → ResultadoEvaluacion actualizado"))
                    else:
                        self.stdout.write(self.style.WARNING("  → DRY RUN: No se guardó"))

                    actualizadas += 1
                else:
                    self.stdout.write(self.style.WARNING("\n→ Sin cambios significativos"))
                    sin_cambios += 1

            if dry_run:
                self.stdout.write(f"\n{'=' * 80}")
                self.stdout.write(self.style.WARNING("DRY RUN: Los cambios NO se guardaron"))
                self.stdout.write(f"{'=' * 80}\n")
                # Rollback si es dry-run
                transaction.set_rollback(True)

        # Resumen
        self.stdout.write(f"\n{'=' * 80}")
        self.stdout.write(self.style.SUCCESS(f"Evaluaciones con cambios: {actualizadas}"))
        self.stdout.write(f"Evaluaciones sin cambios: {sin_cambios}")
        self.stdout.write(f"Total procesadas: {actualizadas + sin_cambios}")
        self.stdout.write(f"{'=' * 80}\n")
