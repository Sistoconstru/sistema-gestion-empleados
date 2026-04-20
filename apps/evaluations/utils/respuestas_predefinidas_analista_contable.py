"""
Respuestas predefinidas y lógica de evaluación para Analista Contable
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

COMUNICACION_ANALISTA_CONTABLE = {
    'pregunta': 'COMUNICACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** La comunicación presenta deficiencias graves. Los reportes contables son confusos y contienen errores frecuentes. No comunica efectivamente con el equipo ni con la coordinación. **Acción requerida:** Mejora urgente en comunicación técnica contable.',
            'plan_mejora': 'Participar en taller de comunicación técnica financiera. Usar plantillas estándar para reportes. Confirmar comprensión de instrucciones mediante reuniones diarias con coordinación.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La comunicación es básica pero insuficiente para el cargo. Los reportes requieren aclaraciones frecuentes. Debe mejorar comunicación con equipo y coordinación sobre temas contables complejos.',
            'plan_mejora': 'Desarrollar habilidades de síntesis en reportes financieros. Practicar presentación de estados financieros. Mejorar comunicación de hallazgos en conciliaciones.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Se comunica adecuadamente sobre temas contables. Los reportes son generalmente claros aunque ocasionalmente requieren ajustes. Es receptivo a observaciones. **Oportunidad:** Mayor proactividad en comunicar situaciones críticas.',
            'plan_mejora': 'Perfeccionar comunicación de análisis contables complejos. Desarrollar presentaciones ejecutivas de estados financieros. Comunicar proactivamente desviaciones antes de solicitud.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Comunica efectivamente información contable compleja. Sus reportes son claros, precisos y oportunos. Facilita comprensión de situaciones financieras al equipo directivo. **Fortaleza reconocida:** Comunicador efectivo.',
            'plan_mejora': 'Mantener excelencia comunicativa. Capacitar al equipo contable en comunicación efectiva. Liderar presentaciones de resultados financieros a gerencia.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente comunicador de información financiera. Sus reportes son impecables y anticipan necesidades de información. Es referente en comunicación de temas contables complejos. **Fortaleza destacada:** Comunicación excepcional.',
            'plan_mejora': 'Mantener excelencia. Crear guías de comunicación contable para el área. Ser mentor en comunicación de información financiera a stakeholders.'
        }
    }
}

TRABAJO_EQUIPO_ANALISTA_CONTABLE = {
    'pregunta': 'TRABAJO EN EQUIPO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No trabaja efectivamente con el equipo contable. Se aísla y no comparte información crítica. No contribuye a objetivos del área. **Acción requerida:** Desarrollar competencias colaborativas urgentemente.',
            'plan_mejora': 'Participar en actividades de integración del equipo contable. Compartir conocimientos técnicos con auxiliares. Colaborar activamente en cierres contables mensuales.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El trabajo en equipo es limitado. Comparte información solo cuando se solicita. No apoya proactivamente a auxiliares contables. **Recomendación:** Mejorar disposición colaborativa.',
            'plan_mejora': 'Integrarse más en el equipo. Ofrecer apoyo técnico en períodos críticos. Compartir mejores prácticas contables con el equipo.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Trabaja adecuadamente con el equipo. Comparte información cuando es necesario. Contribuye satisfactoriamente a cierres contables. **Oportunidad:** Mayor proactividad en liderazgo técnico del equipo.',
            'plan_mejora': 'Liderar iniciativas de mejora en procesos contables. Crear sinergias entre áreas contable y financiera. Capacitar a auxiliares en temas técnicos complejos.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Trabaja muy bien en equipo. Comparte proactivamente conocimientos contables. Apoya técnicamente a auxiliares y contribuye activamente a objetivos del área. **Fortaleza reconocida:** Excelente colaborador.',
            'plan_mejora': 'Mantener alto nivel de colaboración. Servir como enlace técnico entre contabilidad y otras áreas. Documentar mejores prácticas de trabajo colaborativo.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente trabajo en equipo y liderazgo técnico. Es modelo de colaboración. Comparte generosamente conocimientos, apoya constantemente y eleva el nivel técnico del equipo. **Fortaleza destacada:** Líder natural del equipo contable.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de desarrollo técnico del equipo contable. Facilitar espacios de colaboración interdepartamental financiera.'
        }
    }
}

MEJORA_CONTINUA_ANALISTA_CONTABLE = {
    'pregunta': 'MEJORA CONTINUA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No demuestra compromiso con mejora continua. Realiza procesos contables sin buscar optimización. No propone mejoras ni innovaciones. **Acción requerida:** Desarrollar mentalidad de mejora continua.',
            'plan_mejora': 'Capacitación en mejora continua de procesos contables. Establecer métricas de calidad para análisis contables. Proponer al menos una mejora trimestral en procesos.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El enfoque de mejora continua es limitado. Cumple procedimientos sin cuestionarlos. Propone pocas mejoras en procesos contables. **Recomendación:** Fortalecer compromiso con optimización.',
            'plan_mejora': 'Implementar ciclos de revisión de procesos contables. Proponer mejoras en cierre contable. Benchmarking con mejores prácticas contables del sector.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Realiza procesos contables bajo estándares aceptables. Ocasionalmente propone mejoras. **Oportunidad:** Mayor proactividad en optimización de procesos contables.',
            'plan_mejora': 'Liderar proyecto de optimización de proceso contable específico. Proponer automatizaciones en tareas repetitivas. Investigar mejores prácticas contables.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Compromiso activo con mejora continua. Propone regularmente mejoras en procesos contables. Implementa estándares de calidad altos. **Fortaleza reconocida:** Agente de cambio en el área.',
            'plan_mejora': 'Mantener proactividad. Liderar implementación de mejoras en procesos críticos. Formar parte de comité de mejora continua organizacional.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente en mejora continua. Propone e implementa mejoras significativas constantemente. Ha optimizado procesos clave del área contable. **Fortaleza destacada:** Innovador en procesos contables.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación digital del área contable. Diseñar programa de mejora continua para toda el área financiera.'
        }
    }
}

# =====================================================================
# OBJETIVOS - EL HACER (40%)
# =====================================================================

OBJETIVOS_ANALISTA_CONTABLE = {
    'pregunta': 'OBJETIVOS - ANALIZAR Y CONCILIAR',
    'respuestas': {
        1: {
            'retroalimentacion': '**Desempeño insatisfactorio:** No cumple con objetivos de análisis y conciliación contable. Los informes contienen errores graves y frecuentes. Las conciliaciones no son oportunas. No garantiza cumplimiento tributario. **Requiere plan de mejora inmediato.**',
            'plan_mejora': 'Capacitación urgente en análisis contable y conciliaciones. Supervisión directa en cierres contables. Revisión diaria de trabajo por coordinación. Capacitación en obligaciones tributarias.'
        },
        2: {
            'retroalimentacion': '**Desempeño por debajo de expectativas:** Cumple parcialmente con objetivos. Los informes tienen errores que requieren corrección. Las conciliaciones se retrasan. El cumplimiento tributario requiere seguimiento constante. **Necesita mejora significativa.**',
            'plan_mejora': 'Entrenamiento en técnicas de análisis contable. Implementar checklist de conciliaciones. Capacitación en calendario tributario y parafiscal. Seguimiento semanal de avances.'
        },
        3: {
            'retroalimentacion': '**Desempeño satisfactorio:** Cumple con objetivos básicos de análisis y conciliación. Los informes son generalmente correctos aunque requieren revisión. Las conciliaciones se entregan a tiempo. Cumple obligaciones tributarias bajo supervisión. **Oportunidad:** Mayor autonomía y proactividad.',
            'plan_mejora': 'Desarrollar análisis contables más profundos. Mejorar calidad de conciliaciones para reducir revisiones. Dominar completamente calendario tributario. Proponer mejoras en procesos.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Cumple muy bien con objetivos. Analiza y concilia cuentas con exactitud. Los informes reflejan la calidad del trabajo del área. Garantiza cumplimiento tributario oportuno. Proporciona información financiera confiable. **Fortaleza reconocida:** Confiabilidad técnica.',
            'plan_mejora': 'Mantener excelencia. Asumir análisis contables más complejos. Capacitar a auxiliares en técnicas de conciliación. Participar en proyectos estratégicos del área financiera.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente cumplimiento de objetivos. Sus análisis y conciliaciones son impecables. Los informes no presentan errores. Maneja proactivamente obligaciones tributarias. Es referente técnico en análisis contable. **Fortaleza destacada:** Excelencia en análisis financiero.',
            'plan_mejora': 'Mantener excelencia. Liderar implementación de controles contables. Diseñar modelos de análisis financiero para la organización. Representar al área en auditorías externas.'
        }
    }
}

# =====================================================================
# COMPETENCIAS INTERPERSONALES - EL SER (25%)
# =====================================================================

CALIDAD_TRABAJO_ANALISTA_CONTABLE = {
    'pregunta': 'CALIDAD EN EL TRABAJO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Conocimiento muy limitado del área contable. No analiza aspectos complejos adecuadamente. Los informes presentan errores graves frecuentes. No refleja calidad en el trabajo. **Acción requerida:** Capacitación técnica urgente.',
            'plan_mejora': 'Capacitación intensiva en contabilidad y análisis financiero. Estudiar procedimientos contables del área. Supervisión constante en trabajos complejos. Implementar checklist de calidad.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico pero insuficiente. Dificultad para analizar situaciones complejas. Los informes requieren correcciones frecuentes. **Recomendación:** Profundizar conocimientos técnicos.',
            'plan_mejora': 'Curso de actualización contable y NIIF. Estudiar casos complejos con mentoría. Implementar revisión sistemática antes de entregar informes. Desarrollar criterio técnico.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Amplios conocimientos del área. Analiza adecuadamente situaciones. Los informes son generalmente correctos. **Oportunidad:** Mayor profundidad en análisis complejos.',
            'plan_mejora': 'Especializarse en área contable específica. Participar en análisis de casos complejos. Mejorar presentación de informes. Desarrollar criterio para discernir situaciones no rutinarias.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Amplios conocimientos del área contable. Analiza efectivamente aspectos complejos. Sus informes son de calidad, presentan pocos errores y reflejan el trabajo del área. **Fortaleza reconocida:** Solidez técnica.',
            'plan_mejora': 'Mantener calidad. Profundizar en normativa contable avanzada. Ser consultor interno en temas contables complejos. Participar en proyectos de mejora de calidad del área.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Amplios y profundos conocimientos contables. Excelente capacidad de análisis de aspectos complejos. Sus informes son impecables y reflejan fielmente la calidad del área. Es referente técnico. **Fortaleza destacada:** Excelencia técnica.',
            'plan_mejora': 'Mantener excelencia. Liderar capacitación técnica del equipo. Diseñar manuales de procedimientos contables. Representar a la empresa en asuntos técnicos con entes externos.'
        }
    }
}

ATENCION_DETALLE_ANALISTA_CONTABLE = {
    'pregunta': 'ATENCIÓN AL DETALLE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Poca atención al detalle. No identifica discrepancias en conciliaciones. Los informes contienen errores de datos. Genera reprocesos. **Acción requerida:** Desarrollar meticulosidad urgentemente.',
            'plan_mejora': 'Implementar checklist de verificación para cada tarea. Practicar técnicas de revisión de documentos. Doble verificación de todos los informes. Capacitación en control de calidad.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Atención al detalle básica pero insuficiente. Identifica solo discrepancias evidentes. Los informes requieren correcciones de datos. **Recomendación:** Mejorar meticulosidad.',
            'plan_mejora': 'Desarrollar técnicas de análisis detallado. Implementar revisión sistemática de conciliaciones. Practicar identificación de inconsistencias. Reducir errores en informes.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Procesa y analiza información financiera con efectividad adecuada. Identifica discrepancias principales en conciliaciones. **Oportunidad:** Mayor precisión y consistencia.',
            'plan_mejora': 'Perfeccionar técnicas de análisis detallado. Implementar controles adicionales en conciliaciones. Desarrollar alertas tempranas de discrepancias. Reducir margen de error a mínimo.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente atención al detalle. Procesa información financiera con efectividad, consistencia y precisión. Identifica discrepancias en conciliaciones antes del cierre. **Fortaleza reconocida:** Meticulosidad.',
            'plan_mejora': 'Mantener precisión. Capacitar al equipo en técnicas de análisis detallado. Diseñar controles de calidad para el área. Participar en auditorías internas.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Atención al detalle excepcional. Identifica discrepancias mínimas que otros no detectan. Sus conciliaciones son impecables. Previene errores antes de que ocurran. **Fortaleza destacada:** Precisión extraordinaria.',
            'plan_mejora': 'Mantener excelencia. Liderar implementación de controles de calidad en toda el área. Diseñar programa de certificación en precisión contable. Ser auditor líder interno.'
        }
    }
}

PLANEACION_PROGRAMACION_ANALISTA_CONTABLE = {
    'pregunta': 'PLANEACIÓN Y PROGRAMACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No planea adecuadamente el cierre contable ni obligaciones tributarias. Trabaja reactivamente. No coordina con el equipo. Incumple plazos. **Acción requerida:** Desarrollar habilidades de planeación urgentemente.',
            'plan_mejora': 'Capacitación en gestión del tiempo y planeación. Elaborar cronograma semanal de actividades. Usar calendario tributario. Coordinar diariamente con equipo y coordinación.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Planeación básica pero insuficiente. Elabora calendario pero no lo sigue consistentemente. La coordinación con el equipo es limitada. Ocasionalmente incumple plazos. **Recomendación:** Mejorar organización.',
            'plan_mejora': 'Implementar sistema de gestión de tareas. Seguimiento semanal de cumplimiento de cronograma. Mejorar comunicación de plazos con equipo. Establecer alertas tempranas.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Planea adecuadamente el cierre contable y obligaciones tributarias. Elabora calendario y coordina con el equipo. Cumple generalmente con plazos. **Oportunidad:** Mayor anticipación y coordinación proactiva.',
            'plan_mejora': 'Perfeccionar planeación de cierres complejos. Implementar seguimiento de hitos críticos. Mejorar coordinación interdepartamental. Desarrollar planes de contingencia.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Planea efectivamente cierre contable y obligaciones. Elabora calendario tributario detallado y coordina muy bien con el equipo para cumplimiento oportuno. Anticipa necesidades. **Fortaleza reconocida:** Excelente planificador.',
            'plan_mejora': 'Mantener excelencia en planeación. Liderar implementación de mejoras en cronogramas del área. Capacitar al equipo en gestión del tiempo. Optimizar procesos de cierre.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente capacidad de planeación. Elabora calendarios detallados con anticipación. Coordina impecablemente con equipo. Siempre cumple plazos y anticipa contingencias. **Fortaleza destacada:** Planeación estratégica excepcional.',
            'plan_mejora': 'Mantener excelencia. Liderar planeación estratégica del área contable. Diseñar sistema de gestión de proyectos contables. Optimizar procesos de cierre y tributarios a nivel organizacional.'
        }
    }
}

LIDERAZGO_EQUIPO_ANALISTA_CONTABLE = {
    'pregunta': 'LIDERAZGO Y ORIENTACIÓN AL EQUIPO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No orienta ni supervisa al equipo de auxiliares. No resuelve dudas técnicas. No revisa el trabajo antes de consolidar. Genera errores en información consolidada. **Acción requerida:** Desarrollar liderazgo técnico urgentemente.',
            'plan_mejora': 'Capacitación en liderazgo técnico. Implementar reuniones diarias con auxiliares. Establecer protocolo de revisión de trabajo. Desarrollar criterio para orientar al equipo.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Liderazgo técnico limitado. Resuelve solo dudas básicas. La revisión de trabajo de auxiliares es superficial. **Recomendación:** Fortalecer rol de orientador técnico.',
            'plan_mejora': 'Desarrollar habilidades de mentoría técnica. Implementar revisión sistemática de trabajo de auxiliares. Mejorar comunicación de criterios técnicos. Capacitarse en liderazgo.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Orienta adecuadamente al equipo. Resuelve dudas técnicas comunes. Revisa trabajo de auxiliares antes de consolidar. **Oportunidad:** Mayor proactividad en desarrollo del equipo.',
            'plan_mejora': 'Perfeccionar técnicas de mentoría. Implementar sesiones de capacitación técnica para auxiliares. Desarrollar criterios de revisión más rigurosos. Mejorar delegación efectiva.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Orienta y supervisa muy bien al equipo. Resuelve efectivamente dudas técnicas. Revisa rigurosamente trabajo de auxiliares antes de consolidar. Desarrolla capacidades del equipo. **Fortaleza reconocida:** Liderazgo técnico sólido.',
            'plan_mejora': 'Mantener liderazgo efectivo. Diseñar programa de desarrollo técnico para auxiliares. Implementar sistema de mentoría formal. Participar en proyectos de liderazgo organizacional.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente liderazgo técnico. Orienta magistralmente al equipo. Resuelve dudas complejas con claridad. Su revisión previene errores en consolidación. Eleva el nivel técnico del equipo constantemente. **Fortaleza destacada:** Líder técnico excepcional.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de certificación técnica del equipo contable. Diseñar escuela de formación contable interna. Ser mentor de otros analistas en la organización.'
        }
    }
}

# =====================================================================
# COMPETENCIAS TÉCNICAS - EL SABER (25%)
# =====================================================================

LEGISLACION_TRIBUTARIA_ANALISTA_CONTABLE = {
    'pregunta': 'LEGISLACIÓN TRIBUTARIA, LABORAL Y COMERCIAL',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Conocimiento muy deficiente de legislación tributaria, laboral y comercial. No domina obligaciones fiscales (IVA, ICA, retención). Desconoce normativa laboral. Genera riesgos legales y sanciones. **Acción requerida:** Capacitación urgente.',
            'plan_mejora': 'Curso intensivo de legislación tributaria colombiana. Estudiar obligaciones IVA, ICA, retención en fuente. Capacitación en normativa laboral básica. Supervisión estricta en declaraciones tributarias.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico pero insuficiente de legislación. Domina solo aspectos rutinarios de obligaciones tributarias. Desconoce normativa laboral compleja. Requiere apoyo constante. **Recomendación:** Profundizar conocimientos legales.',
            'plan_mejora': 'Curso de actualización tributaria. Estudiar reforma tributaria vigente. Capacitación en normativa laboral. Seminarios de legislación comercial. Consultar con expertos en casos complejos.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Dominio adecuado de obligaciones tributarias principales. Conoce normativa laboral básica. Maneja correctamente IVA, ICA y retenciones comunes. **Oportunidad:** Profundizar en normativa compleja.',
            'plan_mejora': 'Especializarse en área tributaria específica. Estudiar jurisprudencia fiscal relevante. Actualización continua en reformas. Desarrollar criterio para interpretar normas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen dominio de legislación tributaria, laboral y comercial. Maneja correctamente obligaciones fiscales. Conoce normativa laboral. Identifica riesgos legales y propone soluciones. **Fortaleza reconocida:** Solidez normativa.',
            'plan_mejora': 'Mantener actualización. Ser consultor interno en temas tributarios. Participar en implementación de reformas. Capacitar al equipo en cambios normativos.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente dominio de legislación. Experto en obligaciones tributarias, laborales y comerciales. Interpreta correctamente normas complejas. Previene riesgos legales. Es referente normativo. **Fortaleza destacada:** Experto legal-tributario.',
            'plan_mejora': 'Mantener excelencia. Liderar implementación de cumplimiento normativo. Representar a la empresa ante autoridades tributarias. Diseñar programa de actualización normativa para el área.'
        }
    }
}

MANEJO_PUC_NIIF_ANALISTA_CONTABLE = {
    'pregunta': 'MANEJO DEL PUC Y NIIF',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina el Plan Único de Cuentas ni las NIIF. Clasifica incorrectamente las cuentas. No aplica normas de información financiera. Genera estados financieros con errores graves. **Acción requerida:** Capacitación técnica urgente.',
            'plan_mejora': 'Curso básico de PUC. Capacitación en NIIF para PYMES. Estudiar estructura del plan de cuentas. Practicar clasificación contable bajo supervisión. Estudiar casos prácticos de NIIF.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico del PUC y NIIF. Clasifica correctamente cuentas simples pero tiene dificultades con complejas. Aplica NIIF en casos rutinarios. **Recomendación:** Profundizar conocimientos técnicos.',
            'plan_mejora': 'Curso intermedio de NIIF para PYMES. Estudiar aplicación del PUC en casos complejos. Practicar reconocimiento y medición bajo NIIF. Analizar estados financieros bajo estándares.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Aplica adecuadamente el PUC y las NIIF en casos comunes. Clasifica correctamente la mayoría de operaciones. Genera estados financieros con estándares básicos. **Oportunidad:** Dominar aplicación en situaciones complejas.',
            'plan_mejora': 'Especializarse en NIIF aplicadas a sector específico. Estudiar casos complejos de reconocimiento y medición. Profundizar en revelaciones financieras. Participar en actualizaciones de NIIF.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen dominio del PUC y las NIIF. Aplica correctamente normas de información financiera. Clasifica adecuadamente operaciones complejas. Genera estados financieros de calidad. **Fortaleza reconocida:** Solidez en estándares contables.',
            'plan_mejora': 'Mantener dominio. Ser consultor interno en aplicación de NIIF. Liderar actualización de políticas contables. Capacitar al equipo en estándares internacionales.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Experto en PUC y NIIF. Aplica magistralmente normas de información financiera para PYMES. Domina revelaciones complejas. Sus estados financieros son referencia de calidad. **Fortaleza destacada:** Experto en estándares internacionales.',
            'plan_mejora': 'Mantener excelencia. Liderar implementación de actualizaciones de NIIF. Diseñar manual de políticas contables organizacional. Representar a la empresa en temas de estándares internacionales.'
        }
    }
}

MANEJO_SOFTWARE_CONTABLE_ANALISTA_CONTABLE = {
    'pregunta': 'MANEJO AVANZADO DEL SOFTWARE CONTABLE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina el software contable. No puede generar estados financieros ni informes de gestión. Desconoce funcionalidades avanzadas. Requiere asistencia constante. **Acción requerida:** Capacitación urgente en sistema.',
            'plan_mejora': 'Curso básico del software contable utilizado. Practicar generación de reportes estándar. Estudiar funcionalidades principales. Tutorías diarias hasta lograr autonomía básica.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo básico del software. Genera reportes simples con dificultad. No domina módulos avanzados ni personalización de informes. **Recomendación:** Profundizar en herramienta.',
            'plan_mejora': 'Curso intermedio del software contable. Aprender generación de estados financieros. Dominar reportes de gestión. Practicar personalización de informes fiscales.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Dominio adecuado del software contable. Genera estados financieros e informes de gestión estándar. Conoce funcionalidades principales. **Oportunidad:** Dominar características avanzadas.',
            'plan_mejora': 'Especializarse en módulos avanzados del sistema. Aprender automatizaciones y macros. Desarrollar reportes personalizados. Optimizar uso de herramientas analíticas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Dominio avanzado del software contable. Genera eficientemente estados financieros, informes de gestión y reportes fiscales. Aprovecha funcionalidades avanzadas. **Fortaleza reconocida:** Experticia en sistema.',
            'plan_mejora': 'Mantener dominio. Capacitar al equipo en uso avanzado del software. Optimizar procesos mediante automatizaciones. Participar en implementación de nuevas versiones.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Experto en software contable. Domina todas las funcionalidades, incluyendo las más avanzadas. Genera reportes complejos y personalizados. Optimiza procesos mediante el sistema. **Fortaleza destacada:** Experto en tecnología contable.',
            'plan_mejora': 'Mantener excelencia. Liderar optimización tecnológica del área contable. Diseñar programa de certificación en software para el equipo. Evaluar e implementar nuevas herramientas tecnológicas.'
        }
    }
}

CONOCIMIENTO_PLATAFORMAS_DIAN_ANALISTA_CONTABLE = {
    'pregunta': 'CONOCIMIENTO DE PLATAFORMAS DIAN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina los portales de la DIAN. No puede realizar trámites en línea. Desconoce procedimientos digitales. Genera retrasos en obligaciones. **Acción requerida:** Capacitación urgente en plataformas.',
            'plan_mejora': 'Capacitación básica en portales DIAN. Practicar trámites comunes con supervisión. Estudiar tutoriales de plataformas. Realizar presentaciones de prueba hasta lograr autonomía.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico de plataformas DIAN. Realiza trámites simples con dificultad. Desconoce procedimientos especiales. Requiere apoyo frecuente. **Recomendación:** Mejorar dominio de portales.',
            'plan_mejora': 'Curso de actualización en plataformas DIAN. Practicar declaraciones y pagos en línea. Estudiar procedimientos especiales. Desarrollar autonomía en trámites digitales.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Dominio adecuado de portales DIAN. Realiza trámites comunes en línea correctamente. Conoce procedimientos principales. **Oportunidad:** Dominar trámites especiales y excepcionales.',
            'plan_mejora': 'Especializarse en procedimientos complejos de DIAN. Estudiar normativa de trámites electrónicos. Desarrollar experticia en casos especiales. Mantenerse actualizado en cambios de plataformas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen dominio de plataformas DIAN. Realiza eficientemente todo tipo de trámites en línea. Conoce procedimientos especiales. Resuelve problemas técnicos de plataformas. **Fortaleza reconocida:** Experticia en portales tributarios.',
            'plan_mejora': 'Mantener dominio. Capacitar al equipo en uso de plataformas DIAN. Ser punto de contacto con soporte técnico de DIAN. Optimizar procesos de presentación electrónica.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Experto en plataformas DIAN. Domina todos los procedimientos, incluyendo los más complejos. Resuelve problemas técnicos avanzados. Optimiza trámites digitales. **Fortaleza destacada:** Experto en tecnología tributaria digital.',
            'plan_mejora': 'Mantener excelencia. Liderar capacitación en portales DIAN para la organización. Diseñar procedimientos optimizados de trámites electrónicos. Representar a la empresa en implementación de nuevas plataformas.'
        }
    }
}

# =====================================================================
# FUNCIONES DE CÁLCULO Y GENERACIÓN DE PLAN
# =====================================================================

def calcular_puntaje_ponderado_analista_contable(respuestas):
    """
    Calcula el puntaje ponderado para Analista Contable
    Distribución: Org 10%, Obj 40%, Interp 25%, Tec 25%
    """
    # Definir los pesos por categoría
    pesos_categorias = {
        'Competencias Organizacionales': 10.0,
        'Objetivos - El Hacer': 40.0,
        'Competencias Interpersonales - El Ser': 25.0,
        'Competencias Técnicas - El Saber': 25.0
    }

    # Agrupar respuestas por categoría
    respuestas_por_categoria = {}
    for respuesta in respuestas:
        if respuesta.pregunta.categoria == 'Observación SST':
            continue  # No afecta el puntaje

        categoria = respuesta.pregunta.categoria
        if categoria not in respuestas_por_categoria:
            respuestas_por_categoria[categoria] = []
        respuestas_por_categoria[categoria].append(respuesta)

    # Calcular puntaje por categoría
    puntajes_categorias = {}
    for categoria, lista_respuestas in respuestas_por_categoria.items():
        suma_puntajes = sum(float(r.opcion_seleccionada.valor_numerico) for r in lista_respuestas)
        num_preguntas = len(lista_respuestas)
        promedio_categoria = suma_puntajes / num_preguntas if num_preguntas > 0 else 0
        puntajes_categorias[categoria] = promedio_categoria

    # Calcular puntaje total ponderado y detalle por categorías
    puntaje_total = 0
    detalle_categorias = {}

    for categoria, peso in pesos_categorias.items():
        if categoria in puntajes_categorias:
            promedio = puntajes_categorias[categoria]
            # Convertir escala 1-5 a porcentaje (0-100%) y aplicar peso
            puntaje_categoria_porcentaje = ((promedio - 1) / 4) * 100
            contribucion = (puntaje_categoria_porcentaje * peso) / 100
            puntaje_total += contribucion

            # Guardar detalle de la categoría
            detalle_categorias[categoria] = {
                'promedio': round(promedio, 2),
                'porcentaje': round(puntaje_categoria_porcentaje, 2),
                'ponderacion': peso,
                'contribucion': round(contribucion, 2)
            }

    # Convertir puntaje total a escala 1-5
    puntaje_escala_5 = 1 + (puntaje_total / 100) * 4

    # Determinar nivel de desempeño
    if puntaje_total >= 90:
        nivel = 'Muy alto'
    elif puntaje_total >= 70:
        nivel = 'Alto'
    elif puntaje_total >= 50:
        nivel = 'Moderado'
    elif puntaje_total >= 30:
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
    """
    Formatea los comentarios del evaluador para el plan de mejora
    """
    comentarios = ""
    if respuesta.comentarios_evaluador:
        comentarios += f"   💬 Comentario del evaluador: {respuesta.comentarios_evaluador}\n"
    return comentarios


def generar_plan_mejora_analista_contable(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Analista Contable
    basado en respuestas y resultado ponderado.
    Formato estándar unificado con otros planes de mejora.

    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion
        resultado_evaluacion: dict con resultado del cálculo ponderado

    Returns:
        str: Plan de mejora completo formateado
    """
    planes = []

    # Encabezado con resultado general
    plan_header = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║              PLAN DE MEJORA - EVALUACIÓN ANUAL DE DESEMPEÑO                  ║
