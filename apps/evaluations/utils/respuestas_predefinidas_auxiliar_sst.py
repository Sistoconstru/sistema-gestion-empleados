"""
Respuestas predefinidas y lógica de evaluación para Auxiliar de SST
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

COMUNICACION_AUXILIAR_SST = {
    'pregunta': 'COMUNICACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** La comunicación presenta deficiencias graves. Los reportes de inventario son confusos y contienen errores frecuentes. No comunica efectivamente con producción ni ventas. **Acción requerida:** Mejora urgente en comunicación sobre disponibilidad de stock.',
            'plan_mejora': 'Participar en taller de comunicación efectiva. Usar plantillas estándar para reportes de inventario. Confirmar comprensión de requerimientos mediante reuniones diarias con producción y ventas.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La comunicación es básica pero insuficiente para el cargo. Los reportes requieren aclaraciones frecuentes. Debe mejorar comunicación con producción y ventas sobre disponibilidad de materiales.',
            'plan_mejora': 'Desarrollar habilidades de síntesis en reportes de stock. Practicar comunicación clara de faltantes. Mejorar alertas tempranas sobre disponibilidad.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Se comunica adecuadamente sobre inventarios. Los reportes son generalmente claros aunque ocasionalmente requieren ajustes. Es receptivo a observaciones. **Oportunidad:** Mayor proactividad en comunicar situaciones críticas de stock.',
            'plan_mejora': 'Perfeccionar comunicación de análisis de inventarios complejos. Desarrollar alertas automáticas de stock crítico. Comunicar proactivamente desviaciones antes de solicitud.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Comunica efectivamente información de inventarios. Sus reportes son claros, precisos y oportunos. Facilita comprensión de disponibilidad a producción y ventas. **Fortaleza reconocida:** Comunicador efectivo.',
            'plan_mejora': 'Mantener excelencia comunicativa. Capacitar al equipo en comunicación efectiva de inventarios. Liderar reuniones de coordinación sobre disponibilidad de materiales.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente comunicador de información de inventarios. Sus reportes son impecables y anticipan necesidades. Es referente en comunicación sobre disponibilidad y stock. **Fortaleza destacada:** Comunicación excepcional.',
            'plan_mejora': 'Mantener excelencia. Crear guías de comunicación de inventarios para el área. Ser mentor en comunicación efectiva de disponibilidad a stakeholders.'
        }
    }
}

TRABAJO_EQUIPO_AUXILIAR_SST = {
    'pregunta': 'TRABAJO EN EQUIPO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No trabaja efectivamente con producción ni ventas. Se aísla y no comparte información crítica de stock. No contribuye a objetivos del área. **Acción requerida:** Desarrollar competencias colaborativas urgentemente.',
            'plan_mejora': 'Participar en actividades de integración con producción y ventas. Compartir información de inventarios oportunamente. Colaborar activamente en tomas de inventario trimestral.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El trabajo en equipo es limitado. Comparte información solo cuando se solicita. No apoya proactivamente a producción ni ventas. **Recomendación:** Mejorar disposición colaborativa.',
            'plan_mejora': 'Integrarse más con equipos de producción y comercial. Ofrecer información de disponibilidad proactivamente. Compartir mejores prácticas de gestión de inventarios.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Trabaja adecuadamente con el equipo. Comparte información cuando es necesario. Contribuye satisfactoriamente a tomas de inventario. **Oportunidad:** Mayor proactividad en coordinación interdepartamental.',
            'plan_mejora': 'Liderar iniciativas de mejora en procesos de inventarios. Crear sinergias entre almacén, producción y ventas. Facilitar comunicación fluida entre áreas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Trabaja muy bien en equipo. Comparte proactivamente información de stock. Coordina efectivamente con producción y ventas. Contribuye activamente a objetivos del área. **Fortaleza reconocida:** Excelente colaborador.',
            'plan_mejora': 'Mantener alto nivel de colaboración. Servir como enlace entre almacén y áreas productivas. Documentar mejores prácticas de coordinación.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente trabajo en equipo y coordinación interdepartamental. Es modelo de colaboración. Comparte generosamente información, apoya constantemente y facilita la operación. **Fortaleza destacada:** Líder natural en coordinación.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de mejora de coordinación interdepartamental. Facilitar espacios de colaboración entre almacén, producción y comercial.'
        }
    }
}

MEJORA_CONTINUA_AUXILIAR_SST = {
    'pregunta': 'MEJORA CONTINUA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No demuestra compromiso con mejora continua. Realiza procesos de inventario sin buscar optimización. No propone mejoras ni innovaciones. **Acción requerida:** Desarrollar mentalidad de mejora continua.',
            'plan_mejora': 'Capacitación en mejora continua de procesos de inventario. Establecer métricas de calidad para control de stock. Proponer al menos una mejora trimestral en procesos.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El enfoque de mejora continua es limitado. Cumple procedimientos sin cuestionarlos. Propone pocas mejoras en procesos de inventario. **Recomendación:** Fortalecer compromiso con optimización.',
            'plan_mejora': 'Implementar ciclos de revisión de procesos de inventario. Proponer mejoras en toma de inventario trimestral. Benchmarking con mejores prácticas del sector.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Realiza procesos bajo estándares aceptables. Ocasionalmente propone mejoras. **Oportunidad:** Mayor proactividad en optimización de gestión de inventarios.',
            'plan_mejora': 'Liderar proyecto de optimización de proceso específico de inventarios. Proponer automatizaciones en tareas repetitivas. Investigar mejores prácticas de gestión de stock.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Compromiso activo con mejora continua. Propone regularmente mejoras en procesos de inventarios. Implementa estándares de calidad altos. **Fortaleza reconocida:** Agente de cambio en el área.',
            'plan_mejora': 'Mantener proactividad. Liderar implementación de mejoras en procesos críticos de inventarios. Formar parte de comité de mejora continua organizacional.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente en mejora continua. Propone e implementa mejoras significativas constantemente. Ha optimizado procesos clave del área de inventarios. **Fortaleza destacada:** Innovador en gestión de stock.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación digital del área de inventarios. Diseñar programa de mejora continua para toda la cadena de suministro.'
        }
    }
}

# =====================================================================
# OBJETIVOS - EL HACER (40%)
# =====================================================================

OBJETIVOS_AUXILIAR_SST = {
    'pregunta': 'OBJETIVOS - GESTIÓN DE INVENTARIOS',
    'respuestas': {
        1: {
            'retroalimentacion': '**Desempeño insatisfactorio:** No cumple con objetivos de gestión de inventarios. Los informes contienen errores graves y frecuentes. No controla órdenes de pedido pendientes. Las asignaciones de madera no son correctas. No garantiza disponibilidad de stock. **Requiere plan de mejora inmediato.**',
            'plan_mejora': 'Capacitación urgente en gestión de inventarios y ERP. Supervisión directa en tomas de inventario. Revisión diaria de trabajo por coordinación. Capacitación en control de órdenes de pedido.'
        },
        2: {
            'retroalimentacion': '**Desempeño por debajo de expectativas:** Cumple parcialmente con objetivos. Los informes tienen errores que requieren corrección. El control de inventarios requiere seguimiento constante. Las asignaciones se retrasan. **Necesita mejora significativa.**',
            'plan_mejora': 'Entrenamiento en técnicas de gestión de inventarios. Implementar checklist de control de stock. Capacitación en asignación de madera producida. Seguimiento semanal de avances.'
        },
        3: {
            'retroalimentacion': '**Desempeño satisfactorio:** Cumple con objetivos básicos de gestión de inventarios. Los informes son generalmente correctos aunque requieren revisión. Controla inventarios adecuadamente. Las asignaciones se entregan a tiempo. **Oportunidad:** Mayor autonomía y proactividad.',
            'plan_mejora': 'Desarrollar análisis de inventarios más profundos. Mejorar precisión en asignaciones para reducir ajustes. Dominar completamente ciclo de órdenes de pedido. Proponer mejoras en procesos.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Cumple muy bien con objetivos. Gestiona efectivamente el ciclo completo de inventarios. Los informes reflejan la realidad del stock. Controla órdenes pendientes. Asigna correctamente madera producida. Garantiza disponibilidad de stock. **Fortaleza reconocida:** Confiabilidad en gestión.',
            'plan_mejora': 'Mantener excelencia. Asumir gestión de inventarios más complejos. Optimizar procesos de toma trimestral. Participar en proyectos estratégicos del área de operaciones.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente cumplimiento de objetivos. Su gestión de inventarios es impecable. Los informes no presentan errores. Maneja proactivamente todo el ciclo de inventarios. Es referente en gestión de stock. **Fortaleza destacada:** Excelencia en gestión de inventarios.',
            'plan_mejora': 'Mantener excelencia. Liderar implementación de controles de inventarios. Diseñar modelos de gestión de stock para la organización. Optimizar procesos de inventario trimestral.'
        }
    }
}

# =====================================================================
# COMPETENCIAS INTERPERSONALES - EL SER (25%)
# =====================================================================

CALIDAD_TRABAJO_AUXILIAR_SST = {
    'pregunta': 'CALIDAD EN EL TRABAJO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Conocimiento muy limitado del área de inventarios. No analiza aspectos complejos adecuadamente. Los informes presentan errores graves frecuentes. No refleja calidad en el trabajo. **Acción requerida:** Capacitación técnica urgente.',
            'plan_mejora': 'Capacitación intensiva en gestión de inventarios. Estudiar procedimientos del área. Supervisión constante en trabajos complejos. Implementar checklist de calidad.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico pero insuficiente. Dificultad para analizar situaciones complejas. Los informes requieren correcciones frecuentes. **Recomendación:** Profundizar conocimientos técnicos.',
            'plan_mejora': 'Curso de gestión de inventarios. Estudiar casos complejos con mentoría. Implementar revisión sistemática antes de entregar informes. Desarrollar criterio técnico.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Amplios conocimientos del área. Analiza adecuadamente situaciones. Los informes son generalmente correctos. **Oportunidad:** Mayor profundidad en análisis complejos de inventarios.',
            'plan_mejora': 'Especializarse en gestión de inventarios del sector maderero. Participar en análisis de casos complejos. Mejorar presentación de informes. Desarrollar criterio para discernir situaciones no rutinarias.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Amplios conocimientos del área de inventarios. Analiza efectivamente aspectos complejos. Sus informes son de calidad, presentan pocos errores y reflejan la realidad del stock. **Fortaleza reconocida:** Solidez técnica.',
            'plan_mejora': 'Mantener calidad. Profundizar en metodologías avanzadas de inventarios. Ser consultor interno en temas de gestión de stock. Participar en proyectos de mejora de calidad del área.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Amplios y profundos conocimientos de inventarios. Excelente capacidad de análisis de aspectos complejos. Sus informes son impecables y reflejan fielmente la realidad. Es referente técnico. **Fortaleza destacada:** Excelencia técnica.',
            'plan_mejora': 'Mantener excelencia. Liderar capacitación técnica del equipo. Diseñar manuales de procedimientos de inventarios. Representar a la empresa en asuntos técnicos con proveedores externos.'
        }
    }
}

ATENCION_DETALLE_AUXILIAR_SST = {
    'pregunta': 'ATENCIÓN AL DETALLE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Poca atención al detalle. No detecta diferencias entre lo físico y el sistema. No revisa consecutivos diariamente. Los informes contienen errores. Genera reprocesos. **Acción requerida:** Desarrollar meticulosidad urgentemente.',
            'plan_mejora': 'Implementar checklist de verificación para cada tarea. Practicar técnicas de revisión de documentos. Doble verificación de todos los informes. Capacitación en control de calidad.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Atención al detalle básica pero insuficiente. Detecta solo discrepancias evidentes. Omite registros ocasionalmente. Los informes requieren correcciones. **Recomendación:** Mejorar meticulosidad.',
            'plan_mejora': 'Desarrollar técnicas de análisis detallado. Implementar revisión sistemática de consecutivos. Practicar identificación de inconsistencias. Reducir errores en informes.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Detecta diferencias principales entre físico y sistema. Revisa consecutivos adecuadamente. **Oportunidad:** Mayor precisión en identificación de discrepancias menores antes del cierre.',
            'plan_mejora': 'Perfeccionar técnicas de análisis detallado. Implementar controles adicionales de verificación. Desarrollar alertas tempranas de discrepancias. Reducir margen de error a mínimo.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente atención al detalle. Detecta diferencias entre físico y sistema antes del cierre. Revisa consecutivos diariamente sin omitir registros. Identifica y reporta incongruencias oportunamente. **Fortaleza reconocida:** Meticulosidad.',
            'plan_mejora': 'Mantener precisión. Capacitar al equipo en técnicas de análisis detallado. Diseñar controles de calidad para el área. Participar en auditorías internas.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Atención al detalle excepcional. Identifica discrepancias mínimas que otros no detectan. Su revisión de consecutivos es impecable. Previene errores antes de que ocurran. **Fortaleza destacada:** Precisión extraordinaria.',
            'plan_mejora': 'Mantener excelencia. Liderar implementación de controles de calidad en toda el área. Diseñar programa de certificación en precisión de inventarios. Ser auditor líder interno.'
        }
    }
}

PLANEACION_PROGRAMACION_AUXILIAR_SST = {
    'pregunta': 'PLANEACIÓN Y PROGRAMACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No planea adecuadamente las asignaciones ni el inventario trimestral. Trabaja reactivamente. No coordina con el equipo. Incumple plazos. **Acción requerida:** Desarrollar habilidades de planeación urgentemente.',
            'plan_mejora': 'Capacitación en gestión del tiempo y planeación. Elaborar cronograma semanal de actividades. Usar calendario de inventarios. Coordinar diariamente con equipo y coordinación.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Planeación básica pero insuficiente. Elabora cronograma pero no lo sigue consistentemente. La coordinación es limitada. Ocasionalmente incumple plazos. **Recomendación:** Mejorar organización.',
            'plan_mejora': 'Implementar sistema de gestión de tareas. Seguimiento semanal de cumplimiento de cronograma. Mejorar comunicación de plazos. Establecer alertas tempranas.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Planea adecuadamente asignaciones e inventario trimestral. Organiza secuencia de actividades. Cumple generalmente con plazos. **Oportunidad:** Mayor anticipación y coordinación proactiva.',
            'plan_mejora': 'Perfeccionar planeación de inventarios complejos. Implementar seguimiento de hitos críticos. Mejorar coordinación con producción y ventas. Desarrollar planes de contingencia.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Planea efectivamente asignaciones, compras y preparación de inventario trimestral. Organiza secuencia con anticipación suficiente. Las tareas críticas se ejecutan sin contratiempos. **Fortaleza reconocida:** Excelente planificador.',
            'plan_mejora': 'Mantener excelencia en planeación. Liderar implementación de mejoras en cronogramas del área. Capacitar al equipo en gestión del tiempo. Optimizar procesos de inventario.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente capacidad de planeación. Organiza calendarios detallados con anticipación. Coordina impecablemente. Siempre cumple plazos y anticipa contingencias. **Fortaleza destacada:** Planeación estratégica excepcional.',
            'plan_mejora': 'Mantener excelencia. Liderar planeación estratégica del área de inventarios. Diseñar sistema de gestión de proyectos. Optimizar procesos de inventario trimestral a nivel organizacional.'
        }
    }
}

COMUNICACION_EFECTIVA_AUXILIAR_SST = {
    'pregunta': 'COMUNICACIÓN EFECTIVA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No coordina efectivamente con producción ni ventas. No informa sobre disponibilidad de materiales. Genera paros por falta de comunicación. **Acción requerida:** Desarrollar comunicación efectiva urgentemente.',
            'plan_mejora': 'Capacitación en comunicación interdepartamental. Implementar reuniones diarias con producción y ventas. Establecer protocolo de alertas de stock. Desarrollar canales efectivos de comunicación.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Comunicación limitada con producción y ventas. Informa sobre faltantes solo cuando se solicita. No es proactivo en alertas de stock. **Recomendación:** Fortalecer comunicación proactiva.',
            'plan_mejora': 'Desarrollar habilidades de comunicación proactiva. Implementar sistema de alertas automáticas. Mejorar coordinación con áreas productivas. Capacitarse en comunicación efectiva.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Coordina adecuadamente con producción y ventas. Informa sobre disponibilidad cuando es necesario. **Oportunidad:** Mayor proactividad en comunicar situaciones críticas de stock.',
            'plan_mejora': 'Perfeccionar técnicas de comunicación. Implementar alertas tempranas de faltantes. Desarrollar comunicación predictiva de necesidades. Mejorar coordinación interdepartamental.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Coordina muy bien con producción y ventas. Informa oportunamente sobre faltantes o excesos. Previene paros mediante comunicación efectiva. **Fortaleza reconocida:** Comunicación interdepartamental sólida.',
            'plan_mejora': 'Mantener comunicación efectiva. Diseñar sistema de alertas optimizado. Implementar mejores prácticas de coordinación. Participar en proyectos de integración departamental.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente comunicación con producción y ventas. Coordina magistralmente sobre disponibilidad. Sus alertas previenen paros. Anticipa necesidades. **Fortaleza destacada:** Comunicación excepcional.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de comunicación interdepartamental. Diseñar sistema de información integrado. Ser mentor en coordinación efectiva.'
        }
    }
}

# =====================================================================
# COMPETENCIAS TÉCNICAS - EL SABER (25%)
# =====================================================================

ERP_AVANZADO_AUXILIAR_SST = {
    'pregunta': 'ERP AVANZADO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina el ERP. No puede gestionar OPs, remisiones ni ajustes. Desconoce funcionalidades de carga de producción. Genera negativos en el sistema. Requiere asistencia constante. **Acción requerida:** Capacitación urgente en sistema.',
            'plan_mejora': 'Curso básico del ERP utilizado. Practicar gestión de OPs y remisiones. Estudiar funcionalidades de inventarios. Tutorías diarias hasta lograr autonomía básica.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo básico del ERP. Gestiona OPs simples con dificultad. No domina carga de producción ni resolución de negativos. **Recomendación:** Profundizar en herramienta.',
            'plan_mejora': 'Curso intermedio del ERP. Aprender carga de producción correctamente. Dominar ajustes y traslados. Practicar resolución de negativos en el sistema.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Dominio adecuado del ERP. Gestiona OPs, remisiones y ajustes estándar. Conoce funcionalidades principales. **Oportunidad:** Dominar características avanzadas y resolución de negativos.',
            'plan_mejora': 'Especializarse en módulos avanzados del sistema. Aprender resolución de negativos complejos. Desarrollar consultas personalizadas. Optimizar uso de herramientas de inventarios.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Dominio avanzado del ERP. Opera el sistema con autonomía total. Gestiona eficientemente OPs, remisiones, ajustes y carga de producción. Resuelve negativos correctamente. **Fortaleza reconocida:** Experticia en sistema.',
            'plan_mejora': 'Mantener dominio. Capacitar al equipo en uso avanzado del ERP. Optimizar procesos mediante automatizaciones. Participar en implementación de nuevas versiones.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Experto en ERP. Domina todas las funcionalidades de inventarios. Opera con autonomía total. Resuelve problemas complejos del sistema. Optimiza procesos. **Fortaleza destacada:** Experto en tecnología de inventarios.',
            'plan_mejora': 'Mantener excelencia. Liderar optimización tecnológica del área. Diseñar programa de certificación en ERP para el equipo. Evaluar e implementar nuevas herramientas.'
        }
    }
}

GESTION_INVENTARIOS_MADERERO_AUXILIAR_SST = {
    'pregunta': 'GESTIÓN DE INVENTARIOS - SECTOR MADERERO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina metodologías de toma física ni valorización. No entiende variabilidad del producto natural. No aplica criterio para diferenciar errores. Genera problemas en inventarios. **Acción requerida:** Capacitación técnica urgente.',
            'plan_mejora': 'Capacitación en gestión de inventarios del sector maderero. Estudiar metodologías de toma física. Aprender valorización por costo promedio. Comprender variabilidad de producto natural.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico de gestión de inventarios. Aplica toma física con dificultad. No domina valorización. Confunde errores del sistema con variaciones naturales. **Recomendación:** Profundizar conocimientos técnicos.',
            'plan_mejora': 'Curso de gestión de inventarios especializados. Estudiar casos del sector maderero. Practicar valorización por costo promedio. Desarrollar criterio técnico.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Dominio adecuado de metodologías de toma física. Aplica valorización correctamente en casos comunes. Comprende variabilidad básica del producto natural. **Oportunidad:** Desarrollar criterio experto para casos complejos.',
            'plan_mejora': 'Especializarse en gestión de inventarios del sector. Estudiar casos complejos de variabilidad. Profundizar en políticas de asignación. Participar en actualizaciones metodológicas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen dominio de gestión de inventarios del sector maderero. Aplica correctamente metodologías de toma física. Valoriza adecuadamente. Aplica criterio para diferenciar errores de variaciones naturales. **Fortaleza reconocida:** Solidez técnica sectorial.',
            'plan_mejora': 'Mantener dominio. Ser consultor interno en inventarios del sector. Liderar actualización de políticas de inventarios. Capacitar al equipo en especificidades del producto natural.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Experto en gestión de inventarios del sector maderero. Domina todas las metodologías. Aplica criterio excepcional para diferenciar errores de variaciones. Es referente técnico. **Fortaleza destacada:** Experto sectorial.',
            'plan_mejora': 'Mantener excelencia. Liderar implementación de mejores prácticas del sector. Diseñar manual de gestión de inventarios madereros. Representar a la empresa en foros técnicos sectoriales.'
        }
    }
}

SOFTWARE_CONTABLE_AUXILIAR_SST = {
    'pregunta': 'MANEJO AVANZADO DEL SOFTWARE CONTABLE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina el software contable. No puede generar estados financieros ni informes de gestión. Desconoce funcionalidades. Requiere asistencia constante. **Acción requerida:** Capacitación urgente en sistema.',
            'plan_mejora': 'Curso básico del software contable utilizado. Practicar generación de reportes estándar. Estudiar funcionalidades principales. Tutorías diarias hasta lograr autonomía básica.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo básico del software. Genera reportes simples con dificultad. No domina módulos avanzados ni personalización de informes. **Recomendación:** Profundizar en herramienta.',
            'plan_mejora': 'Curso intermedio del software contable. Aprender generación de estados financieros. Dominar reportes de gestión. Practicar personalización de informes fiscales.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Dominio adecuado del software contable. Genera estados financieros e informes de gestión estándar. Conoce funcionalidades principales. **Oportunidad:** Dominar características avanzadas.',
            'plan_mejora': 'Especializarse en módulos avanzados del sistema. Aprender automatizaciones. Desarrollar reportes personalizados. Optimizar uso de herramientas analíticas.'
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

PLATAFORMAS_DIAN_AUXILIAR_SST = {
    'pregunta': 'CONOCIMIENTO DE PLATAFORMAS DIAN, BANCOS Y PARAFISCALES',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina los portales de DIAN, bancos ni parafiscales. No puede realizar trámites en línea. Desconoce procedimientos digitales. Genera retrasos. **Acción requerida:** Capacitación urgente en plataformas.',
            'plan_mejora': 'Capacitación básica en portales DIAN y entidades. Practicar trámites comunes con supervisión. Estudiar tutoriales de plataformas. Realizar presentaciones de prueba hasta lograr autonomía.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico de plataformas. Realiza trámites simples con dificultad. Desconoce procedimientos especiales. Requiere apoyo frecuente. **Recomendación:** Mejorar dominio de portales.',
            'plan_mejora': 'Curso de actualización en plataformas DIAN y parafiscales. Practicar trámites en línea. Estudiar procedimientos especiales. Desarrollar autonomía en trámites digitales.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Dominio adecuado de portales DIAN, bancos y parafiscales. Realiza trámites comunes en línea correctamente. Conoce procedimientos principales. **Oportunidad:** Dominar trámites especiales y excepcionales.',
            'plan_mejora': 'Especializarse en procedimientos complejos. Estudiar normativa de trámites electrónicos. Desarrollar experticia en casos especiales. Mantenerse actualizado en cambios de plataformas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen dominio de plataformas DIAN, bancos y parafiscales. Realiza eficientemente todo tipo de trámites en línea. Conoce procedimientos especiales. Resuelve problemas técnicos. **Fortaleza reconocida:** Experticia en portales.',
            'plan_mejora': 'Mantener dominio. Capacitar al equipo en uso de plataformas. Ser punto de contacto con soporte técnico. Optimizar procesos de presentación electrónica.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Experto en plataformas DIAN, bancarias y parafiscales. Domina todos los procedimientos, incluyendo los más complejos. Resuelve problemas técnicos avanzados. Optimiza trámites digitales. **Fortaleza destacada:** Experto en tecnología tributaria digital.',
            'plan_mejora': 'Mantener excelencia. Liderar capacitación en portales para la organización. Diseñar procedimientos optimizados de trámites electrónicos. Representar a la empresa en implementación de nuevas plataformas.'
        }
    }
}

# =====================================================================
# FUNCIONES DE CÁLCULO Y GENERACIÓN DE PLAN
# =====================================================================

def calcular_puntaje_ponderado_auxiliar_sst(respuestas):
    """
    Calcula el puntaje ponderado para Auxiliar de SST
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


