# =============================================================================
# apps/evaluations/utils/respuestas_predefinidas_mantenimiento.py
# Sistema de respuestas predefinidas para Evaluación Anual - Mantenimiento
# Escala: 1-5 (Muy bajo a Muy alto)
# =============================================================================

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# ===================== CONFIGURACIÓN DE PONDERACIÓN =====================

PONDERACION_CATEGORIAS = {
    "Competencias Organizacionales": 0.10,  # 10%
    "Objetivos": 0.40,  # 40%
    "Competencias Interpersonales": 0.25,  # 25%
    "Competencias Técnicas": 0.25  # 25%
}

DISTRIBUCION_PREGUNTAS = {
    "Competencias Organizacionales": 3,  # 3 preguntas
    "Objetivos": 1,  # 1 pregunta
    "Competencias Interpersonales": 3,  # 3 preguntas
    "Competencias Técnicas": 3  # 3 preguntas
}

# ===================== RESPUESTAS PREDEFINIDAS POR COMPETENCIA =====================

RESPUESTAS_MANTENIMIENTO = {
    # ======================== COMPETENCIAS ORGANIZACIONALES (10%) ========================

    "Comunicación": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "Presenta dificultades significativas para comunicar información técnica de forma clara. No reporta fallas adecuadamente ni transmite información crítica, generando confusión y afectando la coordinación del equipo de mantenimiento.",
            "plan": [
                "Participar en talleres de comunicación técnica efectiva.",
                "Implementar formato estandarizado para reporte de fallas y trabajos realizados.",
                "Practicar técnicas de comunicación de información técnica a personal no técnico.",
                "Solicitar retroalimentación inmediata sobre claridad de reportes.",
                "Establecer reuniones semanales con supervisor para mejorar comunicación."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Comunicación técnica básica y a veces poco clara. Reporta información esencial pero tiene dificultades para explicar procedimientos complejos o escuchar activamente sugerencias de otros.",
            "plan": [
                "Mejorar documentación de trabajos de mantenimiento realizados.",
                "Practicar explicación de procedimientos técnicos de forma estructurada.",
                "Solicitar ejemplos de buenos reportes técnicos y replicarlos.",
                "Aumentar participación en reuniones técnicas del equipo.",
                "Desarrollar habilidades de escucha activa en diagnóstico de fallas."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Se comunica de manera aceptable en la mayoría de situaciones técnicas. Transmite información de fallas claramente, aunque puede mejorar en documentación y comunicación de procedimientos complejos.",
            "plan": [
                "Continuar fortaleciendo habilidades de comunicación técnica.",
                "Mejorar calidad de documentación de procedimientos de mantenimiento.",
                "Buscar oportunidades para capacitar a compañeros en procedimientos técnicos.",
                "Solicitar retroalimentación periódica sobre claridad de reportes.",
                "Mantener apertura para recibir y dar sugerencias técnicas."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Excelente capacidad de comunicación técnica. Transmite información de fallas claramente, documenta procedimientos correctamente y facilita el entendimiento mutuo en el equipo de mantenimiento.",
            "plan": [
                "Mantener las prácticas actuales de comunicación técnica efectiva.",
                "Servir como modelo para compañeros con menor desarrollo en esta área.",
                "Liderar capacitaciones técnicas para el equipo.",
                "Compartir mejores prácticas de documentación técnica.",
                "Apoyar en estandarización de formatos de reporte de mantenimiento."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Sobresale por su comunicación técnica excepcional. Reporta fallas con precisión, documenta procedimientos ejemplarmente y genera ambiente de colaboración y aprendizaje continuo en el equipo.",
            "plan": [
                "Continuar siendo referente en comunicación técnica efectiva.",
                "Mentor de nuevos técnicos en documentación y reporte de trabajos.",
                "Liderar creación de manuales de procedimientos de mantenimiento.",
                "Documentar mejores prácticas de comunicación técnica para el área.",
                "Representar al equipo en reuniones interdepartamentales técnicas."
            ]
        }
    },

    "Trabajo en equipo": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "Presenta serias dificultades para trabajar con otros técnicos. No colabora en trabajos que requieren coordinación, genera conflictos y no comparte conocimientos técnicos. Su actitud afecta negativamente el funcionamiento del equipo.",
            "plan": [
                "Participar obligatoriamente en actividades de integración del equipo de mantenimiento.",
                "Establecer metas semanales específicas de colaboración con compañeros.",
                "Recibir coaching sobre trabajo en equipo en entornos técnicos.",
                "Identificar y trabajar barreras personales que dificultan la colaboración.",
                "Comprometerse a solicitar y ofrecer ayuda en trabajos técnicos complejos."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Muestra disposición limitada para colaborar en trabajos técnicos. Trabaja de manera aislada frecuentemente y solo coopera cuando se le solicita directamente. Requiere fortalecer iniciativa colaborativa.",
            "plan": [
                "Participar activamente en trabajos de mantenimiento que requieran equipo.",
                "Practicar ofrecer ayuda proactivamente a compañeros en tareas complejas.",
                "Compartir conocimientos técnicos y experiencias con el equipo regularmente.",
                "Participar en reuniones técnicas aportando ideas constructivas.",
                "Reflexionar semanalmente sobre oportunidades de colaboración técnica."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Colabora adecuadamente en trabajos técnicos cuando es necesario. Comparte conocimientos básicos, coordina con compañeros y contribuye a objetivos comunes de manera satisfactoria.",
            "plan": [
                "Incrementar la frecuencia de colaboración espontánea en el taller.",
                "Identificar y proponer mejoras en procedimientos que beneficien al equipo.",
                "Desarrollar habilidades de coordinación en trabajos técnicos complejos.",
                "Participar en proyectos de mejora que requieran trabajo en equipo.",
                "Mantener actitud constructiva en situaciones de presión o emergencias."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Excelente colaborador técnico. Establece relaciones positivas, comparte conocimientos activamente, coordina eficientemente y contribuye significativamente al logro de objetivos del área de mantenimiento.",
            "plan": [
                "Mantener y potenciar el nivel actual de colaboración técnica.",
                "Asumir roles de coordinación en proyectos de mantenimiento mayor.",
                "Apoyar la integración y capacitación de nuevos técnicos.",
                "Proponer iniciativas que fortalezcan el trabajo colaborativo del equipo.",
                "Compartir mejores prácticas de trabajo en equipo con otros."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Referente excepcional en trabajo colaborativo técnico. Genera sinergias, facilita coordinación en trabajos complejos, resuelve conflictos constructivamente y maximiza el potencial colectivo del equipo.",
            "plan": [
                "Continuar siendo modelo de trabajo colaborativo en mantenimiento.",
                "Liderar iniciativas de mejoramiento del trabajo en equipo.",
                "Mentor de técnicos con menor desarrollo en esta competencia.",
                "Facilitar espacios de integración y fortalecimiento de equipo.",
                "Documentar prácticas efectivas de colaboración técnica para el área."
            ]
        }
    },

    "Mejora continua": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No muestra interés por mejorar procesos de mantenimiento ni adaptarse a nuevas tecnologías. Se resiste a nuevas metodologías y no busca soluciones a problemas recurrentes. Su actitud obstaculiza la innovación.",
            "plan": [
                "Participar en capacitación obligatoria sobre mejora continua en mantenimiento.",
                "Establecer meta mensual de proponer al menos una mejora en procedimientos.",
                "Acompañamiento semanal con supervisor para identificar oportunidades de mejora.",
                "Visitar otras áreas de mantenimiento para conocer mejores prácticas.",
                "Comprometerse a implementar al menos un cambio técnico sugerido por mes."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Acepta cambios cuando son obligatorios, pero no los promueve. Rara vez propone mejoras en procedimientos de mantenimiento y requiere supervisión constante para adaptarse a nuevas tecnologías.",
            "plan": [
                "Estudiar casos de éxito de mejora continua en mantenimiento industrial.",
                "Identificar semanalmente un aspecto mejorable en procedimientos técnicos.",
                "Participar activamente en sesiones de lluvia de ideas técnicas.",
                "Documentar fallas recurrentes y proponer soluciones preventivas.",
                "Solicitar retroalimentación sobre propuestas de mejora técnica."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Acepta y se adapta a mejoras propuestas en procedimientos de mantenimiento. Ocasionalmente sugiere modificaciones menores. Mantiene apertura moderada a nuevas tecnologías y metodologías.",
            "plan": [
                "Incrementar frecuencia de propuestas de mejora técnica (al menos 2 por mes).",
                "Participar en grupos de trabajo para optimización de mantenimiento.",
                "Estudiar metodologías de mantenimiento productivo total (TPM).",
                "Implementar ciclos PHVA en procedimientos propios de mantenimiento.",
                "Compartir aprendizajes sobre mejoras implementadas con el equipo."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Proactivo en la búsqueda de mejoras técnicas. Identifica oportunidades, propone soluciones viables y se adapta rápidamente a nuevas tecnologías. Promueve modernización de procesos de mantenimiento activamente.",
            "plan": [
                "Mantener actitud proactiva hacia la mejora continua técnica.",
                "Liderar proyectos de optimización de procedimientos de mantenimiento.",
                "Capacitar a compañeros en técnicas de mantenimiento preventivo avanzado.",
                "Documentar mejoras implementadas y sus resultados.",
                "Explorar formación en nuevas tecnologías de mantenimiento predictivo."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Agente de cambio excepcional en mantenimiento. Lidera iniciativas de mejora técnica, innova constantemente, facilita adaptación del equipo a nuevas tecnologías y genera cultura de excelencia en mantenimiento.",
            "plan": [
                "Continuar siendo referente en mejora continua de mantenimiento.",
                "Liderar programa de innovación técnica en el área.",
                "Mentor de otros técnicos en metodologías de mejora continua.",
                "Presentar casos de éxito en foros técnicos de la organización.",
                "Investigar tendencias y mejores prácticas de mantenimiento del sector."
            ]
        }
    },

    # ======================== OBJETIVOS (40%) ========================

    "Mantenimiento de Maquinaria": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No cumple con las tareas básicas de mantenimiento preventivo ni correctivo. Las máquinas presentan paradas frecuentes por falta de mantenimiento adecuado. No garantiza disponibilidad de maquinaria crítica.",
            "plan": [
                "Reentrenamiento urgente en procedimientos básicos de mantenimiento preventivo.",
                "Supervisión directa diaria por una semana para identificar brechas técnicas.",
                "Establecer metas diarias claras y medibles para mantenimiento.",
                "Capacitación intensiva en diagnóstico básico de fallas mecánicas/eléctricas.",
                "Evaluación semanal de desempeño con plan de acción correctivo."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Cumple parcialmente con mantenimiento preventivo y correctivo. Las reparaciones son lentas o requieren rehacer trabajos. No siempre minimiza tiempos de parada de máquinas críticas.",
            "plan": [
                "Capacitación específica en diagnóstico rápido y efectivo de fallas.",
                "Practicar procedimientos de mantenimiento bajo supervisión hasta alcanzar estándar.",
                "Implementar checklist de verificación para mantenimiento preventivo.",
                "Mejorar manejo de herramientas y repuestos para reducir tiempos.",
                "Solicitar retroalimentación diaria sobre calidad y velocidad de trabajos."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Realiza satisfactoriamente mantenimiento preventivo y correctivo de maquinaria. Minimiza tiempos de parada en la mayoría de casos, aunque puede mejorar eficiencia en diagnóstico y reparación.",
            "plan": [
                "Optimizar tiempos de diagnóstico mediante técnicas más eficientes.",
                "Mejorar precisión en reparaciones para reducir reincidencias.",
                "Proponer mejoras en cronograma de mantenimiento preventivo.",
                "Participar activamente en análisis de fallas recurrentes.",
                "Documentar procedimientos efectivos para compartir con compañeros."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Desempeño destacado en mantenimiento de maquinaria. Realiza mantenimiento preventivo y correctivo con alta eficiencia. Minimiza tiempos de parada y garantiza disponibilidad de equipos críticos.",
            "plan": [
                "Mantener estándares de excelencia en mantenimiento.",
                "Entrenar a compañeros en técnicas de diagnóstico rápido.",
                "Proponer e implementar mejoras en sistemas de mantenimiento preventivo.",
                "Asumir responsabilidades adicionales en mantenimiento de equipos complejos.",
                "Participar en definición de mejores prácticas de mantenimiento."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Desempeño excepcional y ejemplar en mantenimiento. Máxima eficiencia en mantenimiento preventivo y correctivo. Anticipa fallas, optimiza disponibilidad de maquinaria y es referente técnico del equipo.",
            "plan": [
                "Continuar siendo modelo de excelencia en mantenimiento.",
                "Liderar programa de estandarización de mejores prácticas técnicas.",
                "Mentor principal de nuevos técnicos de mantenimiento.",
                "Participar en diseño de programas de mantenimiento predictivo.",
                "Representar al área en comités técnicos de productividad."
            ]
        }
    },

    # ======================== COMPETENCIAS INTERPERSONALES (25%) ========================

    "Iniciativa": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No actúa proactivamente ante señales de falla. Espera a que las máquinas se dañen completamente antes de reportar. No toma decisiones técnicas independientes ni anticipa problemas.",
            "plan": [
                "Capacitación en detección temprana de fallas (ruidos, vibraciones, temperaturas).",
                "Establecer sistema de reporte inmediato de anomalías detectadas.",
                "Desarrollar criterio técnico mediante casos de estudio de fallas.",
                "Supervisión para fomentar toma de decisiones técnicas básicas.",
                "Implementar inspecciones preventivas diarias con reporte obligatorio."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Poca iniciativa para anticiparse a fallas. Ocasionalmente detecta anomalías pero no siempre actúa preventivamente. Requiere supervisión para tomar decisiones técnicas.",
            "plan": [
                "Desarrollar habilidades de inspección sensorial (visual, auditiva, táctil).",
                "Practicar toma de decisiones técnicas en situaciones de menor criticidad.",
                "Participar en análisis de fallas para mejorar capacidad de anticipación.",
                "Establecer rutina diaria de inspección preventiva de equipos críticos.",
                "Solicitar retroalimentación sobre calidad de detección temprana de fallas."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Detecta y reporta anomalías razonablemente. Se anticipa a algunas fallas mediante inspección rutinaria. Toma decisiones técnicas básicas de forma independiente.",
            "plan": [
                "Incrementar capacidad de análisis predictivo de fallas.",
                "Mejorar habilidades de diagnóstico técnico avanzado.",
                "Proponer mejoras en sistemas de detección temprana de anomalías.",
                "Desarrollar mayor autonomía en solución de problemas técnicos.",
                "Compartir experiencias de detección temprana con el equipo."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Alta proactividad técnica. Se anticipa efectivamente a fallas mediante inspección detallada. Detecta anomalías sutiles y actúa preventivamente. Toma decisiones técnicas acertadas de forma independiente.",
            "plan": [
                "Mantener nivel de proactividad y criterio técnico actual.",
                "Entrenar a compañeros en técnicas de detección temprana de fallas.",
                "Liderar implementación de sistemas de mantenimiento predictivo.",
                "Documentar indicadores tempranos de falla para el equipo.",
                "Participar en desarrollo de procedimientos de inspección preventiva."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Proactividad excepcional. Anticipa fallas con precisión mediante análisis técnico avanzado. Detecta anomalías antes que se conviertan en problemas. Toma decisiones técnicas complejas con excelente criterio.",
            "plan": [
                "Continuar siendo referente en proactividad técnica.",
                "Liderar programa de mantenimiento predictivo del área.",
                "Capacitar al equipo en análisis de condición de máquinas.",
                "Desarrollar indicadores predictivos de falla para equipos críticos.",
                "Representar al área en comités de confiabilidad operacional."
            ]
        }
    },

    "Análisis de Problemas": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No identifica causas raíz de fallas. Realiza reparaciones superficiales que no solucionan problemas. Las mismas fallas se repiten frecuentemente por diagnóstico deficiente.",
            "plan": [
                "Capacitación urgente en metodologías de análisis de fallas (RCA).",
                "Practicar diagnóstico sistemático bajo supervisión directa.",
                "Estudiar casos de fallas recurrentes y sus soluciones definitivas.",
                "Implementar uso obligatorio de checklist de diagnóstico.",
                "Evaluación técnica semanal de capacidad de análisis."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Capacidad limitada de análisis de fallas. Identifica síntomas pero no siempre encuentra causas raíz. Las soluciones propuestas no siempre son definitivas.",
            "plan": [
                "Mejorar técnicas de diagnóstico mediante metodología 5 Porqués.",
                "Participar en análisis de fallas junto con técnicos más experimentados.",
                "Estudiar diagramas de causa-efecto aplicados a fallas mecánicas.",
                "Documentar proceso de diagnóstico para mejorar razonamiento técnico.",
                "Solicitar validación de diagnósticos antes de implementar soluciones."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Identifica causas raíz en la mayoría de casos. Propone soluciones que reducen reincidencia de fallas. Realiza análisis técnico satisfactorio, aunque puede mejorar en casos complejos.",
            "plan": [
                "Fortalecer habilidades de análisis en fallas complejas o inusuales.",
                "Estudiar análisis de vibración y termografía para mejor diagnóstico.",
                "Participar en capacitaciones de análisis de fallas avanzado.",
                "Documentar lecciones aprendidas de fallas resueltas.",
                "Proponer mejoras en metodologías de diagnóstico del área."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Excelente capacidad de análisis técnico. Identifica causas raíz con precisión. Propone soluciones definitivas que eliminan reincidencias. Resuelve fallas complejas efectivamente.",
            "plan": [
                "Mantener nivel de análisis técnico actual.",
                "Entrenar a compañeros en metodologías de análisis de fallas.",
                "Liderar investigaciones de fallas críticas o recurrentes.",
                "Documentar casos de éxito en resolución de problemas complejos.",
                "Participar en mejora de procedimientos de diagnóstico."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Experto en análisis de fallas. Identifica causas raíz de problemas complejos con precisión excepcional. Propone soluciones innovadoras y definitivas. Referente técnico en diagnóstico.",
            "plan": [
                "Continuar siendo experto técnico en análisis de fallas.",
                "Liderar programa de capacitación en RCA para el equipo.",
                "Desarrollar metodologías propias de diagnóstico avanzado.",
                "Participar en análisis de fallas críticas a nivel corporativo.",
                "Representar al área en comités técnicos de confiabilidad."
            ]
        }
    },

    "Responsabilidad": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No promueve objetivos del área ni mantiene ambiente adecuado. No demuestra preocupación por calidad de trabajos de mantenimiento. Su actitud afecta resultados y clima del equipo.",
            "plan": [
                "Establecer compromisos claros sobre responsabilidades de mantenimiento.",
                "Supervisión directa diaria con retroalimentación inmediata.",
                "Capacitación sobre responsabilidad y sentido de pertenencia.",
                "Implementar sistema de autoevaluación de calidad de trabajos.",
                "Reuniones semanales de seguimiento con supervisor."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Cumple responsabilidades básicas con inconsistencias. Poca preocupación proactiva por calidad de mantenimiento. Requiere supervisión frecuente para asegurar cumplimiento.",
            "plan": [
                "Desarrollar mayor conciencia sobre impacto de trabajos mal realizados.",
                "Establecer checklist de verificación de calidad para cada trabajo.",
                "Participar en espacios de reflexión sobre cultura de calidad.",
                "Mejorar comunicación proactiva sobre problemas o dificultades técnicas.",
                "Solicitar retroalimentación semanal sobre nivel de responsabilidad."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Promueve adecuadamente objetivos del área y mantiene ambiente laboral aceptable. Demuestra preocupación por realizar trabajos de mantenimiento con calidad satisfactoria.",
            "plan": [
                "Incrementar iniciativa en promoción de objetivos del área.",
                "Fortalecer compromiso con mejora continua de calidad técnica.",
                "Participar más activamente en actividades de ambiente laboral.",
                "Desarrollar mayor autonomía en aseguramiento de calidad.",
                "Proponer iniciativas que fortalezcan cultura de responsabilidad."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Altamente responsable. Promueve activamente objetivos del área, mantiene excelente ambiente laboral y demuestra constante preocupación por calidad, precisión y contribución al éxito del mantenimiento.",
            "plan": [
                "Mantener nivel de responsabilidad y compromiso actual.",
                "Servir como modelo de comportamiento responsable para el equipo.",
                "Participar en comités de calidad o mejora del área.",
                "Mentor de técnicos en desarrollo de responsabilidad profesional.",
                "Liderar iniciativas que fortalezcan cultura de excelencia técnica."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Responsabilidad ejemplar y excepcional. Líder en promoción de objetivos, genera ambiente laboral positivo, máxima calidad técnica. Verdadero agente de éxito del área de mantenimiento.",
            "plan": [
                "Continuar siendo referente de responsabilidad y excelencia.",
                "Liderar programa de cultura de calidad en mantenimiento.",
                "Participar en comités estratégicos de calidad y ambiente laboral.",
                "Desarrollar materiales de capacitación sobre responsabilidad técnica.",
                "Representar al área como embajador de cultura de excelencia."
            ]
        }
    },

    # ======================== COMPETENCIAS TÉCNICAS (25%) ========================

    "Disponibilidad de Máquina": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "Tiempos de parada excesivos por fallas frecuentes. No realiza mantenimiento preventivo adecuado. Las máquinas bajo su responsabilidad presentan baja disponibilidad operativa crítica.",
            "plan": [
                "Reentrenamiento urgente en mantenimiento preventivo sistemático.",
                "Implementar cronograma estricto de inspección y lubricación de equipos.",
                "Supervisión directa de cumplimiento de rutinas de mantenimiento.",
                "Capacitación en detección temprana de fallas potenciales.",
                "Evaluación semanal de indicadores de disponibilidad de máquinas."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Disponibilidad de máquinas por debajo del estándar. Paradas frecuentes por mantenimiento preventivo incompleto o reparaciones que requieren rehacerse. Necesita mejorar efectividad.",
            "plan": [
                "Mejorar cumplimiento riguroso de cronograma de mantenimiento preventivo.",
                "Capacitación en técnicas de mantenimiento que maximicen disponibilidad.",
                "Implementar indicadores personales de disponibilidad de equipos.",
                "Reducir tiempos de reparación mediante mejor preparación y planificación.",
                "Solicitar retroalimentación semanal sobre efectividad de mantenimiento."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Disponibilidad de máquinas dentro del estándar. Cumple mantenimiento preventivo regularmente. Los tiempos de parada son aceptables, aunque puede optimizar efectividad.",
            "plan": [
                "Optimizar cronograma de mantenimiento para maximizar disponibilidad.",
                "Implementar técnicas de mantenimiento predictivo en equipos críticos.",
                "Reducir variabilidad en tiempos de reparación.",
                "Proponer mejoras en procedimientos de mantenimiento preventivo.",
                "Documentar mejores prácticas que aumenten disponibilidad."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Alta disponibilidad de máquinas. Mantenimiento preventivo riguroso y efectivo. Reparaciones rápidas y definitivas. Paradas mínimas y bien planificadas.",
            "plan": [
                "Mantener indicadores de alta disponibilidad de equipos.",
                "Entrenar a compañeros en técnicas de mantenimiento efectivo.",
                "Proponer mejoras en sistemas de mantenimiento preventivo.",
                "Implementar mantenimiento predictivo en más equipos.",
                "Compartir mejores prácticas de maximización de disponibilidad."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Disponibilidad excepcional de máquinas. Mantenimiento preventivo y predictivo ejemplar. Paradas mínimas, planificadas y ejecutadas eficientemente. Referente en disponibilidad operativa.",
            "plan": [
                "Continuar siendo modelo de excelencia en disponibilidad de equipos.",
                "Liderar programa de confiabilidad operacional del área.",
                "Desarrollar estándares de mantenimiento de clase mundial.",
                "Mentor en técnicas avanzadas de mantenimiento preventivo/predictivo.",
                "Representar al área en comités de productividad y confiabilidad."
            ]
        }
    },

    "Efectividad del Arreglo": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "Reparaciones de baja calidad que no solucionan causa raíz. Reincidencias frecuentes de las mismas fallas. Los arreglos realizados no son duraderos ni confiables.",
            "plan": [
                "Reentrenamiento completo en técnicas de reparación efectiva.",
                "Supervisión directa de todas las reparaciones hasta mejorar calidad.",
                "Implementar procedimiento obligatorio de verificación post-reparación.",
                "Estudiar casos de fallas recurrentes y sus soluciones definitivas.",
                "Evaluación de calidad de cada reparación con retroalimentación inmediata."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Calidad de reparaciones inconsistente. Algunas fallas se repiten por soluciones temporales. Necesita mejorar análisis de causa raíz y técnicas de reparación definitiva.",
            "plan": [
                "Capacitación en metodologías de reparación que aseguren durabilidad.",
                "Implementar checklist de verificación de calidad de reparaciones.",
                "Practicar análisis de causa raíz antes de cada reparación.",
                "Documentar y analizar casos de reincidencias de fallas.",
                "Solicitar validación técnica de reparaciones complejas antes de cerrar."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Calidad de reparaciones satisfactoria. La mayoría de arreglos solucionan causas raíz y son duraderos. Reincidencias ocasionales en casos complejos.",
            "plan": [
                "Mejorar técnicas de reparación en casos complejos o especializados.",
                "Reducir reincidencias al mínimo mediante mejor análisis previo.",
                "Participar en capacitaciones de técnicas avanzadas de reparación.",
                "Documentar procedimientos de reparación exitosos.",
                "Proponer mejoras en estándares de calidad de reparaciones."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Alta efectividad en reparaciones. Soluciona causas raíz consistentemente. Arreglos duraderos y confiables. Reincidencias mínimas. Contribuye significativamente a estabilidad operativa.",
            "plan": [
                "Mantener estándares de excelencia en calidad de reparaciones.",
                "Entrenar a compañeros en técnicas de reparación definitiva.",
                "Documentar mejores prácticas de reparación para el área.",
                "Participar en desarrollo de procedimientos estándar de reparación.",
                "Liderar análisis de fallas complejas o recurrentes."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Efectividad excepcional en reparaciones. Soluciones definitivas de alta calidad técnica. Cero reincidencias. Innovador en técnicas de reparación. Referente técnico en el área.",
            "plan": [
                "Continuar siendo experto en reparaciones de excelencia.",
                "Liderar programa de estandarización de reparaciones de calidad.",
                "Desarrollar nuevas técnicas de reparación para el área.",
                "Mentor principal en métodos de reparación efectiva.",
                "Representar al área en comités técnicos de confiabilidad."
            ]
        }
    },

    "Cumplimiento de Cronograma": {
        1: {
            "titulo": "Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No cumple cronograma de mantenimiento preventivo. Actividades asignadas se retrasan constantemente. No ejecuta plan de mantenimiento según lo programado.",
            "plan": [
                "Establecer sistema de seguimiento diario de cumplimiento de cronograma.",
                "Capacitación en gestión del tiempo y priorización de tareas.",
                "Supervisión directa para asegurar cumplimiento de actividades programadas.",
                "Implementar alarmas y recordatorios de mantenimientos programados.",
                "Reunión semanal de revisión de cumplimiento con plan de acción."
            ]
        },
        2: {
            "titulo": "Bajo (2) - Necesita desarrollo",
            "recomendacion": "Cumplimiento parcial de cronograma. Retrasos frecuentes en mantenimiento preventivo. No siempre completa actividades asignadas según programación.",
            "plan": [
                "Mejorar planificación semanal de actividades de mantenimiento.",
                "Implementar sistema personal de seguimiento de tareas programadas.",
                "Identificar y eliminar causas de retrasos recurrentes.",
                "Coordinar mejor con producción para ventanas de mantenimiento.",
                "Solicitar retroalimentación semanal sobre cumplimiento de cronograma."
            ]
        },
        3: {
            "titulo": "Moderado (3) - Cumple lo esperado",
            "recomendacion": "Cumplimiento aceptable de cronograma de mantenimiento. Ejecuta la mayoría de actividades programadas a tiempo. Retrasos ocasionales justificados.",
            "plan": [
                "Incrementar cumplimiento a 100% del cronograma planificado.",
                "Mejorar coordinación para evitar retrasos por falta de recursos.",
                "Proponer optimizaciones en secuencia de actividades de mantenimiento.",
                "Anticipar posibles conflictos de programación y resolverlos proactivamente.",
                "Documentar mejores prácticas de gestión de cronograma."
            ]
        },
        4: {
            "titulo": "Alto (4) - Supera expectativas",
            "recomendacion": "Excelente cumplimiento de cronograma. Ejecuta 100% de actividades de mantenimiento preventivo según programación. Planifica eficientemente y se anticipa a conflictos.",
            "plan": [
                "Mantener nivel de cumplimiento riguroso de cronograma.",
                "Apoyar a compañeros en planificación y gestión de tiempo.",
                "Proponer mejoras en diseño de cronogramas de mantenimiento.",
                "Participar en optimización de frecuencias de mantenimiento preventivo.",
                "Compartir técnicas efectivas de planificación con el equipo."
            ]
        },
        5: {
            "titulo": "Muy alto (5) - Excelencia",
            "recomendacion": "Cumplimiento ejemplar del cronograma. 100% de ejecución de plan de mantenimiento. Planificación impecable y anticipación proactiva. Referente en disciplina de mantenimiento preventivo.",
            "plan": [
                "Continuar siendo modelo de disciplina en cumplimiento de cronograma.",
                "Liderar diseño y optimización de cronogramas de mantenimiento del área.",
                "Capacitar al equipo en técnicas de planificación y gestión del tiempo.",
                "Desarrollar herramientas de seguimiento de cumplimiento.",
                "Representar al área en comités de planificación de mantenimiento."
            ]
        }
    }
}

# ===================== FUNCIONES ESPECÍFICAS PARA MANTENIMIENTO =====================

def calcular_puntaje_ponderado_mantenimiento(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado para la evaluación de Mantenimiento
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

    # Mapeo de preguntas a categorías
    mapeo_preguntas_categorias = {
        "Comunicación": "Competencias Organizacionales",
        "Trabajo en equipo": "Competencias Organizacionales",
        "Mejora continua": "Competencias Organizacionales",
        "Mantenimiento de Maquinaria": "Objetivos",
        "Iniciativa": "Competencias Interpersonales",
        "Análisis de Problemas": "Competencias Interpersonales",
        "Responsabilidad": "Competencias Interpersonales",
        "Disponibilidad": "Competencias Técnicas",
        "Efectividad": "Competencias Técnicas",
        "Cumplimiento": "Competencias Técnicas"
    }

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

        # Si por alguna razón no tiene categoría, intentar mapear por texto
        if not categoria:
            pregunta_texto = respuesta.pregunta.pregunta or ""
            for clave_pregunta, cat in mapeo_preguntas_categorias.items():
                if clave_pregunta.lower() in pregunta_texto.lower():
                    categoria = cat
                    break

            # Fallback final
            if not categoria:
                categoria = "Competencias Técnicas"

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

def generar_plan_mejora_mantenimiento(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Mantenimiento
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
║                            MANTENIMIENTO                                     ║
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
        for competencia_key in RESPUESTAS_MANTENIMIENTO.keys():
            if competencia_key.lower() in pregunta_texto.lower():
                competencia_encontrada = competencia_key
                break

        if not competencia_encontrada:
            # Si no se encuentra, usar el primer elemento del texto de la pregunta
            competencia_encontrada = pregunta_texto.split(':')[0] if ':' in pregunta_texto else pregunta_texto[:50]

        plan_texto = f"{contador}. {competencia_encontrada}\n"
        plan_texto += f"   Calificación: {puntuacion}/5\n\n"

        # Si puntuación es 5: Felicitar
        if puntuacion == 5:
            plan_texto += "   ✅ ¡EXCELENTE DESEMPEÑO!\n"
            plan_texto += "   El empleado ha demostrado dominio excepcional en esta competencia.\n"
            plan_texto += "   Continue con este nivel de excelencia.\n"

        # Si puntuación es 4 o menos: Plan de acción con máximo 3 items
        else:
            if competencia_encontrada in RESPUESTAS_MANTENIMIENTO and puntuacion in RESPUESTAS_MANTENIMIENTO[competencia_encontrada]:
                datos_plan = RESPUESTAS_MANTENIMIENTO[competencia_encontrada][puntuacion]

                plan_texto += f"   📋 PLAN DE ACCIÓN:\n"

                # Tomar solo los primeros 3 items del plan
                items_plan = datos_plan['plan'][:3]

                for idx, item in enumerate(items_plan, 1):
                    plan_texto += f"   {idx}. {item}\n"

                # Marcar si requiere seguimiento bimensual (puntuaciones 1, 2 o 3)
                if puntuacion <= 3:
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
    return puntaje_porcentaje < 91

def crear_seguimientos_bimensuales_mantenimiento(plan_mejora):
    """
    Crea seguimientos bimensuales para evaluación de Mantenimiento.
    Reutiliza la función genérica de seguimientos.

    Args:
        plan_mejora: Instancia de PlanMejoraPredefinido
    """
    from ..utils.respuestas_predefinidas import crear_seguimientos_bimensuales
    return crear_seguimientos_bimensuales(plan_mejora)
