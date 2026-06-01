"""
Respuestas predefinidas y lógica de evaluación para Directores
Sistema de calificación: Escala 1-5 (Muy bajo a Muy alto)
Total de competencias: 12
Ponderación por categorías:
  - Competencias Organizacionales (10%): Preguntas 1-3
  - Objetivos (40%): Pregunta 4
  - Competencias Interpersonales (25%): Preguntas 5-8
  - Competencias Técnicas (25%): Preguntas 9-12
"""

# =====================================================================
# COMPETENCIAS ORGANIZACIONALES (10%)
# =====================================================================

COMUNICACION_DIRECTOR = {
    'pregunta': 'COMUNICACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** La comunicación directiva es deficiente. No transmite efectivamente la estrategia ni visión del área. Genera confusión en el equipo y otras direcciones. **Acción requerida:** Mejora urgente en comunicación directiva.',
            'plan_mejora': 'Capacitación en comunicación ejecutiva. Estructurar mensajes claros en comités directivos. Implementar comunicación regular con el equipo sobre estrategia y objetivos.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La comunicación es básica pero insuficiente para el nivel directivo. Falta claridad en la transmisión de estrategia. Debe mejorar articulación con otras direcciones y alta gerencia.',
            'plan_mejora': 'Desarrollar habilidades de comunicación estratégica. Practicar presentaciones ejecutivas. Establecer canales de comunicación efectivos con stakeholders.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Comunica adecuadamente con el equipo directivo y gerencia. La transmisión de estrategia es generalmente clara. **Oportunidad:** Mayor impacto en comunicación con alta dirección y junta.',
            'plan_mejora': 'Perfeccionar comunicación ejecutiva de alto impacto. Desarrollar storytelling estratégico. Fortalecer presentaciones a junta directiva.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Comunica efectivamente visión y estrategia. Articula claramente objetivos al equipo. Mantiene comunicación fluida con gerencia y pares directivos. **Fortaleza reconocida:** Comunicador directivo efectivo.',
            'plan_mejora': 'Mantener excelencia comunicativa. Liderar comunicación de cambios organizacionales. Ser vocero del área en foros estratégicos.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente comunicador a nivel directivo. Inspira y alinea al equipo con la visión organizacional. Es referente en comunicación estratégica. **Fortaleza destacada:** Líder comunicacional.',
            'plan_mejora': 'Mantener excelencia. Desarrollar programa de comunicación organizacional. Mentorear a otros directores en comunicación ejecutiva.'
        }
    }
}

TRABAJO_EQUIPO_DIRECTOR = {
    'pregunta': 'TRABAJO EN EQUIPO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No trabaja efectivamente con el equipo directivo. Genera silos entre áreas. No comparte recursos ni conocimiento. **Acción requerida:** Desarrollar competencias colaborativas a nivel directivo urgentemente.',
            'plan_mejora': 'Participar activamente en comités directivos. Desarrollar proyectos transversales. Compartir recursos y mejores prácticas entre áreas.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El trabajo colaborativo con otras direcciones es limitado. Falta integración interdireccional. **Recomendación:** Fortalecer trabajo en equipo a nivel directivo.',
            'plan_mejora': 'Liderar iniciativas interdireccionales. Fomentar sinergias entre áreas. Participar proactivamente en comités estratégicos.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Trabaja adecuadamente con el equipo directivo. Colabora en proyectos estratégicos. **Oportunidad:** Mayor proactividad en generación de sinergias organizacionales.',
            'plan_mejora': 'Liderar proyectos transformacionales inter-áreas. Crear alianzas estratégicas internas. Compartir recursos de manera estratégica.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente colaboración directiva. Genera sinergias efectivas entre áreas. Contribuye activamente a objetivos organizacionales. **Fortaleza reconocida:** Líder colaborativo.',
            'plan_mejora': 'Mantener alto nivel de colaboración. Liderar comités estratégicos transversales. Ser facilitador de integración organizacional.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Líder excepcional en trabajo colaborativo. Genera alta integración y sinergias. Eleva el desempeño del equipo directivo completo. **Fortaleza destacada:** Integrador organizacional.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación cultural de colaboración. Diseñar modelo de gestión integrada para la organización.'
        }
    }
}