def generar_plan_mejora_auxiliar_sst(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Auxiliar de SST
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
║                        AUXILIAR DE SST                                ║
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
        8: 'comunicacion_efectiva',
        9: 'erp_avanzado',
        10: 'gestion_inventarios_maderero',
        11: 'software_contable',
        12: 'plataformas_dian'
    }

    # Mapeo de claves a diccionarios de datos
    RESPUESTAS_AUXILIAR_SST = {
        'comunicacion': COMUNICACION_AUXILIAR_SST,
        'trabajo_equipo': TRABAJO_EQUIPO_AUXILIAR_SST,
        'mejora_continua': MEJORA_CONTINUA_AUXILIAR_SST,
        'objetivos': OBJETIVOS_AUXILIAR_SST,
        'calidad_trabajo': CALIDAD_TRABAJO_AUXILIAR_SST,
        'atencion_detalle': ATENCION_DETALLE_AUXILIAR_SST,
        'planeacion_programacion': PLANEACION_PROGRAMACION_AUXILIAR_SST,
        'comunicacion_efectiva': COMUNICACION_EFECTIVA_AUXILIAR_SST,
        'erp_avanzado': ERP_AVANZADO_AUXILIAR_SST,
        'gestion_inventarios_maderero': GESTION_INVENTARIOS_MADERERO_AUXILIAR_SST,
        'software_contable': SOFTWARE_CONTABLE_AUXILIAR_SST,
        'plataformas_dian': PLATAFORMAS_DIAN_AUXILIAR_SST
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
            if clave_competencia and clave_competencia in RESPUESTAS_AUXILIAR_SST:
                competencia_data = RESPUESTAS_AUXILIAR_SST[clave_competencia]
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
