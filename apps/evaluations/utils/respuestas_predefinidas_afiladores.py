"""
Respuestas predefinidas y planes de mejora para la evaluación anual de Afiladores
Sistema de ponderación por categorías
"""

from .respuestas_predefinidas import formatear_comentarios_evaluador

# Ponderación de categorías (debe sumar 100%)
PONDERACION_CATEGORIAS = {
    'Competencias Organizacionales': 10,
    'Objetivos': 40,
    'Competencias Interpersonales': 25,
    'Competencias Técnicas': 25
}

# ============ COMPETENCIAS ORGANIZACIONALES (10%) ============

COMUNICACION_AFILADORES = {
    'competencia': 'COMUNICACIÓN',
    'descripcion': 'Capacidad para comunicar, de forma voluntaria, transmitir ideas, información y opiniones de forma clara y convincente, por escrito y oralmente, escuchando y siendo receptivo/a a las propuestas de los/as demás',
    'categoria': 'Competencias Organizacionales',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'Requiere capacitación inmediata en comunicación efectiva. Implementar reportes escritos diarios sobre el estado del herramental. Practicar comunicación asertiva con operarios sobre tiempos de entrega.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Mejorar claridad en la comunicación sobre prioridades y tiempos. Utilizar formatos estándar para reportar el estado del afilado. Desarrollar habilidades de escucha activa.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Fortalecer comunicación proactiva sobre demoras o problemas técnicos. Mejorar retroalimentación a operarios sobre cuidado del herramental.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener el buen nivel de comunicación y compartir mejores prácticas con el equipo.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Excelente desempeño. Continuar siendo referente en comunicación efectiva.'
        }
    }
}

TRABAJO_EQUIPO_AFILADORES = {
    'competencia': 'TRABAJO EN EQUIPO',
    'descripcion': 'Capacidad para establecer relaciones de participación y cooperación con otras personas, compartiendo recursos y conocimiento, armonizando intereses y contribuyendo activamente al logro de los objetivos de la organización',
    'categoria': 'Competencias Organizacionales',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'Requiere desarrollo urgente en trabajo colaborativo. Participar en reuniones de producción. Coordinar con operarios sobre necesidades de afilado. Compartir conocimientos sobre herramental.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Incrementar colaboración con operarios y mantenimiento. Compartir información sobre el estado del herramental. Apoyar en la capacitación sobre cuidado de herramientas.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Fortalecer coordinación con producción para planificar afilados. Ser más proactivo en compartir conocimientos técnicos.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener el buen nivel de colaboración y continuar apoyando al equipo de producción.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Excelente trabajo en equipo. Continuar siendo modelo de colaboración.'
        }
    }
}

MEJORA_CONTINUA_AFILADORES = {
    'competencia': 'MEJORA CONTINUA',
    'descripcion': 'Capacidad para llevar a cabo las actividades, funciones y responsabilidades inherentes al puesto de trabajo bajo estándares de calidad y buscando la mejora continua proponiendo la adaptación y modernización de los procesos y metodologías vigentes en la organización',
    'categoria': 'Competencias Organizacionales',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'Desarrollar mentalidad de mejora continua. Documentar procesos de afilado. Proponer al menos una mejora mensual en los procedimientos de afilado.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Identificar oportunidades de mejora en técnicas de afilado. Experimentar con nuevos métodos que aumenten la durabilidad del filo.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Proponer mejoras en los procedimientos de afilado. Investigar nuevas tecnologías o técnicas para optimizar el proceso.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener la actitud proactiva de mejora. Documentar y compartir las mejoras implementadas.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Excelente. Continuar liderando iniciativas de mejora continua en el área de afilado.'
        }
    }
}

# ============ OBJETIVOS (40%) ============

HERRAMENTAL_OPTIMO_AFILADORES = {
    'competencia': 'MANTENER HERRAMENTAL EN CONDICIONES ÓPTIMAS',
    'descripcion': 'Mantener el herramental de corte en condiciones óptimas de afilado y geometría, garantizando la calidad del acabado de la madera y la vida útil del equipo',
    'categoria': 'Objetivos',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'CRÍTICO: Requiere capacitación intensiva inmediata en técnicas de afilado y geometría. Supervisión constante durante 3 meses. Revisión semanal de herramental afilado. Evaluación de continuidad en el puesto.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Capacitación en técnicas avanzadas de afilado. Seguimiento semanal de la calidad del afilado. Implementar checklist de verificación de geometría. Reducir devoluciones por mala calidad.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Mejorar consistencia en la calidad del afilado. Capacitación en geometrías específicas. Reducir tiempo de afilado sin afectar calidad.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener el buen desempeño. Documentar mejores prácticas para capacitar a otros.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Desempeño excepcional. Continuar garantizando la excelencia en el afilado.'
        }
    }
}