MEJORA_CONTINUA_DIRECTOR = {
    'pregunta': 'MEJORA CONTINUA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No impulsa mejora continua en el área. Mantiene procesos obsoletos. No promueve innovación. **Acción requerida:** Desarrollar cultura de mejora continua urgentemente.',
            'plan_mejora': 'Capacitación en transformación y mejora de procesos. Establecer KPIs de innovación. Liderar proyecto piloto de mejora en el área.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El enfoque de mejora continua es reactivo. Pocos proyectos de optimización en el área. **Recomendación:** Fortalecer liderazgo en mejora e innovación.',
            'plan_mejora': 'Implementar metodologías de mejora continua. Establecer comité de innovación del área. Benchmarking con mejores prácticas del sector.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Promueve mejora continua en el área. Implementa algunas optimizaciones. **Oportunidad:** Liderar transformación significativa del área.',
            'plan_mejora': 'Desarrollar plan de transformación del área. Implementar metodologías ágiles. Crear cultura de innovación en el equipo.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Lidera activamente mejora continua. Ha optimizado procesos clave. Promueve innovación efectivamente. **Fortaleza reconocida:** Agente de cambio.',
            'plan_mejora': 'Mantener liderazgo en mejora. Escalar mejores prácticas a toda la organización. Liderar transformación digital del área.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelencia en liderazgo de mejora continua. Ha transformado significativamente el área. Referente de innovación organizacional. **Fortaleza destacada:** Líder transformacional.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación organizacional. Diseñar sistema de gestión de innovación corporativa.'
        }
    }
}

# =====================================================================
# OBJETIVOS - EL HACER (40%)
# =====================================================================

OBJETIVOS_DIRECTOR = {
    'pregunta': 'OBJETIVOS - GESTIÓN DIRECTIVA ESTRATÉGICA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Desempeño crítico:** No cumple objetivos estratégicos del área. La gestión de recursos es deficiente. No desarrolla efectivamente al equipo. El área no está alineada con la estrategia organizacional. **Acción urgente:** Plan de acción directivo inmediato.',
            'plan_mejora': 'Establecer plan de choque para cumplimiento de objetivos. Coaching directivo intensivo. Revisión y ajuste de estrategia del área. Establecer seguimiento semanal con superior.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Cumple parcialmente objetivos estratégicos (<70%). La gestión de recursos tiene deficiencias. El desarrollo del equipo es limitado. **Recomendación:** Fortalecer capacidades de gestión directiva.',
            'plan_mejora': 'Curso de dirección estratégica. Implementar tablero de control balanceado. Mejorar planificación de recursos. Establecer plan de desarrollo del equipo directivo.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Cumple satisfactoriamente objetivos estratégicos (70-90%). Gestiona adecuadamente recursos. Desarrolla el equipo apropiadamente. El área está generalmente alineada. **Oportunidad:** Excelencia en ejecución estratégica.',
            'plan_mejora': 'Perfeccionar ejecución estratégica. Optimizar asignación de recursos. Implementar programa avanzado de desarrollo de talento. Fortalecer alineación con visión corporativa.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Cumple o supera objetivos estratégicos (90-110%). Gestiona eficientemente recursos. Desarrolla efectivamente al equipo. El área está alineada con la estrategia organizacional. **Fortaleza reconocida:** Director efectivo.',
            'plan_mejora': 'Mantener alto desempeño. Liderar proyectos estratégicos corporativos. Desarrollar próxima generación de líderes. Expandir alcance del área.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Supera consistentemente objetivos estratégicos (+110%). Optimiza recursos generando valor superior. Desarrolla talento de alto nivel. El área es referente de excelencia organizacional. **Fortaleza destacada:** Excelencia directiva.',
            'plan_mejora': 'Mantener excelencia. Asumir responsabilidades corporativas adicionales. Liderar transformación estratégica organizacional. Mentorear a otros directores.'
        }
    }
}

# =====================================================================
# COMPETENCIAS INTERPERSONALES - EL SER (25%)
# =====================================================================

