# =============================================================================
# apps/evaluations/utils/respuestas_predefinidas_auxiliares_administrativos.py
# Sistema de respuestas predefinidas para Auxiliares Administrativos
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

RESPUESTAS_AUXILIARES_ADMINISTRATIVOS = {
    "Comunicación": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No transmite información de manera clara. No escucha activamente propuestas.",
            "plan": [
                "Participar en taller de comunicación efectiva en entorno administrativo.",
                "Practicar comunicación escrita y oral con retroalimentación del supervisor.",
                "Desarrollar hábito de escucha activa en reuniones y conversaciones."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Comunica pero con poca claridad. A veces no escucha completamente las instrucciones.",
            "plan": [
                "Capacitación en redacción de documentos administrativos.",
                "Verificar comprensión repitiendo instrucciones recibidas.",
                "Solicitar retroalimentación sobre claridad en la comunicación."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Comunica de manera adecuada tanto oral como escrita. Escucha propuestas.",
            "plan": [
                "Fortalecer habilidades de comunicación asertiva.",
                "Mejorar capacidad de síntesis en informes.",
                "Participar en dinámicas de comunicación en equipo."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente comunicación, clara y convincente. Muy receptivo a propuestas.",
            "plan": [
                "Mantener nivel de comunicación efectiva.",
                "Apoyar a compañeros en mejorar su comunicación.",
                "Liderar presentaciones en reuniones de equipo."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Comunicación excepcional en todos los canales. Referente del área.",
            "plan": []
        }
    },

    "Trabajo en equipo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Dificultad para colaborar. No comparte información ni conocimiento con el equipo.",
            "plan": [
                "Participar activamente en dinámicas de integración.",
                "Comprometerse a compartir información relevante con el equipo.",
                "Recibir coaching sobre trabajo colaborativo."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Colabora ocasionalmente. Falta más participación activa en objetivos del área.",
            "plan": [
                "Identificar oportunidades para apoyar a compañeros.",
                "Participar en al menos 2 proyectos colaborativos mensuales.",
                "Fortalecer actitud de servicio interno."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Colabora adecuadamente. Comparte recursos y conocimiento cuando se le solicita.",
            "plan": [
                "Ser más proactivo en ofrecer apoyo al equipo.",
                "Compartir mejores prácticas administrativas.",
                "Fortalecer relaciones interpersonales en el área."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente colaborador. Comparte proactivamente y contribuye al logro de objetivos.",
            "plan": [
                "Mantener espíritu colaborativo.",
                "Mentorear a nuevos integrantes del equipo.",
                "Liderar iniciativas de mejora en colaboración."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Pilar fundamental del equipo. Ejemplo de colaboración y apoyo.",
            "plan": []
        }
    },

    "Mejora continua": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No cumple estándares de calidad. Resistente a proponer mejoras en procesos.",
            "plan": [
                "Capacitación en estándares de calidad administrativa.",
                "Revisar y adoptar procedimientos establecidos.",
                "Participar en taller de mejora continua."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Cumple mínimamente estándares. Rara vez propone mejoras.",
            "plan": [
                "Identificar al menos 2 oportunidades de mejora mensuales.",
                "Estudiar mejores prácticas administrativas.",
                "Documentar procesos actuales para mejorarlos."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Cumple estándares de calidad. Ocasionalmente propone mejoras.",
            "plan": [
                "Ser más proactivo en proponer optimizaciones.",
                "Participar en comités de mejora continua.",
                "Implementar al menos 1 mejora trimestral en sus procesos."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Alto estándar de calidad. Propone regularmente mejoras efectivas.",
            "plan": [
                "Mantener enfoque en mejora continua.",
                "Compartir mejores prácticas con otras áreas.",
                "Liderar proyectos de optimización de procesos."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Referente en calidad y mejora continua. Innovador en modernización.",
            "plan": []
        }
    },

    "Brindar soporte operativo y administrativo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No gestiona adecuadamente documentos ni correspondencia. Desorden en actividades de oficina.",
            "plan": [
                "Capacitación intensiva en gestión documental y administrativa.",
                "Establecer rutina diaria de organización y priorización.",
                "Supervisión directa en manejo de correspondencia y trámites."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Soporte básico pero con errores frecuentes. Falta orden y oportunidad.",
            "plan": [
                "Implementar checklist de tareas administrativas diarias.",
                "Mejorar gestión del tiempo en atención a clientes.",
                "Capacitación en manejo de correspondencia y radicación."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Brinda soporte adecuado. Puede mejorar en eficiencia y anticipación de necesidades.",
            "plan": [
                "Optimizar tiempos de respuesta en trámites.",
                "Anticipar necesidades de clientes internos/externos.",
                "Mejorar organización de archivo y documentación."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente soporte operativo. Eficiente, ordenado y oportuno en todas sus tareas.",
            "plan": [
                "Mantener estándares de excelencia.",
                "Apoyar en capacitación de nuevos auxiliares.",
                "Proponer mejoras en procesos administrativos."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Soporte excepcional. Referente en eficiencia y calidad administrativa.",
            "plan": []
        }
    },

    "Orientación al cliente": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Actitud deficiente hacia clientes. No resuelve solicitudes oportunamente.",
            "plan": [
                "Capacitación en servicio al cliente y actitud de servicio.",
                "Implementar protocolos de atención al cliente.",
                "Seguimiento diario de solicitudes pendientes."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Atiende pero sin anticipar necesidades. Actitud de servicio irregular.",
            "plan": [
                "Mejorar tiempos de respuesta a solicitudes.",
                "Desarrollar empatía y actitud proactiva.",
                "Solicitar retroalimentación de clientes atendidos."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Buena atención. Resuelve solicitudes pero puede anticipar más necesidades.",
            "plan": [
                "Desarrollar capacidad de anticipación a necesidades.",
                "Implementar seguimiento proactivo a solicitudes.",
                "Mejorar personalización en el trato."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente orientación al cliente. Anticipa necesidades y resuelve oportunamente.",
            "plan": [
                "Mantener estándares de servicio.",
                "Compartir mejores prácticas con el equipo.",
                "Liderar iniciativas de mejora en atención al cliente."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Referente en servicio al cliente. Actitud excepcional.",
            "plan": []
        }
    },

    "Atención al detalle": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Errores frecuentes en documentos. No revisa antes de radicar o enviar.",
            "plan": [
                "Implementar lista de verificación antes de radicar documentos.",
                "Capacitación en técnicas de revisión y control de calidad.",
                "Doble revisión supervisada durante 1 mes."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Revisa pero aún comete errores evitables. Falta consistencia.",
            "plan": [
                "Establecer rutina de revisión sistemática.",
                "Usar herramientas de corrección ortográfica y formato.",
                "Solicitar retroalimentación sobre precisión en documentos."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Revisa adecuadamente. Errores ocasionales que puede reducir.",
            "plan": [
                "Mejorar técnicas de revisión de documentos.",
                "Implementar pausas antes de enviar documentos críticos.",
                "Desarrollar mayor concentración en tareas de detalle."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente atención al detalle. Muy pocos errores, alta precisión.",
            "plan": [
                "Mantener estándares de precisión.",
                "Apoyar en revisión de documentos críticos.",
                "Compartir técnicas de verificación con el equipo."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Precisión excepcional. Referente en calidad de documentos.",
            "plan": []
        }
    },

    "Capacidad de planeación y organización": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Desorganizado. Requiere supervisión constante para cumplir tareas.",
            "plan": [
                "Capacitación en gestión del tiempo y priorización.",
                "Usar herramientas de organización (agenda, calendario).",
                "Reuniones diarias con supervisor para organizar tareas."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Organiza básicamente pero necesita recordatorios frecuentes.",
            "plan": [
                "Implementar sistema de organización personal.",
                "Establecer prioridades al inicio de cada jornada.",
                "Reducir dependencia de supervisión externa."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Organiza adecuadamente su agenda y prioridades sin supervisión constante.",
            "plan": [
                "Mejorar anticipación de tareas recurrentes.",
                "Optimizar distribución del tiempo en el día.",
                "Implementar planificación semanal además de diaria."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente organización. Anticipa y prioriza efectivamente.",
            "plan": [
                "Mantener alto nivel de organización.",
                "Apoyar a compañeros en planificación de tareas.",
                "Liderar mejoras en organización del área."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Organización excepcional. Referente en planificación.",
            "plan": []
        }
    },

    "Manejo básico de Office": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No domina Word, Excel ni PowerPoint. Requiere asistencia constante.",
            "plan": [
                "Capacitación intensiva en Microsoft Office básico.",
                "Practicar diariamente creación de documentos en Word.",
                "Aprender funciones básicas de Excel (tablas, fórmulas simples)."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Conocimiento básico pero limitado. Dificultad con funciones intermedias.",
            "plan": [
                "Curso de Office nivel intermedio.",
                "Practicar elaboración de informes en Word con formato.",
                "Aprender tablas dinámicas y gráficos en Excel."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Domina funciones básicas. Puede mejorar en funciones avanzadas.",
            "plan": [
                "Capacitación en funciones avanzadas de Excel.",
                "Mejorar diseño de presentaciones en PowerPoint.",
                "Aprender macros y automatizaciones básicas."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente dominio de Office. Usa funciones avanzadas efectivamente.",
            "plan": [
                "Mantener actualización en nuevas versiones de Office.",
                "Apoyar a compañeros en uso de Office.",
                "Explorar Power BI o herramientas complementarias."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Dominio excepcional. Referente en Office.",
            "plan": []
        }
    },

    "Gestión documental y archivo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No clasifica ni radica adecuadamente. Desorden en archivo y custodia.",
            "plan": [
                "Capacitación en gestión documental y normatividad.",
                "Aprender técnicas de clasificación y radicación.",
                "Implementar sistema de archivo con supervisión directa."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Clasifica básicamente pero con errores. Archivo desorganizado.",
            "plan": [
                "Reforzar conocimiento en tablas de retención documental.",
                "Mejorar técnicas de clasificación y rotulado.",
                "Establecer rutina semanal de organización de archivo."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Gestiona adecuadamente documentos. Archivo organizado.",
            "plan": [
                "Optimizar tiempos de búsqueda y recuperación.",
                "Implementar sistema de archivo digital más eficiente.",
                "Capacitación en preservación documental."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente gestión documental. Sistema de archivo eficiente.",
            "plan": [
                "Mantener estándares de organización.",
                "Liderar mejoras en gestión documental del área.",
                "Capacitar a compañeros en buenas prácticas."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Gestión documental excepcional. Referente.",
            "plan": []
        }
    },

    "Manejo de software contable/administrativo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No opera el sistema de facturación/órdenes. Requiere asistencia constante.",
            "plan": [
                "Capacitación intensiva en el sistema de información usado.",
                "Practicar operaciones básicas con supervisión.",
                "Crear manual personalizado de uso del sistema."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Opera funciones básicas con dificultad. Muchas consultas al soporte.",
            "plan": [
                "Capacitación intermedia en el software.",
                "Practicar procesos de facturación y órdenes.",
                "Reducir dependencia de soporte técnico."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Opera adecuadamente el sistema. Puede mejorar en funciones avanzadas.",
            "plan": [
                "Aprender módulos avanzados del sistema.",
                "Optimizar tiempos en procesos recurrentes.",
                "Explorar reportes y consultas personalizadas."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Excelente manejo del sistema. Opera eficientemente todos los módulos.",
            "plan": [
                "Mantener dominio del sistema.",
                "Apoyar a compañeros en uso del software.",
                "Proponer mejoras en parametrización."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Dominio excepcional. Referente técnico del sistema.",
            "plan": []
        }
    },

    "Conocimiento básico contable": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No comprende conceptos contables básicos. Dificultad en facturación y cuentas.",
            "plan": [
                "Capacitación en conceptos contables básicos.",
                "Aprender proceso de facturación y su impacto contable.",
                "Estudiar cuentas por cobrar y por pagar."
            ]
        },
        2: {
            "titulo": "⭐⭐ Calificación 2 – Cumple mínimamente",
            "recomendacion": "Conocimiento muy básico. Requiere apoyo constante en temas contables.",
            "plan": [
                "Curso de contabilidad básica empresarial.",
                "Practicar clasificación de documentos contables.",
                "Aprender lectura de estados financieros básicos."
            ]
        },
        3: {
            "titulo": "⭐⭐⭐ Calificación 3 – Cumple satisfactoriamente",
            "recomendacion": "Comprende conceptos básicos. Apoya adecuadamente procesos de facturación.",
            "plan": [
                "Profundizar en conceptos contables intermedios.",
                "Aprender sobre conciliaciones y ajustes.",
                "Mejorar comprensión de impuestos y retenciones."
            ]
        },
        4: {
            "titulo": "⭐⭐⭐⭐ Calificación 4 – Supera expectativas",
            "recomendacion": "Buen conocimiento contable. Apoya efectivamente en procesos financieros.",
            "plan": [
                "Mantener conocimientos actualizados.",
                "Apoyar en capacitación de nuevos auxiliares.",
                "Explorar temas contables más avanzados."
            ]
        },
        5: {
            "titulo": "⭐⭐⭐⭐⭐ Calificación 5 – Excelente",
            "recomendacion": "Conocimiento contable excepcional para nivel auxiliar.",
            "plan": []
        }
    }
}


# ===================== FUNCIONES =====================

def calcular_puntaje_ponderado_auxiliares_administrativos(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado para auxiliares administrativos según categorías.

    Ponderación:
    - Competencias Organizacionales (preguntas 1-3): 10%
    - Objetivos (pregunta 4): 40%
    - Competencias Interpersonales (preguntas 5-7): 25%
    - Competencias Técnicas (preguntas 8-11): 25%
    TOTAL: 100%
    """

    # Mapeo: orden de pregunta -> categoría
    MAPEO_CATEGORIAS = {
        1: "Competencias Organizacionales",
        2: "Competencias Organizacionales",
        3: "Competencias Organizacionales",
        4: "Objetivos",
        5: "Competencias Interpersonales",
        6: "Competencias Interpersonales",
        7: "Competencias Interpersonales",
        8: "Competencias Técnicas",
        9: "Competencias Técnicas",
        10: "Competencias Técnicas",
        11: "Competencias Técnicas"
    }

    # Contadores por categoría
    suma_por_categoria = {
        "Competencias Organizacionales": 0,
        "Objetivos": 0,
        "Competencias Interpersonales": 0,
        "Competencias Técnicas": 0
    }

    count_por_categoria = {
        "Competencias Organizacionales": 0,
        "Objetivos": 0,
        "Competencias Interpersonales": 0,
        "Competencias Técnicas": 0
    }

    # Procesar cada respuesta
    for respuesta in respuestas_evaluacion:
        if respuesta.opcion_seleccionada:
            orden = respuesta.pregunta.orden
            valor = float(respuesta.opcion_seleccionada.valor_numerico)
            categoria = MAPEO_CATEGORIAS.get(orden)

            if categoria:
                suma_por_categoria[categoria] += valor
                count_por_categoria[categoria] += 1

    # Calcular promedios y contribuciones por categoría
    detalle_categorias = {}
    puntaje_total_ponderado = 0

    for categoria, ponderacion in PONDERACION_CATEGORIAS.items():
        if count_por_categoria[categoria] > 0:
            promedio = suma_por_categoria[categoria] / count_por_categoria[categoria]
            porcentaje = (promedio / 5) * 100
            contribucion = (promedio / 5) * (ponderacion * 100)

            detalle_categorias[categoria] = {
                'promedio': round(promedio, 2),
                'porcentaje': round(porcentaje, 2),
                'ponderacion': ponderacion * 100,
                'contribucion': round(contribucion, 2)
            }

            puntaje_total_ponderado += contribucion

    # Convertir puntaje total a escala de 5
    puntaje_escala = (puntaje_total_ponderado / 100) * 5

    # Determinar nivel de desempeño
    if puntaje_total_ponderado >= 18:
        nivel_desempeno = "Excelente"
    elif puntaje_total_ponderado >= 14:
        nivel_desempeno = "Bueno"
    elif puntaje_total_ponderado >= 10:
        nivel_desempeno = "Satisfactorio"
    else:
        nivel_desempeno = "Necesita Mejorar"

    return {
        'puntaje_porcentaje': round(puntaje_total_ponderado, 2),
        'puntaje_escala': round(puntaje_escala, 2),
        'nivel_desempeno': nivel_desempeno,
        'detalle_categorias': detalle_categorias
    }


def generar_plan_mejora_auxiliares_administrativos(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para auxiliares administrativos
    basado en respuestas y resultado ponderado.
    """
    planes = []

    # Encabezado
    plan_header = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              PLAN DE MEJORA - EVALUACIÓN ANUAL DE DESEMPEÑO                  ║
║                       AUXILIARES ADMINISTRATIVOS                             ║
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

    # Plan detallado por pregunta
    planes.append("EVALUACIÓN POR COMPETENCIA:\n\n")

    contador = 1

    for respuesta in respuestas_evaluacion.order_by('pregunta__orden'):
        pregunta_texto = respuesta.pregunta.pregunta or respuesta.pregunta.categoria
        puntuacion = int(respuesta.opcion_seleccionada.valor_numerico) if respuesta.opcion_seleccionada else 0

        # Buscar competencia en diccionario
        competencia_encontrada = None
        for competencia_key in RESPUESTAS_AUXILIARES_ADMINISTRATIVOS.keys():
            if competencia_key.lower() in pregunta_texto.lower():
                competencia_encontrada = competencia_key
                break

        if not competencia_encontrada:
            competencia_encontrada = pregunta_texto[:80]

        plan_texto = f"{contador}. {competencia_encontrada}\n"
        plan_texto += f"   Calificación: {puntuacion}/5\n"

        # Agregar comentarios del evaluador si existen
        plan_texto += formatear_comentarios_evaluador(respuesta)
        plan_texto += "\n"

        # Plan según puntuación
        if puntuacion == 5:
            plan_texto += "   ✅ ¡EXCELENTE DESEMPEÑO!\n"
            plan_texto += "   El empleado ha demostrado dominio excepcional en esta competencia.\n"
            plan_texto += "   Continue con este nivel de excelencia.\n"
        else:
            if competencia_encontrada in RESPUESTAS_AUXILIARES_ADMINISTRATIVOS and puntuacion in RESPUESTAS_AUXILIARES_ADMINISTRATIVOS[competencia_encontrada]:
                datos_plan = RESPUESTAS_AUXILIARES_ADMINISTRATIVOS[competencia_encontrada][puntuacion]

                plan_texto += f"   📋 PLAN DE ACCIÓN:\n"

                items_plan = datos_plan['plan'][:3]

                for idx, item in enumerate(items_plan, 1):
                    plan_texto += f"   {idx}. {item}\n"

                if puntuacion <= 4:
                    plan_texto += f"\n   ⚠️  REQUIERE SEGUIMIENTO BIMENSUAL\n"
            else:
                plan_texto += f"   📋 PLAN DE ACCIÓN:\n"
                plan_texto += f"   1. Revisar procedimientos y mejores prácticas relacionadas.\n"
                plan_texto += f"   2. Solicitar retroalimentación constante del supervisor.\n"
                plan_texto += f"   3. Establecer metas específicas para mejorar en esta área.\n"

        plan_texto += "\n" + "-"*80 + "\n\n"
        planes.append(plan_texto)
        contador += 1

    # Footer
    planes.append("="*80 + "\n")
    planes.append("INSTRUCCIONES:\n")
    planes.append("1. Este plan debe ser revisado y aceptado por el empleado.\n")
    planes.append("2. Se realizarán 3 seguimientos bimensuales (cada 2 meses) durante 6 meses.\n")
    planes.append("3. Al finalizar el período se realizará una evaluación final del plan.\n")
    planes.append("4. Las competencias con seguimiento bimensual deben mostrar avance progresivo.\n")
    planes.append("="*80 + "\n")

    return "".join(planes)