# ============ COMPETENCIAS INTERPERSONALES (25%) ============

DINAMISMO_ENERGIA_AFILADORES = {
    'competencia': 'DINAMISMO / ENERGÍA',
    'descripcion': 'Capacidad para trabajar activamente en situaciones cambiantes y retadoras, con interlocutores diversos, en jornadas extensas de trabajo, sin que por esto se vean afectados su nivel de actividad o su juicio profesional. Comportamiento esperado: Capacidad para mantener la concentración en tareas minuciosas durante toda la jornada',
    'categoria': 'Competencias Interpersonales',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'Desarrollar resistencia y concentración. Implementar pausas estratégicas. Capacitación en ergonomía para trabajos de precisión. Evaluación médica ocupacional.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Mejorar capacidad de concentración en tareas minuciosas. Organizar mejor las cargas de trabajo. Implementar técnicas de manejo de fatiga.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Fortalecer resistencia en jornadas extensas. Mejorar organización de tareas para mantener energía constante.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener el buen nivel de energía y concentración sostenida.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Excelente manejo de energía y concentración. Continuar siendo ejemplo de constancia.'
        }
    }
}

ANALISIS_PROBLEMAS_AFILADORES = {
    'competencia': 'ANÁLISIS DE PROBLEMAS',
    'descripcion': 'Comportamiento esperado: Identifica la causa raíz de una falla mecánica recurrente y propone una solución definitiva',
    'categoria': 'Competencias Interpersonales',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'Capacitación en diagnóstico de fallas en herramental. Desarrollar habilidades de análisis de causa raíz. Trabajar con supervisor para identificar patrones de falla.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Mejorar capacidad de diagnóstico de problemas recurrentes. Documentar fallas y sus causas. Proponer soluciones preventivas.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Fortalecer análisis de causa raíz. Implementar metodología 5 porqués para identificar problemas recurrentes.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener la buena capacidad analítica. Compartir metodologías de diagnóstico con el equipo.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Excelente capacidad de análisis. Continuar siendo referente en solución de problemas.'
        }
    }
}

ATENCION_DETALLE_AFILADORES = {
    'competencia': 'ATENCIÓN AL DETALLE',
    'descripcion': 'Comportamiento esperado: Logra niveles de precisión milimétricos en el afilado',
    'categoria': 'Competencias Interpersonales',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'CRÍTICO: Capacitación intensiva en medición de precisión. Uso obligatorio de instrumentos de medición. Supervisión constante de cada trabajo. Evaluación de aptitudes para el puesto.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Capacitación en uso de instrumentos de medición de precisión. Implementar verificaciones múltiples antes de entregar herramental. Reducir errores de geometría.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Mejorar consistencia en precisión milimétrica. Utilizar lupas y herramientas de medición en cada trabajo. Reducir variabilidad.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener la excelente precisión. Documentar técnicas para mantener estándares.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Precisión excepcional. Continuar siendo referente en trabajos de alta precisión.'
        }
    }
}

# ============ COMPETENCIAS TÉCNICAS (25%) ============

CALIDAD_TRABAJO_AFILADORES = {
    'competencia': 'CALIDAD DEL TRABAJO',
    'descripcion': 'Su estándar de entrega es impecable, entendiendo que el afilado afecta directamente el consumo de energía y la calidad',
    'categoria': 'Competencias Técnicas',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'CRÍTICO: Capacitación técnica inmediata en estándares de calidad. Supervisión del 100% de trabajos. Implementar checklist de calidad obligatorio. Revisión semanal de desempeño.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Capacitación en estándares de calidad de afilado. Implementar auto-inspección antes de entregar. Reducir defectos y retrabajos. Entender impacto en consumo energético.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Mejorar consistencia en la calidad de entrega. Implementar verificaciones finales. Reducir variabilidad en los acabados.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener el alto estándar de calidad. Compartir mejores prácticas con el equipo.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Calidad impecable. Continuar siendo referente en estándares de excelencia.'
        }
    }
}

EFECTIVIDAD_ARREGLO_AFILADORES = {
    'competencia': 'EFECTIVIDAD DEL ARREGLO',
    'descripcion': 'Capacidad para realizar reparaciones técnicas que solucionan la causa raíz de las fallas, asegurando durabilidad en el tiempo, reduciendo reincidencias y contribuyendo a la estabilidad operativa de la planta',
    'categoria': 'Competencias Técnicas',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'Capacitación en reparaciones técnicas de herramental. Trabajar con personal experimentado para aprender técnicas avanzadas. Seguimiento de efectividad de reparaciones.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Mejorar técnicas de reparación para soluciones permanentes. Reducir reincidencia de fallas. Documentar procedimientos de reparación efectivos.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Fortalecer análisis de causa raíz antes de reparar. Implementar soluciones más duraderas. Reducir retrabajos.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener la efectividad en reparaciones. Documentar casos de éxito para capacitación.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Reparaciones altamente efectivas. Continuar contribuyendo a la estabilidad operativa.'
        }
    }
}