LIDERAZGO_ESTRATEGICO_DIRECTOR = {
    'pregunta': 'LIDERAZGO ESTRATÉGICO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No ejerce liderazgo estratégico efectivo. No comunica visión clara. El equipo no está movilizado hacia objetivos. **Acción requerida:** Desarrollar competencias de liderazgo urgentemente.',
            'plan_mejora': 'Coaching ejecutivo en liderazgo. Definir y comunicar visión clara del área. Implementar sistema de seguimiento de objetivos con el equipo.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El liderazgo estratégico es limitado. La visión del área no es suficientemente clara. El seguimiento de objetivos es irregular. **Recomendación:** Fortalecer liderazgo directivo.',
            'plan_mejora': 'Programa de desarrollo de liderazgo estratégico. Articular y comunicar visión inspiradora. Establecer rutina de seguimiento sistemático con el equipo.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Ejerce liderazgo estratégico adecuadamente. Comunica visión satisfactoriamente. Hace seguimiento de objetivos. **Oportunidad:** Inspirar al equipo hacia desempeño superior.',
            'plan_mejora': 'Desarrollar liderazgo inspiracional. Perfeccionar comunicación de estrategia. Implementar sistema de reconocimiento de logros del equipo.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Ejerce liderazgo estratégico sólido. Comunica visión clara e inspiradora. Hace seguimiento efectivo y reconoce logros. **Fortaleza reconocida:** Líder estratégico.',
            'plan_mejora': 'Mantener liderazgo efectivo. Desarrollar líderes en cascada en el área. Ampliar impacto del liderazgo a otras áreas.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Liderazgo estratégico excepcional. Inspira y moviliza equipos de alto desempeño. Es referente de liderazgo organizacional. **Fortaleza destacada:** Líder transformacional.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de desarrollo de liderazgo organizacional. Ser mentor de directores y gerentes senior.'
        }
    }
}

PENSAMIENTO_ESTRATEGICO_DIRECTOR = {
    'pregunta': 'PENSAMIENTO ESTRATÉGICO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Pensamiento estratégico muy limitado. No identifica riesgos ni oportunidades. Las decisiones son principalmente reactivas. **Acción requerida:** Desarrollar capacidad estratégica urgentemente.',
            'plan_mejora': 'Capacitación en pensamiento estratégico y análisis de entorno. Participar en comités de planeación estratégica. Implementar análisis FODA trimestral del área.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El pensamiento estratégico es básico. Identifica algunos riesgos y oportunidades pero de manera limitada. **Recomendación:** Fortalecer visión estratégica de largo plazo.',
            'plan_mejora': 'Desarrollar habilidades de análisis de entorno. Implementar planeación estratégica del área. Benchmarking estratégico con competidores.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Demuestra pensamiento estratégico adecuado. Identifica riesgos y oportunidades principales. Diseña planes estratégicos satisfactorios. **Oportunidad:** Anticipación proactiva de escenarios futuros.',
            'plan_mejora': 'Perfeccionar análisis de escenarios. Desarrollar planes estratégicos robustos. Implementar sistema de vigilancia de tendencias del sector.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Pensamiento estratégico sólido. Anticipa efectivamente riesgos y oportunidades. Diseña estrategias que generan ventajas competitivas. **Fortaleza reconocida:** Estratega efectivo.',
            'plan_mejora': 'Mantener capacidad estratégica. Liderar planeación estratégica corporativa. Desarrollar modelos de análisis predictivo para el área.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Pensamiento estratégico excepcional. Anticipa tendencias y diseña estrategias disruptivas. Es referente estratégico organizacional. **Fortaleza destacada:** Visionario estratégico.',
            'plan_mejora': 'Mantener excelencia. Liderar definición de estrategia corporativa. Desarrollar capacidades de inteligencia competitiva organizacional.'
        }
    }
}