║                           ANALISTA CONTABLE                                  ║
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

    # Mapeo de preguntas a competencias
    mapeo_competencias = {
        1: 'comunicacion',
        2: 'trabajo_equipo',
        3: 'mejora_continua',
        4: 'objetivos',
        5: 'calidad_trabajo',
        6: 'atencion_detalle',
        7: 'planeacion_programacion',
        8: 'liderazgo_equipo',
        9: 'legislacion_tributaria',
        10: 'manejo_puc_niif',
        11: 'manejo_software_contable',
        12: 'conocimiento_plataformas_dian'
    }

    # Mapeo de claves a diccionarios de datos
    RESPUESTAS_ANALISTA_CONTABLE = {
        'comunicacion': COMUNICACION_ANALISTA_CONTABLE,
        'trabajo_equipo': TRABAJO_EQUIPO_ANALISTA_CONTABLE,
        'mejora_continua': MEJORA_CONTINUA_ANALISTA_CONTABLE,
        'objetivos': OBJETIVOS_ANALISTA_CONTABLE,
        'calidad_trabajo': CALIDAD_TRABAJO_ANALISTA_CONTABLE,
        'atencion_detalle': ATENCION_DETALLE_ANALISTA_CONTABLE,
        'planeacion_programacion': PLANEACION_PROGRAMACION_ANALISTA_CONTABLE,
        'liderazgo_equipo': LIDERAZGO_EQUIPO_ANALISTA_CONTABLE,
        'legislacion_tributaria': LEGISLACION_TRIBUTARIA_ANALISTA_CONTABLE,
        'manejo_puc_niif': MANEJO_PUC_NIIF_ANALISTA_CONTABLE,
        'manejo_software_contable': MANEJO_SOFTWARE_CONTABLE_ANALISTA_CONTABLE,
        'conocimiento_plataformas_dian': CONOCIMIENTO_PLATAFORMAS_DIAN_ANALISTA_CONTABLE
    }

    for respuesta in respuestas_evaluacion.order_by('pregunta__orden'):
        # Excluir preguntas SST
        if respuesta.pregunta.categoria == 'Observación SST':
            continue

        numero_pregunta = respuesta.pregunta.orden
        nombre_competencia = respuesta.pregunta.pregunta
        puntuacion = int(respuesta.opcion_seleccionada.valor_numerico) if respuesta.opcion_seleccionada else 0
        clave_competencia = mapeo_competencias.get(numero_pregunta)

        plan_texto = f"{contador}. {nombre_competencia}\n"
        plan_texto += f"   Calificación: {puntuacion}/5\n"

        # Agregar comentarios del evaluador si existen
        plan_texto += formatear_comentarios_evaluador(respuesta)
        plan_texto += "\n"

        # Si puntuación es 5: Felicitar
        if puntuacion == 5:
            plan_texto += "   ✅ ¡EXCELENTE DESEMPEÑO!\n"
            plan_texto += "   El empleado ha demostrado dominio excepcional en esta competencia.\n"
            plan_texto += "   Continue con este nivel de excelencia.\n"

        # Si puntuación es 4 o menos: Plan de acción
        else:
            if clave_competencia and clave_competencia in RESPUESTAS_ANALISTA_CONTABLE:
                competencia_data = RESPUESTAS_ANALISTA_CONTABLE[clave_competencia]
                if puntuacion in competencia_data['respuestas']:
                    datos_respuesta = competencia_data['respuestas'][puntuacion]

                    plan_texto += f"   📋 PLAN DE ACCIÓN:\n"

                    # Dividir el plan_mejora en puntos (separados por punto)
                    plan_mejora_texto = datos_respuesta.get('plan_mejora', '')
                    items_plan = [item.strip() for item in plan_mejora_texto.split('.') if item.strip()]

                    # Tomar solo los primeros 3 items
                    for idx, item in enumerate(items_plan[:3], 1):
                        plan_texto += f"   {idx}. {item}.\n"

                    # Marcar si requiere seguimiento bimensual (cualquier puntuación ≤ 4)
                    if puntuacion <= 4:
                        plan_texto += f"\n   ⚠️  REQUIERE SEGUIMIENTO BIMENSUAL\n"
                else:
                    # Plan genérico si no hay datos para esa puntuación
                    plan_texto += f"   📋 PLAN DE ACCIÓN:\n"
                    plan_texto += f"   1. Revisar los procedimientos y mejores prácticas relacionadas con esta competencia.\n"
                    plan_texto += f"   2. Solicitar retroalimentación constante del supervisor inmediato.\n"
                    plan_texto += f"   3. Establecer metas específicas para mejorar en esta área.\n"
            else:
                # Plan genérico si no hay datos predefinidos
                plan_texto += f"   📋 PLAN DE ACCIÓN:\n"
                plan_texto += f"   1. Revisar los procedimientos y mejores prácticas relacionadas con esta competencia.\n"
                plan_texto += f"   2. Solicitar retroalimentación constante del supervisor inmediato.\n"
                plan_texto += f"   3. Establecer metas específicas para mejorar en esta área.\n"

        plan_texto += "\n" + "-"*80 + "\n\n"
        planes.append(plan_texto)
        contador += 1

    # Agregar sección de SST
    planes.append("="*80 + "\n")
    planes.append("OBSERVACIÓN DE SEGURIDAD Y SALUD EN EL TRABAJO (SST)\n")
    planes.append("="*80 + "\n\n")
    planes.append("Nota: La evaluación de uso de EPP se registra por separado y no afecta el puntaje general.\n")
    planes.append("Esta observación es fundamental para garantizar la seguridad del empleado.\n\n")

    # Footer
    planes.append("="*80 + "\n")
    planes.append("INSTRUCCIONES:\n")
    planes.append("1. Este plan debe ser revisado y aceptado por el empleado.\n")
    planes.append("2. Se realizarán 3 seguimientos bimestrales (cada 2 meses) durante 6 meses.\n")
    planes.append("3. Al finalizar el período se realizará una evaluación final del plan.\n")
    planes.append("4. Las competencias con seguimiento bimensual deben mostrar avance progresivo.\n")
    planes.append("="*80 + "\n")

    return "".join(planes)
