# =============================================================================
# apps/evaluations/utils/respuestas_predefinidas_auxiliar_procesos.py
# Sistema de respuestas predefinidas para Evaluación Anual - Auxiliares de Procesos
# Escala: 1-5 (Muy bajo a Muy alto)
# =============================================================================

from datetime import datetime, timedelta
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
    "Competencias Interpersonales": 3,  # 3 preguntas (Trabajo en equipo, Dinamismo, Responsabilidad)
    "Competencias Técnicas": 3  # 3 preguntas (Clasificación, Orden y aseo, Apoyo al proceso)
}

# ===================== RESPUESTAS PREDEFINIDAS POR COMPETENCIA =====================

RESPUESTAS_AUXILIAR_PROCESOS = {
    # ======================== COMPETENCIAS ORGANIZACIONALES (10%) ========================

    "Comunicación": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "Presenta dificultades significativas para comunicarse de forma clara y voluntaria. No transmite ideas ni opiniones de manera comprensible, lo que genera confusión y afecta negativamente la coordinación del equipo.",
            "plan": [
                "Participar en talleres de comunicación efectiva en el contexto laboral.",
                "Practicar diariamente la técnica de '5W' (qué, quién, cuándo, dónde, por qué) antes de transmitir información.",
                "Solicitar retroalimentación inmediata de compañeros sobre claridad de mensajes.",
                "Establecer espacios de práctica supervisada con el jefe directo.",
                "Usar herramientas visuales (diagramas, notas) para complementar comunicación verbal."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "La comunicación es básica y a veces poco clara. Puede transmitir información simple, pero tiene dificultades para expresar ideas complejas o escuchar activamente las propuestas de otros.",
            "plan": [
                "Preparar previamente los puntos clave antes de reuniones o conversaciones importantes.",
                "Practicar la técnica de parafraseo para confirmar comprensión.",
                "Solicitar ejemplos concretos cuando no entienda instrucciones.",
                "Aumentar participación en reuniones de equipo gradualmente.",
                "Leer material sobre comunicación asertiva y escucha activa."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Se comunica de manera aceptable en la mayoría de situaciones. Transmite información básica claramente, aunque puede mejorar en escucha activa y en la transmisión de ideas más complejas.",
            "plan": [
                "Continuar fortaleciendo habilidades de comunicación bidireccional.",
                "Practicar técnicas de resumen y síntesis de información.",
                "Buscar oportunidades para liderar pequeñas reuniones informativas.",
                "Solicitar retroalimentación periódica sobre estilo comunicativo.",
                "Mantener apertura para recibir y dar retroalimentación constructiva."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Demuestra muy buena capacidad comunicativa. Transmite ideas claramente, escucha activamente y facilita el entendimiento mutuo. Es receptivo a opiniones y las integra constructivamente.",
            "plan": [
                "Mantener las prácticas actuales de comunicación efectiva.",
                "Servir como modelo para compañeros con menor desarrollo en esta área.",
                "Participar en actividades que requieran negociación o coordinación compleja.",
                "Compartir técnicas personales de comunicación con el equipo.",
                "Explorar formación avanzada en comunicación (presentaciones, persuasión)."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Sobresale por su comunicación excepcional. Es claro, convincente, escucha activamente y genera ambiente de confianza. Facilita acuerdos y resuelve malentendidos eficazmente.",
            "plan": [
                "Continuar siendo referente en comunicación efectiva.",
                "Mentor de nuevos empleados en habilidades comunicativas.",
                "Liderar espacios de retroalimentación constructiva en el equipo.",
                "Documentar mejores prácticas de comunicación para el área.",
                "Representar al equipo en instancias que requieran comunicación formal."
            ]
        }
    },

    "Trabajo en equipo": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "Presenta serias dificultades para trabajar con otros. No colabora, genera conflictos frecuentes y no contribuye al logro de objetivos comunes. Su actitud afecta negativamente el ambiente laboral.",
            "plan": [
                "Participar obligatoriamente en actividades de integración y trabajo colaborativo.",
                "Establecer metas semanales específicas de colaboración con compañeros.",
                "Recibir coaching individual sobre trabajo en equipo por parte del supervisor.",
                "Identificar y trabajar barreras personales que dificultan la colaboración.",
                "Comprometerse a solicitar y ofrecer ayuda al menos una vez al día."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Muestra disposición limitada para colaborar. Trabaja de manera aislada frecuentemente y solo coopera cuando se le solicita directamente. Requiere fortalecer iniciativa colaborativa.",
            "plan": [
                "Participar activamente en al menos dos tareas colaborativas por semana.",
                "Practicar ofrecer ayuda proactivamente sin esperar solicitud.",
                "Compartir conocimientos y recursos con compañeros regularmente.",
                "Participar en reuniones de equipo aportando ideas constructivas.",
                "Reflexionar semanalmente sobre oportunidades perdidas de colaboración."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Colabora adecuadamente cuando es necesario. Comparte conocimientos básicos, armoniza intereses del grupo y contribuye a objetivos comunes de manera satisfactoria.",
            "plan": [
                "Incrementar la frecuencia de colaboración espontánea.",
                "Identificar y proponer mejoras en procesos que beneficien al equipo.",
                "Desarrollar habilidades de mediación en conflictos menores.",
                "Participar en proyectos transversales que requieran coordinación amplia.",
                "Mantener actitud constructiva incluso en situaciones de desacuerdo."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Excelente colaborador. Establece relaciones positivas, comparte conocimientos activamente, armoniza intereses y contribuye significativamente al logro de objetivos organizacionales.",
            "plan": [
                "Mantener y potenciar el nivel actual de colaboración.",
                "Asumir roles de coordinación en proyectos de equipo.",
                "Apoyar la integración de nuevos miembros del equipo.",
                "Proponer iniciativas que fortalezcan el trabajo colaborativo.",
                "Compartir mejores prácticas de trabajo en equipo con otros."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Referente excepcional en trabajo colaborativo. Genera sinergias, facilita coordinación, resuelve conflictos constructivamente y maximiza el potencial colectivo del equipo.",
            "plan": [
                "Continuar siendo modelo de trabajo colaborativo.",
                "Liderar iniciativas de mejoramiento del trabajo en equipo.",
                "Mentor de empleados con menor desarrollo en esta competencia.",
                "Facilitar espacios de integración y fortalecimiento de equipo.",
                "Documentar prácticas efectivas de colaboración para el área."
            ]
        }
    },

    "Mejora continua": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No muestra interés por mejorar procesos ni adaptarse a cambios. Se resiste a nuevas metodologías y no busca soluciones a problemas recurrentes. Su actitud obstaculiza la innovación.",
            "plan": [
                "Participar en capacitación obligatoria sobre mejora continua y metodologías ágiles.",
                "Establecer meta mensual de proponer al menos una pequeña mejora en su área.",
                "Acompañamiento semanal con supervisor para identificar oportunidades de mejora.",
                "Visitar otras áreas para conocer mejores prácticas aplicables.",
                "Comprometerse a implementar al menos un cambio sugerido por mes."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Acepta cambios cuando son obligatorios, pero no los promueve. Rara vez propone mejoras y requiere supervisión constante para adaptarse a nuevos estándares.",
            "plan": [
                "Estudiar casos de éxito de mejora continua en la organización.",
                "Identificar semanalmente un aspecto mejorable en su trabajo diario.",
                "Participar activamente en sesiones de lluvia de ideas.",
                "Documentar problemas recurrentes y proponer al menos una solución mensual.",
                "Solicitar retroalimentación sobre propuestas de mejora."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Acepta y se adapta a mejoras propuestas. Ocasionalmente sugiere modificaciones menores a procesos. Mantiene apertura moderada a la modernización de metodologías.",
            "plan": [
                "Incrementar frecuencia de propuestas de mejora (al menos 2 por mes).",
                "Participar en grupos de trabajo para optimización de procesos.",
                "Estudiar metodologías de mejora continua (Kaizen, Lean, etc.).",
                "Implementar ciclos PHVA (Planear-Hacer-Verificar-Actuar) en tareas propias.",
                "Compartir aprendizajes sobre mejoras implementadas con el equipo."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Proactivo en la búsqueda de mejoras. Identifica oportunidades, propone soluciones viables y se adapta rápidamente a cambios. Promueve modernización de procesos activamente.",
            "plan": [
                "Mantener actitud proactiva hacia la mejora continua.",
                "Liderar proyectos pequeños de optimización de procesos.",
                "Capacitar a compañeros en técnicas de identificación de desperdicios.",
                "Documentar mejoras implementadas y sus resultados.",
                "Explorar formación en metodologías avanzadas de mejora (Six Sigma, etc.)."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Agente de cambio excepcional. Lidera iniciativas de mejora, innova constantemente, facilita adaptación del equipo a cambios y genera cultura de mejora continua.",
            "plan": [
                "Continuar siendo referente en mejora continua.",
                "Liderar programa de innovación y mejora en el área.",
                "Mentor de otros empleados en técnicas de mejora continua.",
                "Presentar casos de éxito en foros organizacionales.",
                "Investigar tendencias y mejores prácticas del sector para implementar."
            ]
        }
    },

    # ======================== OBJETIVOS (40%) ========================

    "Apoyo a procesos de producción": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No cumple con las tareas básicas de cargue, descargue, clasificación y arrumado. El flujo de materiales se ve constantemente afectado por su desempeño deficiente. No colabora en mantenimiento del área.",
            "plan": [
                "Reentrenamiento urgente en procedimientos básicos de cargue, descargue y clasificación.",
                "Supervisión directa diaria por una semana para identificar brechas específicas.",
                "Establecer metas diarias claras y medibles para cada tarea.",
                "Asignación temporal a tareas simples hasta dominar procedimientos básicos.",
                "Evaluación semanal de desempeño con plan de acción correctivo."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Cumple parcialmente con las tareas asignadas. Realiza cargue y descargue con lentitud o errores frecuentes. La clasificación y arrumado requieren corrección constante. No garantiza flujo adecuado.",
            "plan": [
                "Capacitación específica en técnicas de clasificación y arrumado eficiente.",
                "Practicar bajo supervisión hasta alcanzar velocidad y precisión estándar.",
                "Implementar checklist de verificación para cada actividad.",
                "Participar en mantenimiento del área al menos 2 veces por semana.",
                "Solicitar retroalimentación diaria sobre calidad y velocidad de trabajo."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Realiza satisfactoriamente el cargue, descargue, clasificación y arrumado de madera. Colabora en mantenimiento básico del área. Asegura flujo aceptable de materiales, aunque puede mejorar eficiencia.",
            "plan": [
                "Optimizar tiempos de cargue/descargue mediante técnicas más eficientes.",
                "Mejorar precisión en clasificación para reducir errores al mínimo.",
                "Proponer mejoras en el arrumado para maximizar espacio y accesibilidad.",
                "Participar activamente en mantenimiento preventivo del área.",
                "Documentar procedimientos efectivos para compartir con compañeros."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Desempeño destacado en todas las operaciones de producción. Realiza cargue, descargue, clasificación y arrumado con alta eficiencia y precisión. Garantiza flujo constante y colabora proactivamente en mantenimiento.",
            "plan": [
                "Mantener estándares de excelencia en todas las operaciones.",
                "Entrenar a compañeros nuevos o con menor desempeño.",
                "Proponer e implementar mejoras en layout y organización del área.",
                "Asumir responsabilidades adicionales en coordinación de flujos.",
                "Participar en definición de mejores prácticas para el área."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Desempeño excepcional y ejemplar. Máxima eficiencia en cargue, descargue, clasificación y arrumado. Anticipa problemas, optimiza flujos, mantiene área impecable y es referente para todo el equipo.",
            "plan": [
                "Continuar siendo modelo de excelencia operativa.",
                "Liderar programa de estandarización de mejores prácticas.",
                "Mentor principal de nuevos auxiliares de procesos.",
                "Participar en diseño de mejoras de layout y procesos productivos.",
                "Representar al área en comités de productividad y mejora."
            ]
        }
    },

    # ======================== COMPETENCIAS INTERPERSONALES (25%) ========================

    "Trabajo en equipo colaborativo": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No colabora efectivamente con compañeros de otras áreas. Su comportamiento obstaculiza objetivos comunes y genera conflictos interpersonales. No orienta ni apoya el trabajo de pares.",
            "plan": [
                "Participar en talleres de integración y resolución de conflictos.",
                "Establecer compromisos semanales de colaboración con al menos 3 áreas diferentes.",
                "Recibir coaching sobre habilidades interpersonales y colaboración.",
                "Practicar técnicas de empatía y comunicación asertiva.",
                "Evaluación semanal de comportamiento colaborativo con supervisor."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Colabora mínimamente y solo cuando se le solicita. Poca iniciativa para apoyar a otras áreas u orientar compañeros. El intercambio con pares es limitado y poco efectivo.",
            "plan": [
                "Incrementar participación en actividades inter-áreas voluntariamente.",
                "Ofrecer ayuda proactivamente al menos una vez al día a otros equipos.",
                "Participar en rotaciones o proyectos que requieran colaboración amplia.",
                "Desarrollar habilidades de mentoring con compañeros nuevos.",
                "Solicitar retroalimentación sobre calidad de colaboración brindada."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Colabora adecuadamente con otras áreas cuando es necesario. Promueve intercambio básico de información y orienta ocasionalmente el trabajo de pares hacia la estrategia organizacional.",
            "plan": [
                "Fortalecer comunicación proactiva con áreas relacionadas.",
                "Incrementar frecuencia de orientación a compañeros menos experimentados.",
                "Participar en iniciativas transversales de mejora.",
                "Desarrollar mayor comprensión de objetivos de otras áreas.",
                "Proponer mejoras en coordinación inter-áreas."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Excelente colaborador inter-áreas. Promueve activamente el intercambio y coordina efectivamente con otros equipos. Orienta frecuentemente a pares alineando con estrategia organizacional.",
            "plan": [
                "Mantener nivel de colaboración inter-áreas.",
                "Facilitar sesiones de coordinación entre equipos.",
                "Mentor de empleados en desarrollo de habilidades colaborativas.",
                "Proponer e implementar proyectos de integración entre áreas.",
                "Documentar mejores prácticas de colaboración organizacional."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Referente excepcional en colaboración organizacional. Genera sinergias entre áreas, facilita comunicación efectiva, orienta estratégicamente a todo el equipo y maximiza resultados colectivos.",
            "plan": [
                "Continuar siendo modelo de colaboración organizacional.",
                "Liderar programa de integración y trabajo colaborativo.",
                "Participar en comités estratégicos inter-áreas.",
                "Desarrollar materiales de capacitación sobre colaboración efectiva.",
                "Representar al área en instancias de coordinación corporativa."
            ]
        }
    },

    "Dinamismo": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "Responde muy lentamente y sin agilidad a tareas físicas. No mantiene el ritmo de trabajo requerido y afecta negativamente la productividad del área.",
            "plan": [
                "Evaluación de condiciones físicas y ergonómicas del puesto.",
                "Establecer metas graduales de incremento de velocidad de trabajo.",
                "Capacitación en técnicas de trabajo eficiente y manejo de cargas.",
                "Supervisión directa para identificar causas de lentitud.",
                "Implementar rutinas de acondicionamiento físico si es necesario."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Responde con lentitud en algunas tareas físicas. Requiere mejorar agilidad para alcanzar los estándares de productividad esperados.",
            "plan": [
                "Practicar técnicas de economía de movimiento para mayor eficiencia.",
                "Establecer metas diarias de tiempo por tarea para mejorar velocidad.",
                "Recibir coaching sobre organización de secuencias de trabajo.",
                "Identificar y eliminar movimientos innecesarios.",
                "Monitorear progreso semanal en tiempos de ejecución."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Responde con agilidad aceptable a tareas físicas. Cumple con los ritmos de trabajo esperados, aunque puede optimizar algunos movimientos.",
            "plan": [
                "Continuar manteniendo ritmo de trabajo actual.",
                "Identificar oportunidades de optimización de movimientos.",
                "Practicar técnicas avanzadas de manejo eficiente de materiales.",
                "Participar en estudios de tiempos y movimientos del área.",
                "Compartir técnicas efectivas con compañeros."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Demuestra alta agilidad y respuesta rápida en tareas físicas. Supera consistentemente los estándares de productividad del área.",
            "plan": [
                "Mantener nivel de agilidad y eficiencia actual.",
                "Entrenar a compañeros en técnicas de trabajo ágil.",
                "Participar en diseño de mejores prácticas de manejo de materiales.",
                "Proponer mejoras ergonómicas para el área.",
                "Servir como referencia en estudios de tiempos estándar."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Agilidad excepcional en tareas físicas. Máxima eficiencia en respuesta y ejecución. Marca el estándar de excelencia en dinamismo para el área.",
            "plan": [
                "Continuar siendo modelo de eficiencia y agilidad.",
                "Liderar programa de optimización de movimientos en el área.",
                "Mentor principal en técnicas de trabajo ágil y eficiente.",
                "Participar en diseño de estándares de productividad.",
                "Representar al área en competencias o demostraciones de eficiencia."
            ]
        }
    },

    "Responsabilidad": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No promueve el logro de objetivos corporativos ni mantiene ambiente laboral adecuado. No demuestra preocupación por la calidad ni precisión de las tareas. Su actitud afecta resultados y clima.",
            "plan": [
                "Establecer compromisos claros y medibles sobre responsabilidades básicas.",
                "Supervisión directa diaria con retroalimentación inmediata.",
                "Capacitación sobre responsabilidad laboral y sentido de pertenencia.",
                "Implementar sistema de autoevaluación diaria de cumplimiento.",
                "Reuniones semanales de seguimiento con supervisor para evaluar progreso."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Cumple responsabilidades básicas pero con inconsistencias. Poca preocupación proactiva por calidad y ambiente laboral. Requiere supervisión frecuente para asegurar cumplimiento.",
            "plan": [
                "Desarrollar mayor conciencia sobre impacto de sus acciones en resultados.",
                "Establecer checklist de verificación de calidad para cada tarea.",
                "Participar en espacios de reflexión sobre cultura organizacional.",
                "Mejorar comunicación proactiva sobre problemas o dificultades.",
                "Solicitar retroalimentación semanal sobre nivel de responsabilidad demostrado."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Promueve adecuadamente los objetivos corporativos y mantiene ambiente laboral aceptable. Demuestra preocupación por realizar tareas con precisión y calidad satisfactoria.",
            "plan": [
                "Incrementar iniciativa en promoción de objetivos organizacionales.",
                "Fortalecer compromiso con mejora continua de calidad.",
                "Participar más activamente en actividades de ambiente laboral.",
                "Desarrollar mayor autonomía en aseguramiento de calidad.",
                "Proponer iniciativas que fortalezcan cultura de responsabilidad."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Altamente responsable. Promueve activamente objetivos corporativos, mantiene excelente ambiente laboral y demuestra constante preocupación por calidad, precisión y contribución al éxito organizacional.",
            "plan": [
                "Mantener nivel de responsabilidad y compromiso actual.",
                "Servir como modelo de comportamiento responsable para el equipo.",
                "Participar en comités de calidad o mejora organizacional.",
                "Mentor de empleados en desarrollo de responsabilidad laboral.",
                "Liderar iniciativas que fortalezcan cultura de excelencia."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Responsabilidad ejemplar y excepcional. Líder en promoción de objetivos, genera ambiente laboral positivo, máxima calidad y precisión. Verdadero agente de éxito organizacional.",
            "plan": [
                "Continuar siendo referente de responsabilidad y excelencia.",
                "Liderar programa de cultura organizacional en el área.",
                "Participar en comités estratégicos de calidad y ambiente laboral.",
                "Desarrollar materiales de capacitación sobre responsabilidad corporativa.",
                "Representar al área como embajador de cultura organizacional."
            ]
        }
    },

    # ======================== COMPETENCIAS TÉCNICAS (20%) ========================

    "Clasificación de madera": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No clasifica correctamente la madera por diámetro, longitud y calidad. Errores frecuentes y graves que afectan significativamente el proceso productivo y causan pérdidas.",
            "plan": [
                "Reentrenamiento completo en técnicas de clasificación de madera.",
                "Supervisión directa constante hasta demostrar competencia básica.",
                "Practicar con muestras supervisadas antes de trabajar en línea.",
                "Estudiar especificaciones técnicas de clasificación del área.",
                "Evaluación práctica semanal con retroalimentación inmediata."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Clasifica con errores frecuentes. Confunde especificaciones o no aplica criterios consistentemente. Requiere verificación constante de su trabajo.",
            "plan": [
                "Capacitación adicional en criterios de clasificación específicos.",
                "Implementar checklist de verificación para cada lote.",
                "Practicar identificación visual con retroalimentación inmediata.",
                "Revisar casos de error para identificar patrones.",
                "Solicitar verificación de supervisor hasta mejorar precisión."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Selecciona y clasifica correctamente la madera en la mayoría de casos. Aplica criterios de diámetro, longitud y calidad satisfactoriamente, con errores ocasionales menores.",
            "plan": [
                "Reducir errores al mínimo mediante mayor concentración.",
                "Estudiar casos complejos o borderline con supervisor.",
                "Participar en estandarización de criterios de clasificación.",
                "Proponer mejoras en sistema de clasificación si identifica oportunidades.",
                "Compartir tips de clasificación con compañeros nuevos."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Excelente precisión en clasificación. Aplica criterios técnicos correctamente, identifica casos especiales y mantiene consistencia. Muy pocos errores y de impacto mínimo.",
            "plan": [
                "Mantener nivel de precisión actual.",
                "Entrenar a nuevos empleados en clasificación de madera.",
                "Participar en definición o actualización de criterios de clasificación.",
                "Apoyar en auditorías de calidad de clasificación.",
                "Documentar mejores prácticas y casos especiales."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Experto en clasificación de madera. Precisión excepcional, identifica casos complejos correctamente, referente técnico del área. Cero errores significativos.",
            "plan": [
                "Continuar siendo experto técnico en clasificación.",
                "Liderar programa de entrenamiento en clasificación.",
                "Participar en desarrollo de estándares de clasificación.",
                "Auditor principal de calidad de clasificación.",
                "Representar al área en comités técnicos de calidad."
            ]
        }
    },

    "Orden y aseo": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No mantiene el puesto de trabajo ordenado ni libre de materiales y herramientas en desuso. Genera desorden constante que afecta seguridad y productividad del área.",
            "plan": [
                "Capacitación obligatoria en metodología 5S.",
                "Asignar 15 minutos diarios exclusivos para orden y aseo de puesto.",
                "Supervisión diaria de estado del puesto con retroalimentación.",
                "Implementar sistema de etiquetado y ubicación fija de herramientas.",
                "Evaluación semanal con checklist de orden y limpieza."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Orden y limpieza inconsistentes. Acumula materiales innecesarios ocasionalmente y requiere recordatorios frecuentes para mantener área organizada.",
            "plan": [
                "Reforzar hábitos de orden mediante rutina diaria establecida.",
                "Implementar sistema personal de clasificación de materiales.",
                "Participar en jornadas de 5S del área activamente.",
                "Solicitar retroalimentación semanal sobre estado del puesto.",
                "Comprometerse a dejar área ordenada al final de cada jornada."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Mantiene generalmente el puesto de trabajo libre de materiales y herramientas en desuso. Cumple estándares básicos de orden y limpieza la mayor parte del tiempo.",
            "plan": [
                "Fortalecer consistencia en orden y limpieza al 100%.",
                "Implementar mejoras en organización de herramientas y materiales.",
                "Proponer optimizaciones en layout del puesto de trabajo.",
                "Participar en auditorías de 5S del área.",
                "Apoyar a compañeros en mantenimiento de orden."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Excelente orden y limpieza. Puesto de trabajo consistentemente organizado, libre de materiales innecesarios. Aplica disciplina de 5S y sirve de ejemplo al equipo.",
            "plan": [
                "Mantener estándares de orden y limpieza actuales.",
                "Ser auditor de 5S para el área.",
                "Entrenar a compañeros en técnicas de orden y organización.",
                "Proponer mejoras en sistemas de organización del área.",
                "Liderar jornadas de orden y aseo."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Puesto de trabajo modelo. Orden impecable, aplicación ejemplar de 5S, optimización constante de organización. Referente de disciplina y limpieza para toda el área.",
            "plan": [
                "Continuar siendo modelo de excelencia en 5S.",
                "Liderar programa de 5S del área o planta.",
                "Desarrollar estándares visuales de orden y limpieza.",
                "Capacitador principal en metodología 5S.",
                "Representar al área en auditorías corporativas de 5S."
            ]
        }
    },

    "Apoyo al proceso": {
        1: {
            "titulo": "🔴 Muy bajo (1) - Requiere mejora urgente",
            "recomendacion": "No demuestra disponibilidad ni eficiencia en cargue, descargue y arrumado de paquetes. Genera retrasos constantes y no represa la salida de máquina, afectando gravemente la productividad.",
            "plan": [
                "Reentrenamiento urgente en secuencias y tiempos de operación.",
                "Supervisión directa para identificar causas de ineficiencia.",
                "Establecer metas de tiempo por operación con seguimiento diario.",
                "Capacitación en técnicas de manejo eficiente de materiales.",
                "Evaluación semanal de disponibilidad y eficiencia con plan correctivo."
            ]
        },
        2: {
            "titulo": "🟠 Bajo (2) - Necesita desarrollo",
            "recomendacion": "Disponibilidad y eficiencia limitadas. Cumple operaciones lentamente o con errores que ocasionalmente afectan flujo de producción y generan represamiento.",
            "plan": [
                "Mejorar velocidad mediante práctica supervisada de movimientos.",
                "Implementar técnicas de economía de movimiento.",
                "Coordinar mejor con operadores de máquina para sincronizar tiempos.",
                "Establecer rutinas para prevenir represamiento.",
                "Monitorear progreso semanal en tiempos de ciclo."
            ]
        },
        3: {
            "titulo": "🟡 Moderado (3) - Cumple lo esperado",
            "recomendacion": "Disponibilidad y eficiencia aceptables en cargue, descargue y arrumado. Generalmente evita represamiento de salida de máquina, aunque puede mejorar sincronización.",
            "plan": [
                "Optimizar tiempos para eliminar completamente represamiento.",
                "Mejorar coordinación con operadores de máquina.",
                "Identificar y eliminar tiempos muertos en el ciclo.",
                "Proponer mejoras en secuencia de operaciones.",
                "Mantener comunicación proactiva sobre necesidades de apoyo."
            ]
        },
        4: {
            "titulo": "🟢 Alto (4) - Supera expectativas",
            "recomendacion": "Alta disponibilidad y eficiencia. Realiza cargue, descargue y arrumado con velocidad y precisión. Previene represamiento efectivamente y optimiza flujo de producción.",
            "plan": [
                "Mantener nivel de eficiencia y disponibilidad actual.",
                "Entrenar a compañeros en técnicas de trabajo eficiente.",
                "Proponer mejoras en secuencias de operación.",
                "Participar en estudios de tiempos y métodos.",
                "Servir como referencia en sincronización de operaciones."
            ]
        },
        5: {
            "titulo": "⭐ Muy alto (5) - Excelencia",
            "recomendacion": "Disponibilidad y eficiencia excepcionales. Máxima velocidad y precisión, sincronización perfecta, cero represamiento. Marca el estándar de excelencia en apoyo al proceso.",
            "plan": [
                "Continuar siendo modelo de eficiencia operativa.",
                "Liderar programa de optimización de apoyo a procesos.",
                "Definir estándares de tiempo y método para el área.",
                "Mentor principal en técnicas de trabajo eficiente.",
                "Participar en diseño de mejoras de layout y flujo productivo."
            ]
        }
    }
}

# ===================== FUNCIONES ESPECÍFICAS PARA AUXILIAR DE PROCESOS =====================

def calcular_puntaje_ponderado_auxiliar_procesos(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado para la evaluación de Auxiliares de Procesos
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

    # Mapeo de preguntas a categorías (10 preguntas)
    mapeo_preguntas_categorias = {
        "Comunicación": "Competencias Organizacionales",
        "Trabajo en equipo": "Competencias Organizacionales",
        "Mejora continua": "Competencias Organizacionales",
        "Apoyo a procesos de producción": "Objetivos",
        "Trabajo en equipo colaborativo": "Competencias Interpersonales",
        "Dinamismo": "Competencias Interpersonales",
        "Responsabilidad": "Competencias Interpersonales",
        "Clasificación": "Competencias Técnicas",
        "Orden y aseo": "Competencias Técnicas",
        "Apoyo al proceso": "Competencias Técnicas"
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

def generar_plan_mejora_auxiliar_procesos(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Auxiliares de Procesos
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
║                        AUXILIAR DE PROCESOS                                  ║
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
        for competencia_key in RESPUESTAS_AUXILIAR_PROCESOS.keys():
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
            if competencia_encontrada in RESPUESTAS_AUXILIAR_PROCESOS and puntuacion in RESPUESTAS_AUXILIAR_PROCESOS[competencia_encontrada]:
                datos_plan = RESPUESTAS_AUXILIAR_PROCESOS[competencia_encontrada][puntuacion]

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
    return puntaje_porcentaje < 91

def crear_seguimientos_bimensuales_auxiliar(plan_mejora):
    """
    Crea seguimientos bimensuales para evaluación de Auxiliar de Procesos.
    Reutiliza la función genérica de seguimientos.

    Args:
        plan_mejora: Instancia de PlanMejoraPredefinido
    """
    from ..utils.respuestas_predefinidas import crear_seguimientos_bimensuales
    return crear_seguimientos_bimensuales(plan_mejora)