TOMA_DECISIONES_DIRECTOR = {
    'pregunta': 'TOMA DE DECISIONES BAJO PRESIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Dificultad significativa para tomar decisiones bajo presión. Análisis paralizante o decisiones apresuradas. No asume responsabilidad. **Acción requerida:** Desarrollar competencia crítica urgentemente.',
            'plan_mejora': 'Coaching en toma de decisiones ejecutivas. Practicar análisis de decisiones con casos de estudio. Implementar matriz de toma de decisiones.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La toma de decisiones bajo presión es limitada. Requiere mucho tiempo o evita decisiones difíciles. **Recomendación:** Fortalecer criterio y velocidad decisional.',
            'plan_mejora': 'Desarrollar habilidades de decisión bajo incertidumbre. Practicar análisis rápido riesgo-beneficio. Establecer framework de toma de decisiones.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Toma decisiones adecuadamente bajo presión. Balancea análisis y velocidad satisfactoriamente. Asume responsabilidad. **Oportunidad:** Mayor agilidad en decisiones críticas.',
            'plan_mejora': 'Perfeccionar análisis de información crítica. Desarrollar confianza en intuición directiva. Implementar post-mortem de decisiones clave.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Toma decisiones efectivas bajo presión. Balancea análisis, velocidad y criterio. Asume responsabilidad consistentemente. **Fortaleza reconocida:** Decisor efectivo.',
            'plan_mejora': 'Mantener efectividad decisional. Mentorear a gerentes en toma de decisiones. Liderar situaciones críticas organizacionales.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelencia en toma de decisiones bajo presión. Decisiones acertadas con información limitada. Referente en gestión de crisis. **Fortaleza destacada:** Líder en crisis.',
            'plan_mejora': 'Mantener excelencia. Liderar comité de gestión de crisis organizacional. Desarrollar protocolo de toma de decisiones críticas.'
        }
    }
}

DESARROLLO_PERSONAS_DIRECTOR = {
    'pregunta': 'DESARROLLO DE PERSONAS',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No desarrolla efectivamente al equipo. No identifica potencial. Retroalimentación inexistente o inadecuada. No promueve crecimiento. **Acción requerida:** Priorizar desarrollo de talento urgentemente.',
            'plan_mejora': 'Capacitación en desarrollo de talento y coaching. Implementar reuniones 1-a-1 con equipo directo. Establecer planes de desarrollo individual.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El desarrollo del equipo es limitado. Identifica potencial básicamente. Retroalimentación ocasional. **Recomendación:** Fortalecer competencia de desarrollo de personas.',
            'plan_mejora': 'Desarrollar habilidades de coaching directivo. Implementar sistema de evaluación de desempeño. Crear planes de sucesión para posiciones clave.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Desarrolla adecuadamente al equipo. Identifica potencial satisfactoriamente. Brinda retroalimentación constructiva. **Oportunidad:** Crear pipeline de talento de alto potencial.',
            'plan_mejora': 'Perfeccionar técnicas de desarrollo de talento. Implementar programa de mentoring en el área. Crear plan de sucesión robusto.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Desarrolla efectivamente al equipo. Identifica y potencia talentos. Brinda retroalimentación continua y constructiva. **Fortaleza reconocida:** Desarrollador de talento.',
            'plan_mejora': 'Mantener enfoque en desarrollo. Crear academia interna del área. Liderar programa de desarrollo de líderes organizacional.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelencia en desarrollo de personas. Forma líderes de alto nivel. Genera pipeline robusto de talento. **Fortaleza destacada:** Constructor de equipos de excelencia.',
            'plan_mejora': 'Mantener excelencia. Liderar estrategia de gestión de talento organizacional. Ser mentor de directores en desarrollo de equipos.'
        }
    }
}

# =====================================================================
# COMPETENCIAS TÉCNICAS - EL SABER (25%)
# =====================================================================

