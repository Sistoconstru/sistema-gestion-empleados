# =============================================================================
# apps/evaluations/utils/respuestas_predefinidas_operarios_produccion.py
# Sistema de respuestas predefinidas para Operarios de Producción
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

RESPUESTAS_OPERARIOS_PRODUCCION = {
    "Comunicación": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No comunica información de manera clara. Dificulta el trabajo en equipo por falta de transmisión de ideas.",
            "plan": [
                "Participar en taller de comunicación efectiva en planta.",
                "Practicar reportar incidentes y novedades al supervisor diariamente.",
                "Solicitar retroalimentación sobre claridad en la comunicación."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Comunica pero con poca claridad. A veces genera confusiones en el equipo.",
            "plan": [
                "Asistir a capacitación en comunicación operativa.",
                "Utilizar formato estándar para reportar novedades.",
                "Verificar que el mensaje fue comprendido antes de continuar."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Comunica de manera adecuada pero puede mejorar en proactividad.",
            "plan": [
                "Reforzar hábito de comunicación proactiva con el equipo.",
                "Practicar escucha activa en reuniones de producción.",
                "Compartir mejores prácticas con compañeros."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Comunica claramente y de forma proactiva. Es referente en el equipo.",
            "plan": [
                "Mantener comunicación efectiva.",
                "Apoyar a compañeros con dificultades de comunicación.",
                "Compartir técnicas de comunicación en reuniones."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Comunicación ejemplar. Facilita el trabajo en equipo y previene errores.",
            "plan": []
        }
    },

    "Trabajo en equipo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Trabaja de forma aislada. No coopera con sus compañeros de producción.",
            "plan": [
                "Participar en actividades de integración del equipo de producción.",
                "Colaborar activamente en tareas compartidas.",
                "Solicitar apoyo y ofrecer ayuda cuando sea necesario."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Coopera cuando se le solicita pero no toma iniciativa para apoyar al equipo.",
            "plan": [
                "Desarrollar actitud proactiva de colaboración.",
                "Participar activamente en reuniones de equipo.",
                "Ofrecer apoyo sin esperar que se lo soliciten."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Trabaja bien en equipo. Coopera y apoya cuando es necesario.",
            "plan": [
                "Fortalecer liderazgo informal en el equipo.",
                "Proponer mejoras que beneficien al grupo.",
                "Mediar en conflictos menores del equipo."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente colaborador. Fortalece el desempeño del equipo.",
            "plan": [
                "Mantener actitud colaborativa.",
                "Mentorizar a operarios nuevos.",
                "Liderar iniciativas de mejora grupal."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Referente en trabajo en equipo. Genera ambiente de cooperación y alto rendimiento.",
            "plan": []
        }
    },

    "Mejora continua": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No muestra interés en mejorar procesos. Rechaza cambios y adaptaciones.",
            "plan": [
                "Capacitarse en fundamentos de mejora continua.",
                "Observar y documentar oportunidades de mejora en su puesto.",
                "Proponer al menos una mejora mensual al supervisor."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Acepta cambios pero no propone mejoras proactivamente.",
            "plan": [
                "Identificar ineficiencias en su área de trabajo.",
                "Participar en sesiones de lluvia de ideas para mejoras.",
                "Implementar al menos una sugerencia de mejora al mes."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Propone mejoras ocasionales y se adapta a cambios.",
            "plan": [
                "Aumentar frecuencia de propuestas de mejora.",
                "Liderar implementación de una mejora en su área.",
                "Documentar resultados de mejoras implementadas."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Proactivo en mejora continua. Implementa cambios efectivos.",
            "plan": [
                "Compartir metodología de mejora con compañeros.",
                "Liderar proyecto de optimización en producción.",
                "Capacitarse en herramientas avanzadas de mejora continua."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Líder en mejora continua. Sus propuestas generan impacto significativo en productividad.",
            "plan": []
        }
    },

    "Operación de equipos y máquinas": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No opera correctamente equipos y máquinas. Genera riesgos y productos defectuosos.",
            "plan": [
                "Recibir capacitación técnica urgente en operación de maquinaria.",
                "Trabajar bajo supervisión constante hasta demostrar competencia.",
                "Estudiar manuales de operación y procedimientos de seguridad."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Opera equipos con errores frecuentes. Requiere supervisión continua.",
            "plan": [
                "Reforzar capacitación en operación de maquinaria específica.",
                "Practicar procedimientos bajo supervisión.",
                "Revisar y aplicar estándares de calidad y seguridad."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Opera equipos correctamente cumpliendo estándares de calidad y seguridad.",
            "plan": [
                "Perfeccionar técnicas de operación avanzadas.",
                "Reducir tiempos de setup y configuración.",
                "Capacitarse en operación de equipos adicionales."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Operación experta. Optimiza uso de equipos y genera productos de alta calidad.",
            "plan": [
                "Capacitar a nuevos operarios en uso de equipos.",
                "Documentar mejores prácticas de operación.",
                "Proponer optimizaciones en configuración de máquinas."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Maestro en operación de equipos. Referente técnico en la planta.",
            "plan": []
        }
    },

    "Atención al detalle": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Comete errores frecuentes por falta de atención. Genera reprocesos.",
            "plan": [
                "Implementar checklist de verificación antes de cada tarea.",
                "Reducir velocidad para aumentar precisión.",
                "Solicitar retroalimentación inmediata al supervisor."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Comete errores ocasionales por descuido. Requiere supervisión frecuente.",
            "plan": [
                "Utilizar listas de verificación en tareas críticas.",
                "Implementar pausas breves para mantener concentración.",
                "Revisar trabajo antes de dar por finalizado."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Revisa tareas sistemáticamente. Errores mínimos.",
            "plan": [
                "Mantener estándar de calidad actual.",
                "Documentar buenas prácticas de verificación.",
                "Apoyar a compañeros en control de calidad."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Alto nivel de precisión. Detecta errores antes de que se conviertan en problemas.",
            "plan": [
                "Liderar inspecciones de calidad en producción.",
                "Capacitar al equipo en técnicas de atención al detalle.",
                "Proponer mejoras en controles de calidad."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Excelencia en precisión. Trabajo impecable que previene problemas de calidad.",
            "plan": []
        }
    },

    "Dinamismo y Energía": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Muestra fatiga constante. No mantiene ritmo de producción requerido.",
            "plan": [
                "Mejorar condición física para jornadas laborales.",
                "Optimizar descansos durante la jornada.",
                "Consultar con salud ocupacional sobre ergonomía."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Mantiene ritmo básico pero decae en situaciones exigentes.",
            "plan": [
                "Fortalecer resistencia física.",
                "Implementar técnicas de gestión de energía.",
                "Mantener hidratación y alimentación adecuada."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Trabaja con energía constante en jornadas completas.",
            "plan": [
                "Mantener nivel de energía actual.",
                "Apoyar en momentos de alta demanda.",
                "Promover hábitos saludables en el equipo."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Alto nivel de energía. Mantiene ritmo constante y motiva al equipo.",
            "plan": [
                "Liderar por ejemplo en gestión de energía.",
                "Apoyar a compañeros en momentos críticos.",
                "Compartir técnicas de mantenimiento de energía."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Energía excepcional. Motor del equipo en situaciones exigentes.",
            "plan": []
        }
    },

    "Tolerancia a la Presión": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Se descompensa bajo presión. Comete errores en situaciones críticas.",
            "plan": [
                "Capacitarse en manejo de estrés laboral.",
                "Practicar técnicas de respiración y control emocional.",
                "Trabajar bajo supervisión en situaciones de alta demanda."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Muestra nerviosismo bajo presión. Calidad disminuye en picos de producción.",
            "plan": [
                "Desarrollar técnicas de manejo de presión.",
                "Simular situaciones de alta demanda para practicar.",
                "Solicitar apoyo del supervisor en momentos críticos."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Mantiene rendimiento bajo presión. Responde bien en situaciones críticas.",
            "plan": [
                "Fortalecer capacidad de respuesta rápida.",
                "Liderar en situaciones de alta demanda.",
                "Apoyar a compañeros que tienen dificultades."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente bajo presión. Genera confianza en el equipo.",
            "plan": [
                "Ser referente en momentos críticos.",
                "Capacitar al equipo en manejo de presión.",
                "Liderar respuesta en situaciones de emergencia."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Excepcional bajo presión. Convierte situaciones críticas en oportunidades.",
            "plan": []
        }
    },

    "Productividad": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No cumple metas de producción. Genera desperdicios frecuentes.",
            "plan": [
                "Recibir capacitación en optimización de materia prima.",
                "Establecer metas diarias incrementales.",
                "Identificar causas de baja productividad con el supervisor."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Cumple parcialmente metas. Genera desperdicios ocasionales.",
            "plan": [
                "Implementar técnicas de reducción de desperdicios.",
                "Aumentar velocidad sin comprometer calidad.",
                "Monitorear indicadores de productividad diariamente."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Cumple metas de producción con calidad estándar y desperdicios controlados.",
            "plan": [
                "Optimizar procesos para aumentar productividad.",
                "Reducir tiempos muertos entre tareas.",
                "Proponer mejoras en flujo de trabajo."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Supera metas consistentemente. Minimiza desperdicios y optimiza recursos.",
            "plan": [
                "Documentar técnicas de alta productividad.",
                "Capacitar a compañeros en optimización.",
                "Proponer nuevas metas de producción."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Productividad excepcional. Referente en eficiencia y aprovechamiento de recursos.",
            "plan": []
        }
    },

    "Operación técnica de la máquina": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No configura correctamente la maquinaria. Genera productos defectuosos.",
            "plan": [
                "Capacitación técnica urgente en configuración de máquinas.",
                "Estudiar manuales técnicos y procedimientos operativos.",
                "Practicar bajo supervisión directa hasta certificar competencia."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Configura máquinas con errores. Requiere apoyo frecuente.",
            "plan": [
                "Reforzar capacitación en ajustes técnicos.",
                "Utilizar guías de configuración paso a paso.",
                "Verificar medidas y ajustes antes de iniciar producción."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Configura máquinas correctamente según orden de producción.",
            "plan": [
                "Reducir tiempos de configuración.",
                "Aprender ajustes avanzados de maquinaria.",
                "Certificarse en operación de equipos adicionales."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Configuración experta y rápida. Optimiza parámetros de máquina.",
            "plan": [
                "Capacitar a operarios en configuración técnica.",
                "Documentar mejores prácticas de setup.",
                "Proponer mejoras en procedimientos de configuración."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Maestro técnico. Referente en operación y configuración de maquinaria.",
            "plan": []
        }
    },

    "Mantenimiento Preventivo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No realiza limpieza ni mantenimiento básico. Equipos en mal estado.",
            "plan": [
                "Capacitarse en procedimientos de limpieza y mantenimiento básico.",
                "Implementar rutina diaria de inspección y limpieza.",
                "Reportar inmediatamente anomalías al supervisor."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Realiza limpieza básica pero incompleta. Descuida mantenimiento preventivo.",
            "plan": [
                "Seguir checklist completo de mantenimiento preventivo.",
                "Dedicar tiempo suficiente a limpieza de equipos.",
                "Registrar actividades de mantenimiento realizadas."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Realiza mantenimiento preventivo y limpieza adecuadamente.",
            "plan": [
                "Identificar mejoras en procedimientos de mantenimiento.",
                "Capacitarse en mantenimiento preventivo avanzado.",
                "Apoyar a compañeros en cultura de mantenimiento."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Mantenimiento ejemplar. Equipos siempre en óptimas condiciones.",
            "plan": [
                "Liderar programa de mantenimiento autónomo.",
                "Capacitar al equipo en mantenimiento preventivo.",
                "Proponer mejoras en plan de mantenimiento."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Excelencia en mantenimiento. Previene averías y extiende vida útil de equipos.",
            "plan": []
        }
    },

    "Calidad del Producto": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Genera productos con defectos graves. No cumple estándares de calidad.",
            "plan": [
                "Capacitación urgente en estándares de calidad.",
                "Implementar inspección supervisada de cada producto.",
                "Estudiar causas de defectos y cómo prevenirlos."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Productos con defectos frecuentes. Requiere reprocesos.",
            "plan": [
                "Reforzar conocimiento de estándares de calidad.",
                "Implementar autocontrol durante el proceso.",
                "Reducir tasa de productos no conformes."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Produce con calidad estándar. Mínimos defectos y desperdicios.",
            "plan": [
                "Buscar cero defectos en producción.",
                "Implementar mejoras en control de calidad.",
                "Documentar buenas prácticas de calidad."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Alta calidad consistente. Productos premium con mínimos rechazos.",
            "plan": [
                "Ser referente en estándares de calidad.",
                "Capacitar al equipo en control de calidad.",
                "Proponer mejoras en procesos de aseguramiento."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Excelencia en calidad. Referente en producción de alta calidad.",
            "plan": []
        }
    }
}


# ===================== FUNCIÓN DE GENERACIÓN DE PLAN =====================

def generar_plan_mejora_operarios_produccion(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Operarios de Producción
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
║                        OPERARIO DE PRODUCCIÓN                                ║
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
        for competencia_key in RESPUESTAS_OPERARIOS_PRODUCCION.keys():
            if competencia_key.lower() in pregunta_texto.lower():
                competencia_encontrada = competencia_key
                break

        if not competencia_encontrada:
            # Si no se encuentra, usar el primer elemento del texto de la pregunta
            competencia_encontrada = pregunta_texto.split(':')[0] if ':' in pregunta_texto else pregunta_texto[:50]

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
            if competencia_encontrada in RESPUESTAS_OPERARIOS_PRODUCCION and puntuacion in RESPUESTAS_OPERARIOS_PRODUCCION[competencia_encontrada]:
                datos_plan = RESPUESTAS_OPERARIOS_PRODUCCION[competencia_encontrada][puntuacion]

                plan_texto += f"   📋 PLAN DE ACCIÓN:\n"

                # Tomar solo los primeros 3 items del plan
                items_plan = datos_plan['plan'][:3]

                for idx, item in enumerate(items_plan, 1):
                    plan_texto += f"   {idx}. {item}\n"

                # Marcar si requiere seguimiento bimensual (cualquier puntuación de pregunta ≤ 4)
                # Solo las preguntas con calificación 5 NO requieren seguimiento
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
    asignacion = respuestas_evaluacion.first().asignacion if respuestas_evaluacion.exists() else None
    if asignacion and asignacion.uso_epp_sst:
        sst_texto = "\n" + "="*80 + "\n\n"
        sst_texto += "⚠️  OBSERVACIÓN DE SEGURIDAD Y SALUD EN EL TRABAJO (SST)\n\n"
        sst_texto += "USO DE ELEMENTOS DE PROTECCIÓN PERSONAL (EPP):\n"

        if asignacion.uso_epp_sst == 'correcto':
            sst_texto += "✅ El empleado utiliza correctamente los EPP y promueve su uso.\n"
            sst_texto += "   FELICITACIONES: Mantener este compromiso con la seguridad.\n"
        elif asignacion.uso_epp_sst == 'a_veces':
            sst_texto += "⚠️  El empleado a veces no utiliza adecuadamente los EPP.\n\n"
            sst_texto += "📋 ACCIONES REQUERIDAS:\n"
            sst_texto += "   1. Asistir a capacitación sobre uso correcto de EPP\n"
            sst_texto += "   2. Leer y firmar protocolo de seguridad actualizado\n"
            sst_texto += "   3. Compromiso de uso permanente de implementos de seguridad\n"
            sst_texto += "\n   ⚠️  REQUIERE SEGUIMIENTO MENSUAL EN SST\n"
        elif asignacion.uso_epp_sst == 'nunca':
            sst_texto += "❌ El empleado no utiliza los EPP o no promueve su uso.\n\n"
            sst_texto += "📋 ACCIONES INMEDIATAS REQUERIDAS:\n"
            sst_texto += "   1. Capacitación urgente en SST y uso obligatorio de EPP\n"
            sst_texto += "   2. Firma de compromiso de cumplimiento de normas de seguridad\n"
            sst_texto += "   3. Supervisión semanal por parte del coordinador de SST\n"
            sst_texto += "   4. En caso de reincidencia, aplicar medidas disciplinarias\n"
            sst_texto += "\n   🚨 REQUIERE SEGUIMIENTO SEMANAL INMEDIATO\n"

        sst_texto += "\n" + "="*80 + "\n\n"
        sst_texto += "NOTA: Esta observación no afecta el puntaje de la evaluación de desempeño,\n"
        sst_texto += "      pero es un requisito obligatorio de cumplimiento normativo.\n\n"
        planes.append(sst_texto)

    # Footer
    plan_footer = """
═══════════════════════════════════════════════════════════════════════════════

OBSERVACIONES GENERALES DEL EVALUADOR:
[Espacio para comentarios adicionales del jefe inmediato]



COMPROMISOS DEL EVALUADO:
[Espacio para que el empleado registre sus compromisos específicos]



FIRMA DEL EMPLEADO: _____________________  FECHA: _______________

FIRMA DEL JEFE INMEDIATO: _______________  FECHA: _______________

═══════════════════════════════════════════════════════════════════════════════
"""

    planes.append(plan_footer)

    return "".join(planes)

# ===================== FUNCIONES DE UTILIDAD =====================

def requiere_seguimientos_bimensuales(puntaje_porcentaje):
    """
    Determina si se requieren seguimientos bimensuales
    basado en el puntaje total.

    Args:
        puntaje_porcentaje: float (0-100)

    Returns:
        bool: True si requiere seguimientos
    """
    # Seguimientos requeridos si el puntaje es menor a 91% (Muy alto)
    return puntaje_porcentaje < 91.0


def crear_seguimientos_bimensuales_operarios(plan_mejora):
    """
    Crea seguimientos bimensuales específicos para operarios de producción.
    Reutiliza la función general de respuestas_predefinidas.
    """
    from ..utils.respuestas_predefinidas import crear_seguimientos_bimensuales
    return crear_seguimientos_bimensuales(plan_mejora)


def calcular_puntaje_ponderado_operarios_produccion(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado para evaluación anual de Operarios de Producción.

    Aplica ponderación por categorías:
    - Competencias Organizacionales: 10%
    - Objetivos: 40%
    - Competencias Interpersonales: 25%
    - Competencias Técnicas: 25%

    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion

    Returns:
        dict con:
        - puntaje_escala: float (1-5)
        - puntaje_porcentaje: float (0-100)
        - nivel_desempeno: str
        - detalle_categorias: dict con info por categoría
    """
    from collections import defaultdict

    # Agrupar respuestas por categoría
    respuestas_por_categoria = defaultdict(list)
    for respuesta in respuestas_evaluacion:
        categoria_nombre = respuesta.pregunta.categoria
        puntaje = respuesta.puntaje_obtenido
        respuestas_por_categoria[categoria_nombre].append(float(puntaje))

    # Calcular promedio y contribución por categoría
    detalle_categorias = {}
    puntaje_total_ponderado = 0.0

    for categoria, ponderacion in PONDERACION_CATEGORIAS.items():
        if categoria in respuestas_por_categoria:
            puntajes = respuestas_por_categoria[categoria]
            promedio = sum(puntajes) / len(puntajes)

            # Convertir promedio (1-5) a porcentaje (0-100)
            porcentaje_categoria = (promedio / 5.0) * 100

            # Aplicar ponderación
            contribucion = porcentaje_categoria * ponderacion
            puntaje_total_ponderado += contribucion

            detalle_categorias[categoria] = {
                'promedio': round(promedio, 2),
                'porcentaje': round(porcentaje_categoria, 2),
                'ponderacion': int(ponderacion * 100),
                'contribucion': round(contribucion, 2)
            }

    # Calcular puntaje final en escala 1-5
    puntaje_escala = (puntaje_total_ponderado / 100.0) * 5.0

    # Determinar nivel de desempeño
    if puntaje_total_ponderado >= 91:
        nivel_desempeno = 'Muy alto'
    elif puntaje_total_ponderado >= 76:
        nivel_desempeno = 'Alto'
    elif puntaje_total_ponderado >= 61:
        nivel_desempeno = 'Moderado'
    elif puntaje_total_ponderado >= 41:
        nivel_desempeno = 'Bajo'
    else:
        nivel_desempeno = 'Muy bajo'

    return {
        'puntaje_escala': round(puntaje_escala, 2),
        'puntaje_porcentaje': round(puntaje_total_ponderado, 2),
        'nivel_desempeno': nivel_desempeno,
        'detalle_categorias': detalle_categorias
    }
