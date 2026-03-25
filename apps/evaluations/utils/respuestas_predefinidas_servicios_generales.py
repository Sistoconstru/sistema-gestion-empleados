# =============================================================================
# apps/evaluations/utils/respuestas_predefinidas_servicios_generales.py
# Sistema de respuestas predefinidas para Servicios Generales
# =============================================================================

from datetime import datetime, timedelta
from django.utils import timezone
from .respuestas_predefinidas import formatear_comentarios_evaluador

# ===================== PONDERACIONES =====================
PONDERACION_CATEGORIAS = {
    "Competencias Organizacionales": 0.10,
    "Objetivos": 0.40,
    "Competencias Interpersonales": 0.25,
    "Competencias Técnicas": 0.25
}

# ===================== RESPUESTAS PREDEFINIDAS =====================

RESPUESTAS_SERVICIOS_GENERALES = {
    "Comunicación": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No comunica información de manera clara. No reporta novedades o daños encontrados.",
            "plan": [
                "Participar en taller de comunicación efectiva en el entorno laboral.",
                "Practicar reportar novedades e incidentes al supervisor diariamente.",
                "Solicitar retroalimentación sobre claridad en la comunicación."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Comunica pero con poca claridad. A veces olvida reportar novedades importantes.",
            "plan": [
                "Asistir a capacitación en comunicación operativa.",
                "Utilizar formato estándar para reportar novedades diarias.",
                "Verificar que el mensaje fue comprendido por el supervisor."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Comunica de manera adecuada pero puede ser más proactivo en reportar observaciones.",
            "plan": [
                "Reforzar hábito de comunicación proactiva con el equipo.",
                "Practicar escucha activa durante las instrucciones.",
                "Compartir observaciones de mejora con el supervisor."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Comunica claramente y de forma proactiva. Reporta oportunamente novedades.",
            "plan": [
                "Mantener comunicación efectiva.",
                "Apoyar a compañeros nuevos en procedimientos de reporte.",
                "Documentar mejores prácticas de comunicación."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Comunicación ejemplar. Reporta proactivamente y facilita el trabajo coordinado.",
            "plan": []
        }
    },

    "Trabajo en equipo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Trabaja de forma aislada. No coopera con otros miembros del equipo de servicios.",
            "plan": [
                "Participar en actividades de integración del equipo.",
                "Colaborar activamente en tareas compartidas de limpieza.",
                "Solicitar apoyo y ofrecer ayuda cuando sea necesario."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Coopera cuando se le solicita pero no toma iniciativa para apoyar.",
            "plan": [
                "Desarrollar actitud proactiva de colaboración.",
                "Participar activamente en coordinación de tareas.",
                "Ofrecer apoyo sin esperar que se lo soliciten."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Trabaja bien en equipo. Coopera y apoya cuando es necesario.",
            "plan": [
                "Fortalecer colaboración en tareas conjuntas.",
                "Proponer mejoras que beneficien al grupo.",
                "Compartir conocimientos con compañeros nuevos."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente colaborador. Fortalece el desempeño del equipo de servicios.",
            "plan": [
                "Mantener actitud colaborativa.",
                "Apoyar en la inducción de personal nuevo.",
                "Liderar iniciativas de mejora grupal."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Referente en trabajo en equipo. Genera ambiente de cooperación excepcional.",
            "plan": []
        }
    },

    "Mejora continua": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No muestra interés en mejorar procesos. Rechaza cambios en métodos de trabajo.",
            "plan": [
                "Capacitarse en fundamentos de mejora continua.",
                "Observar y documentar oportunidades de mejora en limpieza.",
                "Proponer al menos una mejora mensual al supervisor."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Acepta cambios pero no propone mejoras proactivamente.",
            "plan": [
                "Identificar ineficiencias en procesos de limpieza.",
                "Participar en sesiones de mejora del área.",
                "Implementar al menos una sugerencia de mejora trimestral."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Propone mejoras ocasionales y se adapta a cambios de metodología.",
            "plan": [
                "Aumentar frecuencia de propuestas de mejora.",
                "Liderar implementación de una mejora en su área.",
                "Documentar resultados de mejoras implementadas."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Proactivo en mejora continua. Implementa cambios efectivos en procesos.",
            "plan": [
                "Compartir metodología de mejora con compañeros.",
                "Liderar proyecto de optimización en servicios generales.",
                "Capacitarse en técnicas avanzadas de limpieza."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Líder en mejora continua. Sus propuestas generan impacto significativo.",
            "plan": []
        }
    },

    "Mantener en óptimas condiciones de limpieza": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Las áreas asignadas no se mantienen limpias. Incumple estándares básicos de orden e higiene.",
            "plan": [
                "Revisar y reforzar protocolo de limpieza por área.",
                "Establecer checklist diario de tareas de limpieza.",
                "Recibir supervisión directa durante 2 semanas."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Limpia áreas básicas pero descuida detalles importantes. Orden e higiene inconsistentes.",
            "plan": [
                "Capacitarse en estándares de limpieza empresarial.",
                "Implementar rutina de verificación por áreas.",
                "Solicitar retroalimentación semanal del supervisor."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Mantiene áreas limpias y ordenadas. Puede mejorar en anticipar necesidades de limpieza profunda.",
            "plan": [
                "Implementar calendario de limpieza profunda.",
                "Mejorar atención a detalles en zonas de alto tráfico.",
                "Participar en capacitación de técnicas avanzadas de limpieza."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Mantiene excelentes condiciones de limpieza e higiene. Anticipa necesidades.",
            "plan": [
                "Mantener estándares de calidad.",
                "Compartir mejores prácticas con el equipo.",
                "Apoyar en supervisión de áreas críticas."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Estándares excepcionales de limpieza e higiene. Referente del área.",
            "plan": []
        }
    },

    "Responsabilidad y puntualidad": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Llega tarde frecuentemente. No inicia su jornada a la hora establecida.",
            "plan": [
                "Revisar y comprometerse con horarios de entrada.",
                "Implementar sistema de registro puntual de asistencia.",
                "Reunión mensual para seguimiento de puntualidad."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Ocasionalmente llega tarde. A veces no reporta novedades importantes.",
            "plan": [
                "Reforzar compromiso con puntualidad.",
                "Mejorar hábito de reporte de novedades al jefe inmediato.",
                "Establecer rutina matinal de verificación de áreas."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Es puntual y cumple con sus horarios. Reporta novedades encontradas.",
            "plan": [
                "Mantener puntualidad constante.",
                "Mejorar detalle en reportes de novedades.",
                "Documentar daños encontrados con fotografías."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Muy puntual y responsable. Reporta proactivamente cualquier novedad.",
            "plan": [
                "Mantener nivel de responsabilidad.",
                "Apoyar en supervisión de cumplimiento horario del equipo.",
                "Compartir mejores prácticas de organización."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Ejemplar en puntualidad y responsabilidad. Referente del equipo.",
            "plan": []
        }
    },

    "Dinamismo y energía": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Muestra resistencia ante solicitudes urgentes. Baja disposición para cambiar de actividad.",
            "plan": [
                "Reforzar actitud de servicio y flexibilidad.",
                "Practicar respuesta rápida a solicitudes urgentes.",
                "Participar en taller de gestión de cambio y adaptabilidad."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Atiende solicitudes urgentes pero con demora. Muestra resistencia ocasional al cambio.",
            "plan": [
                "Mejorar tiempo de respuesta ante solicitudes urgentes.",
                "Desarrollar actitud positiva ante cambios de actividad.",
                "Establecer protocolo de priorización de tareas."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Atiende solicitudes con disposición. Se adapta bien a cambios de actividad.",
            "plan": [
                "Mejorar rapidez en respuesta a solicitudes.",
                "Anticipar necesidades de limpieza urgente.",
                "Fortalecer flexibilidad ante imprevistos."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Atiende rápidamente solicitudes urgentes. Excelente disposición al cambio.",
            "plan": [
                "Mantener actitud proactiva.",
                "Apoyar en capacitación de nuevos empleados.",
                "Liderar respuesta ante emergencias de limpieza."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Disposición excepcional. Responde inmediatamente con energía y entusiasmo.",
            "plan": []
        }
    },

    "Orientación al servicio": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No anticipa necesidades. Áreas críticas como comedores y baños no se mantienen presentables.",
            "plan": [
                "Capacitarse en estándares de presentación de áreas comunes.",
                "Implementar rutina de verificación de zonas de alto tráfico.",
                "Recibir supervisión directa en áreas críticas."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Atiende necesidades cuando se le solicita. Falta anticipación en zonas críticas.",
            "plan": [
                "Desarrollar capacidad de anticipación de necesidades.",
                "Aumentar frecuencia de revisión de comedores y baños.",
                "Establecer checklist de verificación por horario."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Mantiene áreas presentables. Anticipa algunas necesidades de limpieza.",
            "plan": [
                "Mejorar capacidad de anticipación en horas pico.",
                "Aumentar frecuencia de revisión proactiva.",
                "Documentar patrones de uso de áreas comunes."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Anticipa necesidades efectivamente. Áreas críticas siempre presentables.",
            "plan": [
                "Mantener nivel de servicio.",
                "Compartir técnicas de anticipación con el equipo.",
                "Apoyar en definición de estándares del área."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Orientación al servicio excepcional. Referente en atención proactiva.",
            "plan": []
        }
    },

    "Técnicas de limpieza y desinfección": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No aplica correctamente métodos de limpieza. Desconoce técnicas de desinfección.",
            "plan": [
                "Capacitarse en técnicas básicas de limpieza y desinfección.",
                "Practicar métodos correctos bajo supervisión.",
                "Estudiar protocolos específicos por tipo de superficie."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Conoce técnicas básicas pero no las aplica consistentemente.",
            "plan": [
                "Reforzar aplicación de protocolos de limpieza.",
                "Participar en talleres de técnicas de desinfección.",
                "Solicitar retroalimentación sobre métodos aplicados."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Aplica correctamente técnicas básicas. Puede mejorar en métodos avanzados.",
            "plan": [
                "Capacitarse en técnicas avanzadas de limpieza.",
                "Aprender protocolos de desinfección especializada.",
                "Implementar mejores prácticas por tipo de área."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Domina técnicas avanzadas. Aplica métodos apropiados según superficie.",
            "plan": [
                "Mantener estándares técnicos.",
                "Compartir conocimientos con el equipo.",
                "Apoyar en capacitación de personal nuevo."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Experto en técnicas de limpieza y desinfección. Referente técnico.",
            "plan": []
        }
    },

    "Manejo adecuado de productos químicos": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No conoce fichas de seguridad. Manejo inadecuado que pone en riesgo la seguridad.",
            "plan": [
                "Capacitación obligatoria en manejo seguro de químicos.",
                "Estudiar fichas de seguridad de productos utilizados.",
                "Supervisión directa durante uso de químicos por 1 mes."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Conoce diluciones básicas pero comete errores. Almacenamiento incorrecto ocasional.",
            "plan": [
                "Reforzar conocimiento de diluciones correctas.",
                "Capacitarse en almacenamiento seguro de químicos.",
                "Implementar checklist de verificación de diluciones."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Maneja correctamente diluciones y almacenamiento. Puede mejorar en prevención de riesgos.",
            "plan": [
                "Capacitarse en prevención de riesgos químicos.",
                "Mejorar conocimiento de fichas de seguridad.",
                "Participar en simulacros de emergencias químicas."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Manejo experto de químicos. Conoce fichas de seguridad y aplica protocolos.",
            "plan": [
                "Mantener estándares de seguridad.",
                "Apoyar en capacitación del equipo.",
                "Participar en auditorías de seguridad química."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Referente en manejo seguro de productos químicos. Experto en seguridad.",
            "plan": []
        }
    },

    "Gestión y control de insumos de aseo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No registra consumo. Frecuente desperdicio de materiales. No solicita reposición.",
            "plan": [
                "Capacitarse en control de inventario de insumos.",
                "Implementar registro diario de consumo.",
                "Establecer procedimiento de solicitud de reposición."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Registra consumo irregularmente. Solicita reposición tarde causando desabastecimiento.",
            "plan": [
                "Mejorar frecuencia de registro de consumo.",
                "Anticipar solicitudes de reposición.",
                "Capacitarse en gestión de inventarios básica."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Registra consumo y solicita reposición oportunamente. Puede optimizar uso de materiales.",
            "plan": [
                "Implementar técnicas de optimización de insumos.",
                "Participar en capacitación de control de desperdicios.",
                "Establecer indicadores de consumo eficiente."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente gestión de insumos. Evita desperdicios y mantiene stock adecuado.",
            "plan": [
                "Mantener control eficiente.",
                "Compartir mejores prácticas con el equipo.",
                "Apoyar en optimización del presupuesto de insumos."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Gestión ejemplar de insumos. Referente en control y optimización.",
            "plan": []
        }
    },

    "Apoyo logístico y mensajería": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Entrega documentos con demora. Desorganización en distribución interna.",
            "plan": [
                "Capacitarse en procedimientos de mensajería interna.",
                "Implementar sistema de registro de entregas.",
                "Mejorar organización de documentos a distribuir."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Realiza entregas pero sin orden. Ocasionales demoras en distribución.",
            "plan": [
                "Establecer rutina organizada de distribución.",
                "Mejorar tiempo de respuesta en entregas urgentes.",
                "Implementar checklist de verificación de entregas."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Realiza entregas oportunamente. Puede mejorar en organización de rutas.",
            "plan": [
                "Optimizar rutas de distribución interna.",
                "Implementar sistema de priorización de entregas.",
                "Mejorar registro de documentos distribuidos."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente apoyo logístico. Entregas organizadas y oportunas.",
            "plan": [
                "Mantener eficiencia en entregas.",
                "Compartir técnicas de organización con el equipo.",
                "Apoyar en optimización de procesos logísticos."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Apoyo logístico excepcional. Referente en organización y puntualidad.",
            "plan": []
        }
    }
}


# ===================== FUNCIÓN DE CÁLCULO DE PUNTAJE PONDERADO =====================

def calcular_puntaje_ponderado_servicios_generales(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado para la evaluación de Servicios Generales
    teniendo en cuenta el peso de cada categoría.

    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion

    Returns:
        dict: {
            'puntaje_porcentaje': float (0-100),
            'puntaje_escala': int (1-5),
            'nivel_desempeno': str,
            'detalle_categorias': dict
        }
    """

    # Inicializar acumuladores por categoría
    suma_por_categoria = {
        "Competencias Organizacionales": 0,
        "Objetivos": 0,
        "Competencias Interpersonales": 0,
        "Competencias Técnicas": 0
    }

    conteo_por_categoria = {
        "Competencias Organizacionales": 0,
        "Objetivos": 0,
        "Competencias Interpersonales": 0,
        "Competencias Técnicas": 0
    }

    # Procesar cada respuesta
    for respuesta in respuestas_evaluacion:
        puntuacion = int(respuesta.opcion_seleccionada.valor_numerico) if respuesta.opcion_seleccionada else 0

        # Usar directamente la categoría de la pregunta (ya viene correcta desde la BD)
        categoria = respuesta.pregunta.categoria

        # Si por alguna razón no tiene categoría, usar fallback
        if not categoria:
            categoria = "Competencias Interpersonales"

        # Acumular
        if categoria in suma_por_categoria:
            suma_por_categoria[categoria] += puntuacion
            conteo_por_categoria[categoria] += 1

    # Calcular promedio por categoría y aplicar ponderación
    puntaje_total_ponderado = 0
    detalle_categorias = {}

    for categoria in suma_por_categoria.keys():
        if conteo_por_categoria[categoria] > 0:
            promedio_categoria = suma_por_categoria[categoria] / conteo_por_categoria[categoria]
            # Convertir promedio (1-5) a porcentaje (20-100): (promedio/5)*100
            porcentaje_categoria = (promedio_categoria / 5) * 100
            # Aplicar ponderación
            ponderacion = PONDERACION_CATEGORIAS[categoria]
            contribucion = porcentaje_categoria * ponderacion

            puntaje_total_ponderado += contribucion

            detalle_categorias[categoria] = {
                'promedio': round(promedio_categoria, 2),
                'porcentaje': round(porcentaje_categoria, 2),
                'ponderacion': ponderacion * 100,
                'contribucion': round(contribucion, 2)
            }

    # Clasificar según tabla de criterios de cumplimiento
    if puntaje_total_ponderado >= 91:
        nivel_desempeno = 'Muy alto'
        puntaje_escala = 5
    elif puntaje_total_ponderado >= 76:
        nivel_desempeno = 'Alto'
        puntaje_escala = 4
    elif puntaje_total_ponderado >= 61:
        nivel_desempeno = 'Moderado'
        puntaje_escala = 3
    elif puntaje_total_ponderado >= 41:
        nivel_desempeno = 'Bajo'
        puntaje_escala = 2
    else:
        nivel_desempeno = 'Muy bajo'
        puntaje_escala = 1

    return {
        'puntaje_porcentaje': round(puntaje_total_ponderado, 2),
        'puntaje_escala': puntaje_escala,
        'nivel_desempeno': nivel_desempeno,
        'detalle_categorias': detalle_categorias
    }


# ===================== FUNCIÓN DE GENERACIÓN DE PLAN =====================

def generar_plan_mejora_servicios_generales(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Servicios Generales
    basado en respuestas y resultado ponderado.

    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion
        resultado_evaluacion: dict con resultado del cálculo ponderado

    Returns:
        str: Plan de mejora completo formateado
    """
    planes = []

    # Encabezado con resultado general
    plan_header = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              PLAN DE MEJORA - EVALUACIÓN ANUAL DE DESEMPEÑO                  ║
║                          SERVICIOS GENERALES                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

RESULTADO GENERAL:
  • Puntaje Total: {resultado_evaluacion['puntaje_porcentaje']}%
  • Nivel de Desempeño: {resultado_evaluacion['nivel_desempeno']} ({resultado_evaluacion['puntaje_escala']}/5)

DETALLE POR CATEGORÍAS:
"""

    for categoria, datos in resultado_evaluacion['detalle_categorias'].items():
        plan_header += f"  • {categoria} ({datos['ponderacion']}%): {datos['promedio']}/5 → {datos['porcentaje']}% → Contribución: {datos['contribucion']}%\n"

    plan_header += "\n" + "="*80 + "\n\n"
    planes.append(plan_header)

    # Generar plan detallado por TODAS las preguntas
    planes.append("EVALUACIÓN POR COMPETENCIA:\n\n")

    contador = 1

    for respuesta in respuestas_evaluacion.order_by('pregunta__orden'):
        pregunta_texto = respuesta.pregunta.pregunta or respuesta.pregunta.categoria
        puntuacion = int(respuesta.opcion_seleccionada.valor_numerico) if respuesta.opcion_seleccionada else 0

        # Buscar competencia en diccionario
        competencia_encontrada = None
        for competencia_key in RESPUESTAS_SERVICIOS_GENERALES.keys():
            if competencia_key.lower() in pregunta_texto.lower():
                competencia_encontrada = competencia_key
                break

        if not competencia_encontrada:
            # Si no se encuentra, usar el texto completo de la pregunta
            competencia_encontrada = pregunta_texto[:80]

        plan_texto = f"{contador}. {competencia_encontrada}\n"
        plan_texto += f"   Calificación: {puntuacion}/5\n"

        # Agregar comentarios del evaluador si existen
        plan_texto += formatear_comentarios_evaluador(respuesta)
        plan_texto += "\n"

        # Si puntuación es 5: Felicitar
        if puntuacion == 5:
            plan_texto += "   ✅ ¡EXCELENTE DESEMPEÑO!\n"
            plan_texto += "   El empleado ha demostrado dominio excepcional en esta competencia.\n"
            plan_texto += "   Continue con este nivel de excelencia.\n"

        # Si puntuación es 4 o menos: Plan de acción con máximo 3 items
        else:
            if competencia_encontrada in RESPUESTAS_SERVICIOS_GENERALES and puntuacion in RESPUESTAS_SERVICIOS_GENERALES[competencia_encontrada]:
                datos_plan = RESPUESTAS_SERVICIOS_GENERALES[competencia_encontrada][puntuacion]

                plan_texto += f"   📋 PLAN DE ACCIÓN:\n"

                # Tomar solo los primeros 3 items del plan
                items_plan = datos_plan['plan'][:3]

                for idx, item in enumerate(items_plan, 1):
                    plan_texto += f"   {idx}. {item}\n"

                # Marcar si requiere seguimiento bimensual (cualquier puntuación ≤ 4)
                if puntuacion <= 4:
                    plan_texto += f"\n   ⚠️  REQUIERE SEGUIMIENTO BIMENSUAL\n"
            else:
                # Mensaje genérico si no hay datos predefinidos
                plan_texto += f"   📋 PLAN DE ACCIÓN:\n"
                plan_texto += f"   1. Revisar los procedimientos y mejores prácticas relacionadas con esta competencia.\n"
                plan_texto += f"   2. Solicitar retroalimentación constante del supervisor inmediato.\n"
                plan_texto += f"   3. Establecer metas específicas para mejorar en esta área.\n"

        plan_texto += "\n" + "-"*80 + "\n\n"
        planes.append(plan_texto)
        contador += 1

    # Agregar sección de SST si aplica
    planes.append("="*80 + "\n")
    planes.append("OBSERVACIÓN DE SEGURIDAD Y SALUD EN EL TRABAJO (SST)\n")
    planes.append("="*80 + "\n\n")
    planes.append("Nota: La evaluación de uso de EPP se registra por separado y no afecta el puntaje general.\n")
    planes.append("Esta observación es fundamental para garantizar la seguridad del empleado.\n\n")

    # Footer
    planes.append("="*80 + "\n")
    planes.append("INSTRUCCIONES:\n")
    planes.append("1. Este plan debe ser revisado y aceptado por el empleado.\n")
    planes.append("2. Se realizarán 3 seguimientos bimensuales (cada 2 meses) durante 6 meses.\n")
    planes.append("3. Al finalizar el período se realizará una evaluación final del plan.\n")
    planes.append("4. Las competencias con seguimiento bimensual deben mostrar avance progresivo.\n")
    planes.append("="*80 + "\n")

    return "".join(planes)