GESTION_FINANCIERA_DIRECTOR = {
    'pregunta': 'GESTIÓN FINANCIERA Y PRESUPUESTAL',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Gestión financiera muy deficiente. Presupuesto mal controlado. Decisiones sin análisis financiero. Sobrecostos frecuentes. **Acción requerida:** Desarrollar competencia financiera urgentemente.',
            'plan_mejora': 'Capacitación intensiva en gestión financiera para no financieros. Apoyo de contraloría para control presupuestal. Implementar tablero de control financiero.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Gestión financiera básica. Control presupuestal con deficiencias. Toma decisiones con análisis financiero limitado. **Recomendación:** Fortalecer competencias financieras.',
            'plan_mejora': 'Curso de finanzas para directivos. Implementar seguimiento mensual de presupuesto. Desarrollar análisis costo-beneficio para decisiones.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Gestión financiera adecuada. Controla presupuesto satisfactoriamente. Toma decisiones considerando indicadores financieros. **Oportunidad:** Optimización de rentabilidad del área.',
            'plan_mejora': 'Perfeccionar análisis financiero. Implementar presupuesto base cero. Desarrollar modelo de optimización de recursos del área.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Sólida gestión financiera. Controla y optimiza presupuesto efectivamente. Decisiones basadas en análisis financiero robusto. **Fortaleza reconocida:** Gestor financiero efectivo.',
            'plan_mejora': 'Mantener disciplina financiera. Liderar proyectos de optimización de costos. Desarrollar business cases para iniciativas estratégicas.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelencia en gestión financiera. Optimiza presupuesto generando valor significativo. Decisiones financieras ejemplares. **Fortaleza destacada:** Director financieramente astuto.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación de gestión financiera organizacional. Desarrollar modelos de rentabilidad corporativos.'
        }
    }
}

PLANIFICACION_ESTRATEGICA_DIRECTOR = {
    'pregunta': 'PLANIFICACIÓN ESTRATÉGICA Y OPERATIVA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Planificación muy deficiente. No define objetivos ni indicadores claros. Planes de acción inexistentes o inadecuados. **Acción requerida:** Implementar sistema de planeación urgentemente.',
            'plan_mejora': 'Capacitación en planeación estratégica. Implementar metodología OKR o Balanced Scorecard. Establecer plan estratégico del área con indicadores.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Planificación básica. Objetivos poco claros. Indicadores limitados. Planes de acción genéricos. **Recomendación:** Fortalecer sistema de planeación.',
            'plan_mejora': 'Desarrollar competencias en planeación estratégica. Definir objetivos SMART. Implementar tablero de indicadores del área.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Planificación adecuada. Define objetivos e indicadores satisfactoriamente. Planes de acción viables. **Oportunidad:** Planificación estratégica de largo plazo más robusta.',
            'plan_mejora': 'Perfeccionar metodología de planeación. Implementar roadmap a 3-5 años. Desarrollar plan de contingencia para riesgos clave.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Planificación sólida. Objetivos e indicadores claros y retadores. Planes de acción robustos de corto, mediano y largo plazo. **Fortaleza reconocida:** Planificador estratégico.',
            'plan_mejora': 'Mantener excelencia en planeación. Liderar proceso de planeación estratégica corporativa. Implementar agilidad estratégica.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelencia en planeación estratégica. Objetivos ambiciosos y claros. Planes integrales que guían exitosamente al área. **Fortaleza destacada:** Arquitecto estratégico.',
            'plan_mejora': 'Mantener excelencia. Diseñar metodología de planeación organizacional. Liderar transformación de gestión estratégica corporativa.'
        }
    }
}

GESTION_INDICADORES_DIRECTOR = {
    'pregunta': 'GESTIÓN DE INDICADORES Y REPORTING',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No gestiona indicadores del área. Reporting inexistente o inadecuado. No presenta resultados a dirección. **Acción requerida:** Implementar sistema de indicadores urgentemente.',
            'plan_mejora': 'Capacitación en diseño de indicadores y dashboards. Definir indicadores clave del área. Implementar reporte mensual de gestión.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Gestión básica de indicadores. Pocos KPIs definidos. Reporting irregular o poco informativo. **Recomendación:** Fortalecer gestión de indicadores.',
            'plan_mejora': 'Definir tablero balanceado de indicadores. Implementar seguimiento mensual sistemático. Mejorar presentación de resultados a dirección.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Gestiona adecuadamente indicadores. Monitorea KPIs principales. Presenta resultados satisfactoriamente. **Oportunidad:** Dashboard ejecutivo de alto impacto.',
            'plan_mejora': 'Perfeccionar tablero de indicadores. Implementar visualización de datos avanzada. Desarrollar reporting predictivo.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Gestiona efectivamente indicadores. Dashboard completo y actualizado. Presenta resultados de forma clara y analítica. **Fortaleza reconocida:** Gestor de desempeño efectivo.',
            'plan_mejora': 'Mantener calidad en gestión de indicadores. Implementar business intelligence. Liderar definición de indicadores corporativos.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelencia en gestión de indicadores. Dashboard ejecutivo ejemplar. Presenta insights estratégicos de alto valor. **Fortaleza destacada:** Maestro en analytics.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación data-driven de la organización. Desarrollar cultura de gestión por indicadores.'
        }
    }
}