CUMPLIMIENTO_CRONOGRAMA_AFILADORES = {
    'competencia': 'CUMPLIMIENTO DE CRONOGRAMA',
    'descripcion': 'Ejecución al 100% del plan de mantenimiento preventivo y/o actividades asignadas',
    'categoria': 'Competencias Técnicas',
    'respuestas': {
        1: {
            'valor': 'Muy bajo',
            'plan_mejora': 'URGENTE: Implementar sistema de planificación y control. Revisión diaria de cumplimiento. Identificar causas de retrasos. Capacitación en gestión del tiempo.'
        },
        2: {
            'valor': 'Bajo',
            'plan_mejora': 'Mejorar planificación de actividades. Implementar checklist diario. Priorizar tareas según criticidad. Reducir atrasos en cronograma.'
        },
        3: {
            'valor': 'Moderado',
            'plan_mejora': 'Fortalecer cumplimiento de plazos. Mejorar estimación de tiempos. Comunicar anticipadamente posibles retrasos.'
        },
        4: {
            'valor': 'Alto',
            'plan_mejora': 'Mantener el buen cumplimiento de cronogramas. Continuar con la puntualidad en entregas.'
        },
        5: {
            'valor': 'Muy alto',
            'plan_mejora': 'Excelente cumplimiento. Continuar con la disciplina y ejecución al 100%.'
        }
    }
}

# ============ MAPEO DE COMPETENCIAS ============
COMPETENCIAS_AFILADORES = {
    'COMUNICACIÓN': COMUNICACION_AFILADORES,
    'TRABAJO EN EQUIPO': TRABAJO_EQUIPO_AFILADORES,
    'MEJORA CONTINUA': MEJORA_CONTINUA_AFILADORES,
    'MANTENER HERRAMENTAL EN CONDICIONES ÓPTIMAS': HERRAMENTAL_OPTIMO_AFILADORES,
    'DINAMISMO / ENERGÍA': DINAMISMO_ENERGIA_AFILADORES,
    'ANÁLISIS DE PROBLEMAS': ANALISIS_PROBLEMAS_AFILADORES,
    'ATENCIÓN AL DETALLE': ATENCION_DETALLE_AFILADORES,
    'CALIDAD DEL TRABAJO': CALIDAD_TRABAJO_AFILADORES,
    'EFECTIVIDAD DEL ARREGLO': EFECTIVIDAD_ARREGLO_AFILADORES,
    'CUMPLIMIENTO DE CRONOGRAMA': CUMPLIMIENTO_CRONOGRAMA_AFILADORES
}


