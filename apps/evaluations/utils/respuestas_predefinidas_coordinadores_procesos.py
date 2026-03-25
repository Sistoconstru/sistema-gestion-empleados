# =============================================================================
# apps/evaluations/utils/respuestas_predefinidas_coordinadores_procesos.py
# Sistema de respuestas predefinidas para Coordinadores de Procesos
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

RESPUESTAS_COORDINADORES_PROCESOS = {
    "Comunicación": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No comunica efectivamente instrucciones al equipo. Genera confusiones y malentendidos.",
            "plan": [
                "Capacitarse en comunicación efectiva para líderes.",
                "Implementar reuniones diarias de equipo para aclarar objetivos.",
                "Solicitar retroalimentación sobre claridad en instrucciones."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Comunica pero de forma poco clara. El equipo requiere aclaraciones frecuentes.",
            "plan": [
                "Mejorar técnicas de comunicación asertiva.",
                "Utilizar medios escritos para instrucciones importantes.",
                "Verificar comprensión del equipo antes de ejecutar tareas."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Comunica adecuadamente pero puede mejorar en comunicación estratégica.",
            "plan": [
                "Desarrollar habilidades de comunicación gerencial.",
                "Implementar reportes estructurados al área de producción.",
                "Mejorar comunicación ascendente con gerencia."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Comunicación efectiva y clara. El equipo entiende y ejecuta correctamente.",
            "plan": [
                "Mantener excelencia en comunicación.",
                "Ser mentor de otros coordinadores en comunicación efectiva.",
                "Implementar mejoras en canales de comunicación."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Comunicación ejemplar. Genera claridad y alineación total del equipo.",
            "plan": []
        }
    },

    "Trabajo en equipo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No fomenta colaboración. Crea ambiente de trabajo divisivo.",
            "plan": [
                "Capacitarse en liderazgo y construcción de equipos.",
                "Implementar actividades de integración de equipo.",
                "Desarrollar habilidades de resolución de conflictos."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Colabora ocasionalmente pero no promueve trabajo en equipo activamente.",
            "plan": [
                "Fortalecer cultura de colaboración en el área.",
                "Reconocer logros de equipo públicamente.",
                "Mediar conflictos de manera proactiva."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Promueve trabajo en equipo adecuadamente.",
            "plan": [
                "Implementar proyectos colaborativos entre áreas.",
                "Desarrollar liderazgo de equipo en subordinados.",
                "Fortalecer sinergia con otras coordinaciones."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente promotor de colaboración. Equipo cohesionado y productivo.",
            "plan": [
                "Liderar iniciativas de mejora interdepartamental.",
                "Compartir mejores prácticas de trabajo en equipo.",
                "Mentorizar a nuevos coordinadores."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Referente en construcción de equipos de alto desempeño.",
            "plan": []
        }
    },

    "Mejora continua": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No implementa mejoras. Mantiene procesos obsoletos sin cuestionar.",
            "plan": [
                "Capacitarse en metodologías de mejora continua (Lean, Kaizen).",
                "Identificar al menos 3 oportunidades de mejora mensual.",
                "Implementar ciclo PDCA en área de responsabilidad."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Reactivo a cambios pero no propone mejoras proactivamente.",
            "plan": [
                "Liderar proyecto piloto de mejora en un proceso clave.",
                "Involucrar al equipo en identificación de oportunidades.",
                "Documentar y medir impacto de mejoras implementadas."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Implementa mejoras regularmente. Busca eficiencia en procesos.",
            "plan": [
                "Aumentar frecuencia y alcance de proyectos de mejora.",
                "Capacitar al equipo en herramientas de mejora continua.",
                "Establecer indicadores de mejora en el área."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Líder en mejora continua. Genera impacto significativo en productividad.",
            "plan": [
                "Liderar programa de mejora continua a nivel planta.",
                "Certificarse en metodologías avanzadas (Six Sigma).",
                "Compartir casos de éxito con otras áreas."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Referente en innovación y mejora. Genera cultura de excelencia operacional.",
            "plan": []
        }
    },

    "Planificación y control de producción": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No planifica actividades. Descontrol en recursos, metas y seguridad.",
            "plan": [
                "Capacitación urgente en planificación de producción.",
                "Implementar herramientas de programación y control.",
                "Recibir acompañamiento de gerencia de producción."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Planifica básicamente pero con incumplimientos frecuentes.",
            "plan": [
                "Mejorar técnicas de estimación y programación.",
                "Implementar seguimiento diario de cumplimiento de metas.",
                "Optimizar asignación de recursos humanos y materiales."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Planifica y controla adecuadamente. Cumple metas con eficiencia aceptable.",
            "plan": [
                "Implementar técnicas avanzadas de planificación (MRP, JIT).",
                "Reducir variabilidad en cumplimiento de metas.",
                "Optimizar uso de recursos para mayor eficiencia."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente planificación y control. Supera metas con eficiencia destacada.",
            "plan": [
                "Ser referente en planificación de producción.",
                "Capacitar a otros coordinadores en mejores prácticas.",
                "Proponer mejoras en sistema de planificación de la planta."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Maestría en planificación. Referente en gestión operacional.",
            "plan": []
        }
    },

    "Liderazgo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No dirige efectivamente. Equipo desmotivado y sin dirección clara.",
            "plan": [
                "Capacitarse en liderazgo situacional y gestión de equipos.",
                "Implementar reuniones one-on-one con miembros del equipo.",
                "Desarrollar plan de motivación y reconocimiento."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Liderazgo básico. Equipo funciona por inercia más que por motivación.",
            "plan": [
                "Fortalecer habilidades de coaching y desarrollo de personal.",
                "Establecer objetivos claros y comunicarlos efectivamente.",
                "Reconocer logros y gestionar bajo desempeño apropiadamente."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Lidera adecuadamente. Equipo orientado y con motivación aceptable.",
            "plan": [
                "Desarrollar liderazgo transformacional.",
                "Implementar programa de desarrollo de talento en el equipo.",
                "Fortalecer autoridad moral y ejemplo personal."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Liderazgo inspirador. Equipo altamente motivado y comprometido.",
            "plan": [
                "Mentorizar a otros líderes de la organización.",
                "Liderar proyectos estratégicos de alto impacto.",
                "Desarrollar líderes dentro del equipo."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Liderazgo excepcional. Genera equipos de alto desempeño y potencia talentos.",
            "plan": []
        }
    },

    "Toma de Decisiones": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Evita tomar decisiones o toma decisiones inapropiadas frecuentemente.",
            "plan": [
                "Capacitarse en toma de decisiones y análisis de riesgos.",
                "Implementar matriz de decisiones para evaluar opciones.",
                "Practicar toma de decisiones con supervisión de gerencia."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Toma decisiones básicas pero con inseguridad y lentitud.",
            "plan": [
                "Desarrollar confianza en toma de decisiones operativas.",
                "Aprender a priorizar y actuar con información limitada.",
                "Analizar casos de estudio de decisiones efectivas."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Toma decisiones oportunas considerando pros y contras.",
            "plan": [
                "Mejorar velocidad de toma de decisiones sin sacrificar calidad.",
                "Desarrollar visión estratégica en decisiones operativas.",
                "Capacitarse en análisis de causa raíz y solución de problemas."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Decisiones rápidas, acertadas y con visión de impacto.",
            "plan": [
                "Tomar decisiones estratégicas de mayor alcance.",
                "Ser referente en toma de decisiones bajo presión.",
                "Capacitar al equipo en toma de decisiones efectivas."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Excelencia en toma de decisiones. Soluciones rápidas y efectivas ante situaciones críticas.",
            "plan": []
        }
    },

    "Tolerancia a la Presión": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Se descompensa bajo presión. Afecta negativamente al equipo en situaciones críticas.",
            "plan": [
                "Capacitarse en manejo de estrés y resiliencia.",
                "Implementar técnicas de gestión emocional.",
                "Recibir coaching en manejo de situaciones de alta presión."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Mantiene funcionalidad básica bajo presión pero con deterioro visible.",
            "plan": [
                "Desarrollar estrategias de afrontamiento ante picos de demanda.",
                "Practicar toma de decisiones en simulaciones de crisis.",
                "Mejorar delegación para distribuir carga de trabajo."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Mantiene rendimiento bajo presión. Responde adecuadamente en situaciones críticas.",
            "plan": [
                "Fortalecer capacidad de respuesta rápida.",
                "Liderar al equipo efectivamente en momentos de alta demanda.",
                "Desarrollar planes de contingencia para situaciones críticas."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente bajo presión. Lidera efectivamente en situaciones críticas.",
            "plan": [
                "Ser referente en manejo de crisis.",
                "Capacitar al equipo en manejo de situaciones de presión.",
                "Liderar respuesta ante emergencias operacionales."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Excepcional bajo presión. Convierte situaciones críticas en oportunidades de mejora.",
            "plan": []
        }
    },

    "Integridad": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No actúa con ética. Incumple normas y no es coherente entre lo que dice y hace.",
            "plan": [
                "Revisión urgente de código de ética empresarial.",
                "Compromiso escrito de cumplimiento de valores organizacionales.",
                "Seguimiento cercano por parte de gerencia."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Cumple normas básicas pero con inconsistencias ocasionales.",
            "plan": [
                "Reforzar compromiso con valores organizacionales.",
                "Ser ejemplo de ética y cumplimiento de procedimientos.",
                "Reflexionar sobre impacto de decisiones en equipo y organización."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Actúa con integridad. Coherente entre valores declarados y acciones.",
            "plan": [
                "Fortalecer rol de modelo ético para el equipo.",
                "Promover cultura de cumplimiento en el área.",
                "Tomar decisiones considerando impacto ético y de SST."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Ejemplo de integridad. Promueve cultura ética en el área.",
            "plan": [
                "Ser embajador de valores organizacionales.",
                "Liderar comités de ética y cumplimiento.",
                "Influir positivamente en cultura organizacional."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Referente de integridad. Genera confianza absoluta en organización y equipo.",
            "plan": []
        }
    },

    "Gestión de Producción y Rendimientos": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No optimiza materia prima. Desperdicios excesivos y rotación inadecuada de personal.",
            "plan": [
                "Capacitación urgente en gestión de producción y rendimientos.",
                "Implementar controles de desperdicio y aprovechamiento.",
                "Optimizar planificación de rotación de personal."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Gestión básica con desperdicio por encima del estándar.",
            "plan": [
                "Implementar indicadores de rendimiento y desperdicios.",
                "Capacitar al equipo en optimización de materia prima.",
                "Mejorar planificación de rotación según demanda."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Gestiona adecuadamente. Desperdicios dentro del estándar aceptable.",
            "plan": [
                "Reducir desperdicio por debajo del estándar actual.",
                "Optimizar rendimiento de materia prima mediante mejoras técnicas.",
                "Implementar mejores prácticas de rotación de personal."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente gestión. Minimiza desperdicios y optimiza rotación.",
            "plan": [
                "Ser referente en gestión de rendimientos.",
                "Compartir mejores prácticas con otras áreas.",
                "Proponer mejoras en procesos de aprovechamiento."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Maestría en gestión de producción. Rendimientos excepcionales.",
            "plan": []
        }
    },

    "Control de Calidad y Normatividad": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No verifica calidad. Productos no conformes frecuentes y dimensiones incorrectas.",
            "plan": [
                "Capacitación urgente en control de calidad y normatividad.",
                "Implementar inspecciones de calidad en puntos críticos.",
                "Aprender uso de instrumentos de medición de precisión."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Control básico pero con defectos frecuentes y decisiones técnicas cuestionables.",
            "plan": [
                "Fortalecer conocimiento de especificaciones técnicas.",
                "Implementar procedimiento de decisión técnica con Director de Planta.",
                "Reducir tasa de productos no conformes."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Control de calidad adecuado. Decisiones técnicas apropiadas.",
            "plan": [
                "Implementar control estadístico de calidad.",
                "Reducir variabilidad en productos.",
                "Fortalecer criterios técnicos de aceptación/rechazo."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente control de calidad. Decisiones técnicas acertadas.",
            "plan": [
                "Ser referente en aseguramiento de calidad.",
                "Capacitar a otros coordinadores en control de calidad.",
                "Proponer mejoras en sistema de calidad de la planta."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Maestría en control de calidad. Productos consistentemente excelentes.",
            "plan": []
        }
    },

    "Supervisión de Mantenimiento": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No diagnostica problemas. Averías mayores frecuentes por falta de prevención.",
            "plan": [
                "Capacitarse en diagnóstico de fallas mecánicas y eléctricas.",
                "Implementar programa de mantenimiento preventivo.",
                "Coordinar efectivamente con personal de mantenimiento."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Reacciona a fallas pero no anticipa. Mantenimiento preventivo insuficiente.",
            "plan": [
                "Fortalecer capacidad de diagnóstico temprano.",
                "Implementar inspecciones preventivas programadas.",
                "Reportar oportunamente anomalías a mantenimiento."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Diagnostica problemas oportunamente. Previene averías mayores.",
            "plan": [
                "Implementar mantenimiento predictivo.",
                "Capacitarse en mantenimiento autónomo.",
                "Optimizar coordinación con área de mantenimiento."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente supervisión. Minimiza paradas y averías.",
            "plan": [
                "Liderar programa de mantenimiento preventivo del área.",
                "Capacitar al equipo en cuidado de maquinaria.",
                "Ser referente en diagnóstico y prevención."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Maestría en supervisión de mantenimiento. Equipos en condiciones óptimas.",
            "plan": []
        }
    }
}


# ===================== FUNCIÓN DE GENERACIÓN DE PLAN =====================

def generar_plan_mejora_coordinadores_procesos(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Coordinadores de Procesos
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
║                     COORDINADOR DE PROCESOS                                  ║
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
        for competencia_key in RESPUESTAS_COORDINADORES_PROCESOS.keys():
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
            plan_texto += "   El coordinador ha demostrado dominio excepcional en esta competencia.\n"
            plan_texto += "   Continue con este nivel de excelencia.\n"

        # Si puntuación es 4 o menos: Plan de acción con máximo 3 items
        else:
            if competencia_encontrada in RESPUESTAS_COORDINADORES_PROCESOS and puntuacion in RESPUESTAS_COORDINADORES_PROCESOS[competencia_encontrada]:
                datos_plan = RESPUESTAS_COORDINADORES_PROCESOS[competencia_encontrada][puntuacion]

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
                plan_texto += f"   2. Solicitar retroalimentación constante de la gerencia de producción.\n"
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
            sst_texto += "✅ El coordinador utiliza correctamente los EPP y promueve su uso en el equipo.\n"
            sst_texto += "   FELICITACIONES: Mantener este liderazgo en seguridad.\n"
        elif asignacion.uso_epp_sst == 'a_veces':
            sst_texto += "⚠️  El coordinador a veces no utiliza adecuadamente los EPP.\n\n"
            sst_texto += "📋 ACCIONES REQUERIDAS:\n"
            sst_texto += "   1. Reforzar compromiso personal con uso de EPP\n"
            sst_texto += "   2. Ser ejemplo visible de cumplimiento de normas de seguridad\n"
            sst_texto += "   3. Liderar cultura de seguridad en el área de responsabilidad\n"
            sst_texto += "\n   ⚠️  REQUIERE SEGUIMIENTO MENSUAL EN SST\n"
        elif asignacion.uso_epp_sst == 'nunca':
            sst_texto += "❌ El coordinador no utiliza los EPP o no promueve su uso.\n\n"
            sst_texto += "📋 ACCIONES INMEDIATAS REQUERIDAS:\n"
            sst_texto += "   1. Compromiso escrito de cumplimiento de normas de SST\n"
            sst_texto += "   2. Capacitación en liderazgo de seguridad\n"
            sst_texto += "   3. Ser modelo de comportamiento seguro para el equipo\n"
            sst_texto += "   4. Implementar inspecciones de seguridad en el área\n"
            sst_texto += "\n   🚨 REQUIERE SEGUIMIENTO SEMANAL INMEDIATO\n"

        sst_texto += "\n" + "="*80 + "\n\n"
        sst_texto += "NOTA: Esta observación no afecta el puntaje de la evaluación de desempeño,\n"
        sst_texto += "      pero es un requisito obligatorio de cumplimiento normativo.\n\n"
        planes.append(sst_texto)

    # Footer
    plan_footer = """
═══════════════════════════════════════════════════════════════════════════════

OBSERVACIONES GENERALES DE GERENCIA:
[Espacio para comentarios adicionales de la gerencia de producción]



COMPROMISOS DEL COORDINADOR:
[Espacio para que el coordinador registre sus compromisos específicos]



FIRMA DEL COORDINADOR: _____________________  FECHA: _______________

FIRMA DEL GERENTE: __________________________  FECHA: _______________

═══════════════════════════════════════════════════════════════════════════════
"""

    planes.append(plan_footer)

    return "".join(planes)

# ===================== FUNCIONES DE UTILIDAD =====================

def calcular_puntaje_ponderado_coordinadores_procesos(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado para evaluación anual de Coordinadores de Procesos.

    Aplica ponderación por categorías:
    - Competencias Organizacionales: 10%
    - Objetivos: 40%
    - Competencias Interpersonales: 25%
    - Competencias Técnicas: 25%

    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion

    Returns:
        dict con puntaje_escala, puntaje_porcentaje, nivel_desempeno, detalle_categorias
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


def requiere_seguimientos_bimensuales(puntaje_porcentaje):
    """Determina si se requieren seguimientos bimensuales"""
    return puntaje_porcentaje < 91.0


def crear_seguimientos_bimensuales_coordinadores(plan_mejora):
    """Crea seguimientos bimensuales para coordinadores de procesos."""
    from ..utils.respuestas_predefinidas import crear_seguimientos_bimensuales
    return crear_seguimientos_bimensuales(plan_mejora)