HERRAMIENTAS_GESTION_DIRECTOR = {
    'pregunta': 'MANEJO AVANZADO DE HERRAMIENTAS DE GESTIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Manejo muy deficiente de herramientas de gestión. No usa ERP ni sistemas clave. Bajo dominio de herramientas ofimáticas. **Acción requerida:** Capacitación urgente en herramientas.',
            'plan_mejora': 'Capacitación intensiva en ERP y sistemas corporativos. Curso avanzado de Excel y PowerPoint. Familiarización con metodologías de gestión de proyectos.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo básico de herramientas. Usa sistemas clave superficialmente. Dominio limitado de herramientas ofimáticas. **Recomendación:** Fortalecer competencias digitales.',
            'plan_mejora': 'Curso de herramientas ofimáticas avanzadas. Capacitación en ERP y sistemas de información. Certificación en gestión de proyectos.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Manejo adecuado de herramientas de gestión. Usa apropiadamente ERP y sistemas corporativos. Dominio satisfactorio de Office. **Oportunidad:** Aprovechar tecnología para mayor impacto.',
            'plan_mejora': 'Perfeccionar uso de business intelligence. Implementar metodologías ágiles. Desarrollar habilidades en automatización de procesos.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Dominio avanzado de herramientas de gestión. Usa efectivamente ERP, BI y Office. Aplica metodologías de gestión apropiadas. **Fortaleza reconocida:** Competente digitalmente.',
            'plan_mejora': 'Mantener actualización tecnológica. Liderar implementación de nuevas tecnologías en el área. Promover transformación digital.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Maestría en herramientas de gestión. Maximiza tecnología para generar valor. Referente en uso estratégico de herramientas. **Fortaleza destacada:** Líder digital.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación digital organizacional. Desarrollar estrategia de tecnología para la empresa.'
        }
    }
}


# =====================================================================
# FUNCIONES DE CÁLCULO Y GENERACIÓN DE PLANES
# =====================================================================