def calcular_puntaje_ponderado_afiladores(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado según las categorías para Afiladores

    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion

    Returns:
        dict con puntaje_escala (1-5), puntaje_porcentaje (0-100) y nivel_desempeno
    """
    from decimal import Decimal

    # Agrupar respuestas por categoría
    puntajes_por_categoria = {}

    for respuesta in respuestas_evaluacion:
        categoria = respuesta.pregunta.categoria
        valor = float(respuesta.opcion_seleccionada.valor_numerico)

        if categoria not in puntajes_por_categoria:
            puntajes_por_categoria[categoria] = []

        puntajes_por_categoria[categoria].append(valor)

    # Calcular promedio por categoría y aplicar ponderación
    puntaje_total_ponderado = 0

    for categoria, valores in puntajes_por_categoria.items():
        promedio_categoria = sum(valores) / len(valores)
        ponderacion = PONDERACION_CATEGORIAS.get(categoria, 0)

        # Convertir escala 1-5 a porcentaje y aplicar ponderación
        porcentaje_categoria = ((promedio_categoria - 1) / 4) * 100
        contribucion = (porcentaje_categoria * ponderacion) / 100

        puntaje_total_ponderado += contribucion

    # Convertir de vuelta a escala 1-5 para consistencia
    puntaje_escala = 1 + (puntaje_total_ponderado / 100) * 4

    # Determinar nivel de desempeño según porcentaje
    if puntaje_total_ponderado >= 91:
        nivel = 'Muy alto'
    elif puntaje_total_ponderado >= 76:
        nivel = 'Alto'
    elif puntaje_total_ponderado >= 61:
        nivel = 'Moderado'
    elif puntaje_total_ponderado >= 41:
        nivel = 'Bajo'
    else:
        nivel = 'Muy bajo'

    return {
        'puntaje_escala': round(puntaje_escala, 2),
        'puntaje_porcentaje': round(puntaje_total_ponderado, 2),
        'nivel_desempeno': nivel
    }


def generar_plan_mejora_afiladores(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera un plan de mejora personalizado para Afiladores
    """
    plan_mejora = []

    # Encabezado
    plan_mejora.append("=" * 80)
    plan_mejora.append("PLAN DE MEJORA - EVALUACIÓN ANUAL AFILADORES")
    plan_mejora.append("=" * 80)
    plan_mejora.append("")
    plan_mejora.append(f"Puntaje Total: {resultado_evaluacion['puntaje_porcentaje']}%")
    plan_mejora.append(f"Nivel de Desempeño: {resultado_evaluacion['nivel_desempeno']}")
    plan_mejora.append("")

    # Identificar áreas de mejora (respuestas con valor <= 4)
    # Solo las preguntas con calificación 5 NO requieren seguimiento
    areas_mejora = []

    for respuesta in respuestas_evaluacion:
        valor = float(respuesta.opcion_seleccionada.valor_numerico)

        if valor <= 4:
            pregunta_texto = respuesta.pregunta.pregunta
            competencia_key = pregunta_texto.split(':')[0].strip()

            if competencia_key in COMPETENCIAS_AFILADORES:
                competencia_data = COMPETENCIAS_AFILADORES[competencia_key]
                plan_texto = competencia_data['respuestas'][int(valor)]['plan_mejora']

                areas_mejora.append({
                    'competencia': competencia_key,
                    'categoria': competencia_data['categoria'],
                    'valor': int(valor),
                    'valor_texto': competencia_data['respuestas'][int(valor)]['valor'],
                    'plan': plan_texto,
                    'ponderacion': PONDERACION_CATEGORIAS[competencia_data['categoria']],
                    'respuesta': respuesta  # Agregar objeto respuesta para acceder a comentarios
                })

    if areas_mejora:
        # Ordenar por ponderación (más importante primero) y luego por valor (más bajo primero)
        areas_mejora.sort(key=lambda x: (-x['ponderacion'], x['valor']))

        plan_mejora.append("ÁREAS DE MEJORA IDENTIFICADAS")
        plan_mejora.append("-" * 80)
        plan_mejora.append("")

        for i, area in enumerate(areas_mejora, 1):
            plan_mejora.append(f"{i}. {area['competencia']}")
            plan_mejora.append(f"   Categoría: {area['categoria']} (Ponderación: {area['ponderacion']}%)")
            plan_mejora.append(f"   Nivel actual: {area['valor_texto']} ({area['valor']}/5)")

            # Agregar comentarios del evaluador si existen
            comentarios = formatear_comentarios_evaluador(area['respuesta'])
            if comentarios:
                plan_mejora.append(comentarios.strip())

            plan_mejora.append(f"   Plan de acción:")
            plan_mejora.append(f"   {area['plan']}")
            plan_mejora.append(f"   ⚠️  REQUIERE SEGUIMIENTO BIMENSUAL")
            plan_mejora.append("")
    else:
        plan_mejora.append("¡EXCELENTE DESEMPEÑO!")
        plan_mejora.append("No se identificaron áreas críticas de mejora.")
        plan_mejora.append("Continuar manteniendo los altos estándares de calidad y precisión.")
        plan_mejora.append("")

    # Recomendaciones generales según el nivel
    plan_mejora.append("RECOMENDACIONES GENERALES")
    plan_mejora.append("-" * 80)

    if resultado_evaluacion['puntaje_porcentaje'] < 61:
        plan_mejora.append("• Seguimiento quincenal obligatorio con supervisor")
        plan_mejora.append("• Capacitación técnica intensiva en afilado de precisión")
        plan_mejora.append("• Revisión del 100% de trabajos antes de entregar")
        plan_mejora.append("• Evaluación de progreso en 2 meses")
    elif resultado_evaluacion['puntaje_porcentaje'] < 76:
        plan_mejora.append("• Seguimiento mensual con supervisor")
        plan_mejora.append("• Capacitación en áreas identificadas")
        plan_mejora.append("• Implementar checklist de verificación de calidad")
        plan_mejora.append("• Evaluación de progreso en 3 meses")
    elif resultado_evaluacion['puntaje_porcentaje'] < 91:
        plan_mejora.append("• Seguimiento bimestral para mantener desempeño")
        plan_mejora.append("• Continuar fortaleciendo áreas identificadas")
        plan_mejora.append("• Compartir mejores prácticas con el equipo")
    else:
        plan_mejora.append("• Continuar con el excelente desempeño")
        plan_mejora.append("• Servir como mentor para otros afiladores")
        plan_mejora.append("• Documentar mejores prácticas")

    plan_mejora.append("")
    plan_mejora.append("=" * 80)

    return "\n".join(plan_mejora)