def calcular_puntaje_ponderado_director(respuestas):
    """
    Calcula el puntaje ponderado para la evaluación de Directores.

    Estructura:
    - Preguntas 1-3: Competencias Organizacionales (10% total)
    - Pregunta 4: Objetivos (40%)
    - Preguntas 5-8: Competencias Interpersonales (25% total)
    - Preguntas 9-12: Competencias Técnicas (25% total)
    - Pregunta 13: SST (0%)
    """

    # Definir pesos por categoría
    pesos_categorias = {
        'Competencias Organizacionales': 10.0,
        'Objetivos - El Hacer': 40.0,
        'Competencias Interpersonales - El Ser': 25.0,
        'Competencias Técnicas - El Saber': 25.0
    }

    # Inicializar puntajes por categoría
    puntajes_categorias = {cat: 0.0 for cat in pesos_categorias.keys()}
    preguntas_por_categoria = {cat: 0 for cat in pesos_categorias.keys()}
    detalle_categorias = {cat: {'puntaje_obtenido': 0, 'puntaje_maximo': 0, 'porcentaje': 0} for cat in pesos_categorias.keys()}

    # Procesar cada respuesta
    for respuesta in respuestas:
        if respuesta.pregunta.peso_porcentual == 0:  # SST no cuenta
            continue

        categoria = respuesta.pregunta.categoria
        valor_respuesta = float(respuesta.opcion_seleccionada.valor_numerico)

        # Acumular puntaje (escala 1-5)
        puntajes_categorias[categoria] += valor_respuesta
        preguntas_por_categoria[categoria] += 1

        # Acumular para detalle
        detalle_categorias[categoria]['puntaje_obtenido'] += valor_respuesta
        detalle_categorias[categoria]['puntaje_maximo'] += 5

    # Calcular puntaje total ponderado
    puntaje_total = 0.0

    for categoria, peso in pesos_categorias.items():
        num_preguntas = preguntas_por_categoria[categoria]
        if num_preguntas > 0:
            # Promedio de la categoría en escala 1-5
            promedio_categoria = puntajes_categorias[categoria] / num_preguntas
            # Convertir a porcentaje (1-5 → 0-100%)
            porcentaje_categoria = ((promedio_categoria - 1) / 4) * 100
            # Aplicar peso de la categoría
            puntaje_ponderado = (porcentaje_categoria * peso) / 100
            puntaje_total += puntaje_ponderado

            # Actualizar detalle con todas las claves necesarias
            detalle_categorias[categoria]['promedio'] = round(promedio_categoria, 2)
            detalle_categorias[categoria]['porcentaje'] = round(porcentaje_categoria, 2)
            detalle_categorias[categoria]['ponderacion'] = peso
            detalle_categorias[categoria]['contribucion'] = round(puntaje_ponderado, 2)

    # Calcular puntaje en escala 1-5
    puntaje_escala_5 = 1 + (puntaje_total / 100) * 4

    # Determinar nivel de desempeño
    if puntaje_total >= 91:
        nivel = 'Muy alto'
    elif puntaje_total >= 76:
        nivel = 'Alto'
    elif puntaje_total >= 61:
        nivel = 'Moderado'
    elif puntaje_total >= 41:
        nivel = 'Bajo'
    else:
        nivel = 'Muy bajo'

    return {
        'puntaje_porcentaje': round(puntaje_total, 2),
        'puntaje_escala': round(puntaje_escala_5, 2),
        'nivel_desempeno': nivel,
        'puntajes_categorias': puntajes_categorias,
        'pesos_categorias': pesos_categorias,
        'detalle_categorias': detalle_categorias
    }


def formatear_comentarios_evaluador(respuesta):
    """Formatea los comentarios del evaluador para incluir en el plan de mejora"""
    comentarios = ""
    if respuesta.comentarios_evaluador:
        comentarios += f"   💬 Comentario del evaluador: {respuesta.comentarios_evaluador}\n"
    return comentarios


def generar_plan_mejora_director(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera el plan de mejora personalizado para Directores
    siguiendo el formato estándar con estructura numerada
    """

    # Diccionario de competencias
    competencias = {
        'COMUNICACIÓN': COMUNICACION_DIRECTOR,
        'TRABAJO EN EQUIPO': TRABAJO_EQUIPO_DIRECTOR,
        'MEJORA CONTINUA': MEJORA_CONTINUA_DIRECTOR,
        'Diseñar, implementar y controlar la estrategia': OBJETIVOS_DIRECTOR,
        'LIDERAZGO ESTRATÉGICO': LIDERAZGO_ESTRATEGICO_DIRECTOR,
        'PENSAMIENTO ESTRATÉGICO': PENSAMIENTO_ESTRATEGICO_DIRECTOR,
        'TOMA DE DECISIONES BAJO PRESIÓN': TOMA_DECISIONES_DIRECTOR,
        'DESARROLLO DE PERSONAS': DESARROLLO_PERSONAS_DIRECTOR,
        'GESTIÓN FINANCIERA Y PRESUPUESTAL': GESTION_FINANCIERA_DIRECTOR,
        'PLANIFICACIÓN ESTRATÉGICA Y OPERATIVA': PLANIFICACION_ESTRATEGICA_DIRECTOR,
        'GESTIÓN DE INDICADORES Y REPORTING': GESTION_INDICADORES_DIRECTOR,
        'MANEJO AVANZADO DE HERRAMIENTAS DE GESTIÓN': HERRAMIENTAS_GESTION_DIRECTOR,
    }

    # Encabezado
    plan = "╔═══════════════════════════════════════════════════════════════════════════════╗\n"
    plan += "║              PLAN DE MEJORA - EVALUACIÓN ANUAL DIRECTORES                    ║\n"
    plan += "╚═══════════════════════════════════════════════════════════════════════════════╝\n\n"

    # Información del resultado
    puntaje = resultado_evaluacion.get('puntaje_porcentaje', 0)
    nivel = resultado_evaluacion.get('nivel_desempeno', 'N/A')
    detalle = resultado_evaluacion.get('detalle_categorias', {})

    plan += f"PUNTAJE TOTAL: {puntaje}% - Nivel: {nivel}\n\n"
    plan += "DETALLE POR CATEGORÍAS:\n"
    plan += f"  • Competencias Organizacionales (10%): {detalle.get('Competencias Organizacionales', {}).get('porcentaje', 0)}%\n"
    plan += f"  • Objetivos - El Hacer (40%): {detalle.get('Objetivos - El Hacer', {}).get('porcentaje', 0)}%\n"
    plan += f"  • Competencias Interpersonales (25%): {detalle.get('Competencias Interpersonales - El Ser', {}).get('porcentaje', 0)}%\n"
    plan += f"  • Competencias Técnicas (25%): {detalle.get('Competencias Técnicas - El Saber', {}).get('porcentaje', 0)}%\n\n"

    plan += "═══════════════════════════════════════════════════════════════════════════════\n\n"

    # Procesar respuestas y generar el plan por competencias
    respuestas_ordenadas = sorted(respuestas_evaluacion, key=lambda r: r.pregunta.orden)
    contador = 1

    for respuesta in respuestas_ordenadas:
        # Saltar SST
        if respuesta.pregunta.categoria == 'Observación SST':
            continue

        pregunta_texto = respuesta.pregunta.pregunta
        valor = respuesta.opcion_seleccionada.valor_numerico

        # Buscar la competencia correspondiente
        competencia_encontrada = None
        for key, comp in competencias.items():
            if key in pregunta_texto:
                competencia_encontrada = comp
                break

        if competencia_encontrada:
            respuesta_data = competencia_encontrada['respuestas'].get(valor, {})
            retroalimentacion = respuesta_data.get('retroalimentacion', '')
            plan_accion = respuesta_data.get('plan_mejora', '')

            # Limitar plan de acción a máximo 3 items
            acciones = [a.strip() for a in plan_accion.split('.') if a.strip()]
            if len(acciones) > 3:
                acciones = acciones[:3]
            plan_accion_limitado = '. '.join(acciones) + '.'

            plan += f"{contador}. {pregunta_texto[:80]}...\n"
            plan += f"   Calificación: {valor}/5\n"
            plan += f"   {retroalimentacion}\n"
            plan += f"   📋 Plan de acción: {plan_accion_limitado}\n"
            plan += formatear_comentarios_evaluador(respuesta)
            plan += "\n"

            contador += 1

    # Sección SST si existe
    respuesta_sst = next((r for r in respuestas_evaluacion if r.pregunta.categoria == 'Observación SST'), None)
    if respuesta_sst:
        plan += "═══════════════════════════════════════════════════════════════════════════════\n"
        plan += "OBSERVACIÓN DE SEGURIDAD Y SALUD EN EL TRABAJO (SST)\n"
        plan += "═══════════════════════════════════════════════════════════════════════════════\n\n"
        plan += f"Observación: {respuesta_sst.pregunta.pregunta}\n"
        plan += f"Respuesta: {respuesta_sst.opcion_seleccionada.opcion}\n"
        if respuesta_sst.comentarios_evaluador:
            plan += f"💬 Comentario del evaluador: {respuesta_sst.comentarios_evaluador}\n"
        plan += "\n"

    # Pie del plan
    plan += "═══════════════════════════════════════════════════════════════════════════════\n"
    plan += "INSTRUCCIONES:\n"
    plan += "1. Revisar este plan con el director en reunión de retroalimentación ejecutiva\n"
    plan += "2. Priorizar acciones según impacto estratégico\n"
    plan += "3. Establecer cronograma de seguimiento trimestral\n"
    plan += "4. Documentar avances y ajustes en cada revisión\n"
    plan += "═══════════════════════════════════════════════════════════════════════════════\n"

    return plan
