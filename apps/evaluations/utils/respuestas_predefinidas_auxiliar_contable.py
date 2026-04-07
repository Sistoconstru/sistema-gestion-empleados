"""
Respuestas predefinidas y lógica de evaluación para Auxiliar Contable
Sistema de calificación: Escala 1-5 (Muy bajo a Muy alto)
Total de competencias: 11
Ponderación por categorías:
  - Competencias Organizacionales (10%): Preguntas 1-3
  - Objetivos (40%): Pregunta 4
  - Competencias Interpersonales (25%): Preguntas 5-7
  - Competencias Técnicas (25%): Preguntas 8-11
"""

# =====================================================================
# COMPETENCIAS ORGANIZACIONALES (10%)
# =====================================================================

COMUNICACION_AUX_CONTABLE = {
    'pregunta': 'COMUNICACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** La comunicación presenta deficiencias significativas. Los correos y reportes contables contienen errores frecuentes o información poco clara. No escucha activamente ni es receptivo a observaciones sobre registros contables. **Acción requerida:** Debe mejorar urgentemente su comunicación escrita y oral en temas contables.',
            'plan_mejora': 'Participar en taller de comunicación profesional. Utilizar plantillas estandarizadas para reportes contables. Practicar escucha activa con supervisor. Verificar claridad de comunicaciones antes de enviarlas.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La comunicación es básica pero presenta deficiencias. Sus reportes contables a veces son ambiguos o requieren aclaraciones. La comunicación con otras áreas sobre temas contables no siempre es clara. **Recomendación:** Debe mejorar claridad y precisión en comunicaciones contables.',
            'plan_mejora': 'Desarrollar formato estándar para comunicaciones contables. Confirmar comprensión de instrucciones mediante parafraseo. Mejorar redacción de correos sobre inconsistencias contables.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Se comunica de manera adecuada sobre temas contables. Sus reportes son generalmente claros aunque ocasionalmente requieren ajustes menores. Escucha con atención y es receptivo a observaciones. **Oportunidad de mejora:** Puede ser más proactivo en comunicar hallazgos contables.',
            'plan_mejora': 'Perfeccionar comunicación de hallazgos contables. Desarrollar capacidad de síntesis para reportes ejecutivos. Comunicar proactivamente novedades antes de que se soliciten.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Comunica efectivamente sobre temas contables. Sus reportes son claros, precisos y oportunos. Escucha activamente y es muy receptivo a observaciones. **Fortaleza reconocida:** Comunicador efectivo en temas contables.',
            'plan_mejora': 'Mantener excelente comunicación. Capacitar a otros en comunicación de temas contables. Liderar presentaciones sobre estados financieros.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente comunicador en temas contables. Sus reportes son impecables, claros y anticipan necesidades de información. Escucha activa ejemplar. Es referente en comunicación contable. **Fortaleza destacada:** Comunicación excepcional.',
            'plan_mejora': 'Mantener excelencia. Crear guías de comunicación contable para el área. Ser mentor en comunicación efectiva de información financiera.'
        }
    }
}

TRABAJO_EQUIPO_AUX_CONTABLE = {
    'pregunta': 'TRABAJO EN EQUIPO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No trabaja efectivamente en equipo. Se aísla en sus funciones contables y no comparte información relevante con el equipo. No contribuye a objetivos del área contable. **Acción requerida:** Debe desarrollar competencias de trabajo en equipo.',
            'plan_mejora': 'Participar en actividades de integración del área contable. Compartir conocimientos contables con compañeros. Colaborar activamente en cierres contables mensuales.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El trabajo en equipo es limitado. Comparte información contable ocasionalmente pero no proactivamente. Contribuye al equipo solo cuando es solicitado. **Recomendación:** Debe mejorar su disposición colaborativa.',
            'plan_mejora': 'Integrarse más en el equipo contable. Ofrecer apoyo proactivo en períodos de cierre. Compartir mejores prácticas contables con compañeros.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Trabaja adecuadamente en equipo. Comparte información contable cuando es necesario. Contribuye satisfactoriamente a objetivos del área. **Oportunidad de mejora:** Puede ser más proactivo en colaboración.',
            'plan_mejora': 'Liderar al menos una iniciativa de mejora en el área contable. Crear sinergias con otras áreas financieras.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Trabaja muy bien en equipo. Comparte proactivamente información y conocimientos contables. Contribuye activamente al logro de objetivos del área. **Fortaleza reconocida:** Excelente colaborador.',
            'plan_mejora': 'Mantener alto nivel de colaboración. Servir como enlace entre contabilidad y otras áreas. Documentar mejores prácticas de trabajo colaborativo.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente trabajo en equipo. Es modelo de colaboración en el área contable. Comparte generosamente conocimientos, apoya constantemente al equipo. **Fortaleza destacada:** Líder natural en trabajo colaborativo.',
            'plan_mejora': 'Mantener excelencia en trabajo en equipo. Liderar programa de integración del área contable. Facilitar espacios de colaboración interdepartamental.'
        }
    }
}

MEJORA_CONTINUA_AUX_CONTABLE = {
    'pregunta': 'MEJORA CONTINUA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No demuestra compromiso con mejora continua en procesos contables. Realiza tareas sin buscar estándares de calidad. No propone mejoras en procesos contables. **Acción requerida:** Debe desarrollar mentalidad de mejora continua.',
            'plan_mejora': 'Capacitación en mejora continua de procesos contables. Establecer estándares de calidad para registros contables. Proponer al menos una mejora trimestral.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El enfoque de mejora continua es limitado. Cumple estándares básicos pero no los busca activamente. Propone pocas mejoras en procesos contables. **Recomendación:** Debe fortalecer compromiso con calidad.',
            'plan_mejora': 'Implementar ciclos de revisión de calidad de registros. Proponer mejoras en procesos de cierre contable. Benchmarking con mejores prácticas contables.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Realiza actividades contables bajo estándares aceptables. Ocasionalmente propone mejoras en procesos. **Oportunidad de mejora:** Puede ser más proactivo en mejora continua.',
            'plan_mejora': 'Implementar mejoras en eficiencia de procesos contables. Proponer automatizaciones. Liderar iniciativa de mejora trimestral.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Comprometido con mejora continua. Realiza actividades bajo altos estándares. Propone regularmente mejoras en procesos contables. **Fortaleza reconocida:** Promotor de mejora continua.',
            'plan_mejora': 'Mantener enfoque de mejora continua. Compartir metodologías con equipo contable. Implementar mejora innovadora trimestral.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente compromiso con mejora continua. Establece y cumple altos estándares de calidad contable. Propone constantemente mejoras innovadoras. **Fortaleza destacada:** Líder en mejora continua.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de mejora continua del área contable. Capacitar en metodologías de mejora.'
        }
    }
}

# =====================================================================
# OBJETIVOS - EL HACER (40%)
# =====================================================================

OBJETIVOS_AUX_CONTABLE = {
    'pregunta': 'OBJETIVOS - Registrar y verificar transacciones contables',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No cumple objetivos contables. Los registros presentan errores frecuentes. No verifica transacciones adecuadamente. Los informes no son exactos ni oportunos. No cumple normas contables. **Acción requerida:** Capacitación urgente en procesos contables.',
            'plan_mejora': 'Capacitación en registros contables y software contable. Establecer checklist de verificación de transacciones. Mentoreé con contador senior. Implementar revisión diaria de registros.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Cumple parcialmente objetivos contables. Los registros tienen errores ocasionales. La verificación de transacciones es inconsistente. Los informes requieren correcciones frecuentes. **Recomendación:** Debe mejorar precisión y oportunidad.',
            'plan_mejora': 'Capacitación en verificación de transacciones. Implementar doble revisión de registros. Mejorar dominio de software contable. Estudiar normativa contable vigente.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Cumple objetivos contables satisfactoriamente. Los registros son generalmente correctos. Verifica transacciones adecuadamente. Los informes son aceptables. **Oportunidad de mejora:** Puede mejorar velocidad y reducir errores.',
            'plan_mejora': 'Optimizar procesos de registro para mayor eficiencia. Reducir tiempo de cierre contable. Implementar controles preventivos de errores.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Cumple muy bien objetivos contables. Registros precisos y oportunos. Verifica rigurosamente transacciones. Informes de alta calidad. Cumple normas contables. **Fortaleza reconocida:** Excelente desempeño contable.',
            'plan_mejora': 'Mantener alto nivel de desempeño. Automatizar procesos repetitivos. Capacitar a otros en buenas prácticas contables.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente cumplimiento de objetivos contables. Registros impecables y oportunos. Verificación exhaustiva. Informes de excelencia. Dominio total de normativa. **Fortaleza destacada:** Desempeño excepcional.',
            'plan_mejora': 'Mantener excelencia. Liderar proyecto de optimización de procesos contables. Ser referente en calidad contable.'
        }
    }
}

# =====================================================================
# COMPETENCIAS INTERPERSONALES - EL SER (25%)
# =====================================================================

COMPROMISO_RESPONSABILIDAD_AUX_CONTABLE = {
    'pregunta': 'COMPROMISO Y RESPONSABILIDAD',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No cumple compromisos. Los registros contables no se entregan en fechas establecidas. No reporta inconsistencias oportunamente. Falta de responsabilidad en cierre contable. **Acción requerida:** Debe mejorar urgentemente compromiso y responsabilidad.',
            'plan_mejora': 'Establecer calendario estricto de entregas contables. Implementar sistema de recordatorios. Reportar diariamente avance de actividades. Comprometerse públicamente con fechas de cierre.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El compromiso es inconsistente. Ocasionalmente incumple fechas de entrega de registros. No siempre reporta inconsistencias a tiempo. **Recomendación:** Debe fortalecer responsabilidad en cumplimiento de plazos.',
            'plan_mejora': 'Mejorar gestión del tiempo en actividades contables. Priorizar entregas según calendario de cierre. Comunicar proactivamente posibles retrasos.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Cumple compromisos satisfactoriamente. Generalmente entrega registros en fechas establecidas. Reporta inconsistencias adecuadamente. **Oportunidad de mejora:** Puede ser más proactivo y anticipatorio.',
            'plan_mejora': 'Anticipar entregas para evitar presión de última hora. Desarrollar sistema preventivo de detección de inconsistencias.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Alto compromiso y responsabilidad. Entrega registros puntualmente. Reporta inconsistencias oportunamente. Cumple rigurosamente plazos de cierre. **Fortaleza reconocida:** Muy responsable y comprometido.',
            'plan_mejora': 'Mantener alto nivel de compromiso. Ser ejemplo de responsabilidad para equipo contable. Apoyar en gestión de tiempos de cierre.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente compromiso y responsabilidad. Entrega antes de plazos establecidos. Detecta y reporta inconsistencias proactivamente. Modelo de responsabilidad. **Fortaleza destacada:** Compromiso excepcional.',
            'plan_mejora': 'Mantener excelencia. Liderar optimización de calendario de cierre contable. Ser mentor en gestión de compromisos.'
        }
    }
}

ATENCION_DETALLE_AUX_CONTABLE = {
    'pregunta': 'ATENCIÓN AL DETALLE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Baja atención al detalle. Los registros contables presentan errores numéricos frecuentes. No verifica cifras antes de registrar. Los cuadres presentan inconsistencias. **Acción requerida:** Debe mejorar urgentemente precisión y verificación.',
            'plan_mejora': 'Implementar checklist de verificación obligatorio. Realizar doble revisión de todos los registros. Capacitación en exactitud numérica. Práctica con ejercicios de precisión contable.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La atención al detalle es limitada. Los registros tienen errores ocasionales. No siempre verifica cifras antes de registrar. **Recomendación:** Debe mejorar verificación sistemática.',
            'plan_mejora': 'Implementar revisión de cifras antes de cada registro. Utilizar calculadora para verificar operaciones. Desarrollar hábito de revisión de soportes.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Atención al detalle satisfactoria. Generalmente procesa información contable con exactitud. Verifica cifras en la mayoría de casos. **Oportunidad de mejora:** Puede ser más riguroso en verificación.',
            'plan_mejora': 'Perfeccionar hábitos de verificación. Implementar control cruzado de cifras importantes. Reducir errores a cero.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente atención al detalle. Procesa información numérica con alta exactitud. Verifica rigurosamente cifras antes de registrar. Pocos o ningún error. **Fortaleza reconocida:** Muy preciso y detallista.',
            'plan_mejora': 'Mantener alta precisión. Compartir técnicas de verificación con equipo. Ser revisor de registros críticos.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Atención al detalle excepcional. Procesa información con exactitud impecable. Verifica exhaustivamente. Detecta errores que otros no ven. **Fortaleza destacada:** Precisión sobresaliente.',
            'plan_mejora': 'Mantener excelencia. Capacitar en técnicas de verificación contable. Liderar control de calidad de registros.'
        }
    }
}

PLANEACION_ORGANIZACION_AUX_CONTABLE = {
    'pregunta': 'CAPACIDAD DE PLANEACIÓN Y ORGANIZACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No planea ni organiza actividades contables. Las causaciones y cierres son desorganizados. Afecta informes gerenciales por falta de planeación. **Acción requerida:** Debe desarrollar urgentemente capacidad de planificación.',
            'plan_mejora': 'Crear calendario mensual de actividades contables. Priorizar causaciones según impacto en informes. Implementar sistema de organización de documentos. Capacitación en gestión del tiempo.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La planeación es limitada. Organiza actividades contables de manera básica. Ocasionalmente afecta oportunidad de informes. **Recomendación:** Debe mejorar anticipación y organización.',
            'plan_mejora': 'Implementar planeación semanal de actividades. Priorizar tareas según calendario de cierre. Organizar mejor documentación contable.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Planea y organiza actividades contables satisfactoriamente. Generalmente prioriza causaciones adecuadamente. Cumple con informes en plazos. **Oportunidad de mejora:** Puede optimizar organización.',
            'plan_mejora': 'Perfeccionar sistema de priorización. Anticipar necesidades de información. Optimizar flujo de documentación contable.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente planeación y organización. Anticipa y organiza ordenadamente actividades contables. Prioriza efectivamente. Asegura oportunidad de informes. **Fortaleza reconocida:** Muy organizado y planificado.',
            'plan_mejora': 'Mantener alto nivel de organización. Compartir sistema de planeación con equipo. Liderar optimización de calendario contable.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Planeación y organización excepcional. Anticipa perfectamente actividades contables. Organización impecable. Asegura oportunidad óptima de informes. **Fortaleza destacada:** Organización sobresaliente.',
            'plan_mejora': 'Mantener excelencia. Diseñar sistema de planeación para toda el área contable. Ser referente en organización.'
        }
    }
}

# =====================================================================
# COMPETENCIAS TÉCNICAS - EL SABER (25%)
# =====================================================================

MANEJO_OFFICE_AUX_CONTABLE = {
    'pregunta': 'MANEJO BÁSICO DE OFFICE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Manejo deficiente de Office. No domina Excel para tareas contables. No utiliza fórmulas ni tablas dinámicas. Esto limita gravemente su eficiencia. **Acción requerida:** Capacitación urgente en Excel.',
            'plan_mejora': 'Capacitación intensiva en Excel básico e intermedio. Aprender fórmulas contables (SUMA, SI, BUSCARV). Practicar tablas dinámicas. Desarrollar plantillas para conciliaciones.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo limitado de Office. Utiliza Excel básicamente pero no domina herramientas intermedias. No usa tablas dinámicas ni fórmulas avanzadas. **Recomendación:** Debe mejorar dominio de Excel.',
            'plan_mejora': 'Capacitación en Excel intermedio. Aprender tablas dinámicas. Practicar fórmulas para conciliaciones bancarias. Certificación en Office.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Manejo satisfactorio de Office. Utiliza Excel adecuadamente para tareas contables básicas. Conoce fórmulas fundamentales. **Oportunidad de mejora:** Puede dominar funciones avanzadas.',
            'plan_mejora': 'Capacitación en Excel avanzado. Aprender macros básicas. Automatizar reportes recurrentes. Optimizar uso de herramientas Office.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen manejo de Office. Domina Excel para tareas contables. Utiliza tablas dinámicas y fórmulas avanzadas. Genera reportes eficientemente. **Fortaleza reconocida:** Buen dominio de herramientas.',
            'plan_mejora': 'Mantener actualización en herramientas. Aprender Power Query para automatización. Capacitar a otros en Excel contable.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente manejo de Office. Dominio avanzado de Excel. Utiliza macros, Power Query, fórmulas complejas. Automatiza procesos. **Fortaleza destacada:** Experto en herramientas digitales.',
            'plan_mejora': 'Mantener excelencia. Liderar automatización de procesos contables. Capacitar en Excel avanzado al equipo.'
        }
    }
}

MANEJO_PUC_AUX_CONTABLE = {
    'pregunta': 'MANEJO DEL PUC (Plan Único de Cuentas)',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina el PUC. Clasifica incorrectamente transacciones. No conoce catálogo de cuentas. Esto genera errores contables graves. **Acción requerida:** Estudio urgente del PUC.',
            'plan_mejora': 'Estudiar intensivamente el PUC comercial. Practicar clasificación de transacciones diarias. Mentoría con contador sobre uso del PUC. Crear guía personal de cuentas más usadas.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento limitado del PUC. Clasifica transacciones básicas pero comete errores en casos especiales. Requiere consultar frecuentemente. **Recomendación:** Debe fortalecer conocimiento del PUC.',
            'plan_mejora': 'Estudiar PUC con enfoque en cuentas del giro del negocio. Practicar clasificación de casos complejos. Crear matriz de cuentas frecuentes.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Manejo satisfactorio del PUC. Clasifica correctamente transacciones comunes. Ocasionalmente consulta para casos especiales. **Oportunidad de mejora:** Puede dominar casos complejos.',
            'plan_mejora': 'Profundizar en cuentas especiales del PUC. Estudiar casos complejos de clasificación. Mantenerse actualizado en cambios del PUC.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen dominio del PUC. Clasifica correctamente la mayoría de transacciones. Conoce bien catálogo de cuentas del negocio. **Fortaleza reconocida:** Sólido conocimiento del PUC.',
            'plan_mejora': 'Mantener actualización del PUC. Capacitar a otros en uso correcto. Documentar casos especiales de clasificación.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente dominio del PUC. Clasifica perfectamente todo tipo de transacciones. Es referente en consultas sobre cuentas contables. **Fortaleza destacada:** Experto en PUC.',
            'plan_mejora': 'Mantener excelencia. Liderar capacitación en PUC. Crear guía de clasificación contable para la empresa.'
        }
    }
}

MANEJO_SOFTWARE_CONTABLE_AUX_CONTABLE = {
    'pregunta': 'MANEJO DEL SOFTWARE CONTABLE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No domina el software contable. Dificultades para registrar facturas y generar informes. No utiliza eficientemente el sistema. **Acción requerida:** Capacitación urgente en software contable.',
            'plan_mejora': 'Capacitación intensiva en software contable de la empresa. Practicar registro de diferentes tipos de transacciones. Aprender generación de todos los informes. Solicitar acompañamiento técnico.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo limitado del software. Registra transacciones básicas pero con dificultades en casos complejos. No domina todas las funcionalidades. **Recomendación:** Debe mejorar dominio del sistema.',
            'plan_mejora': 'Capacitación en funcionalidades avanzadas del software. Practicar generación de informes. Aprender atajos y mejores prácticas del sistema.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Manejo satisfactorio del software contable. Registra transacciones correctamente. Genera informes básicos. **Oportunidad de mejora:** Puede optimizar uso del sistema.',
            'plan_mejora': 'Aprender funcionalidades avanzadas. Optimizar velocidad de registro. Dominar generación de todos los informes.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen dominio del software contable. Registra eficientemente todo tipo de transacciones. Genera informes con facilidad. **Fortaleza reconocida:** Manejo eficiente del sistema.',
            'plan_mejora': 'Mantener dominio del sistema. Capacitar a otros usuarios. Proponer mejoras en configuración del software.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente dominio del software. Utiliza todas las funcionalidades eficientemente. Genera informes complejos. Es referente técnico del sistema. **Fortaleza destacada:** Experto en software contable.',
            'plan_mejora': 'Mantener excelencia. Liderar capacitación en software. Ser super usuario y soporte técnico interno.'
        }
    }
}

CONOCIMIENTO_NORMAS_CONTABLES_AUX_CONTABLE = {
    'pregunta': 'CONOCIMIENTO DE NORMAS CONTABLES (NIIF BÁSICA)',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No conoce normas contables. Desconoce NIIF básica y principios contables. Esto genera registros incorrectos. **Acción requerida:** Estudio urgente de normativa contable.',
            'plan_mejora': 'Estudiar NIIF para Pymes. Capacitación en principios contables básicos. Asistir a seminarios de actualización normativa. Certificación en normas contables.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento limitado de normas contables. Conoce principios básicos pero no domina NIIF. Requiere orientación constante. **Recomendación:** Debe estudiar normativa vigente.',
            'plan_mejora': 'Estudiar NIIF aplicables al negocio. Asistir a capacitaciones de actualización normativa. Practicar aplicación de normas en casos reales.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Conocimiento satisfactorio de normas contables. Comprende principios básicos y NIIF fundamentales. **Oportunidad de mejora:** Puede profundizar en normativa específica.',
            'plan_mejora': 'Profundizar en NIIF específicas del sector. Mantenerse actualizado en cambios normativos. Estudiar casos de aplicación práctica.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen conocimiento de normas contables. Comprende bien NIIF básica y principios contables. Aplica correctamente normativa. **Fortaleza reconocida:** Sólido conocimiento normativo.',
            'plan_mejora': 'Mantener actualización normativa. Compartir conocimientos con equipo. Liderar aplicación de nuevas normas.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente conocimiento de normas contables. Domina NIIF y principios contables. Es referente en consultas normativas. **Fortaleza destacada:** Experto en normativa contable.',
            'plan_mejora': 'Mantener excelencia. Liderar capacitación en NIIF. Ser consultor interno de normativa contable.'
        }
    }
}


# =====================================================================
# FUNCIÓN DE CÁLCULO PONDERADO
# =====================================================================

def calcular_puntaje_ponderado_auxiliar_contable(respuestas):
    """
    Calcula el puntaje ponderado para Auxiliar Contable

    Distribución de pesos:
    - Competencias Organizacionales: 10% (3.33%, 3.33%, 3.34%)
    - Objetivos - El Hacer: 40%
    - Competencias Interpersonales - El Ser: 25% (8.33%, 8.33%, 8.34%)
    - Competencias Técnicas - El Saber: 25% (6.25% cada una, 4 preguntas)
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


# =====================================================================
# FUNCIÓN DE GENERACIÓN DE PLAN DE MEJORA
# =====================================================================


def formatear_comentarios_evaluador(respuesta):
    """
    Formatea los comentarios del evaluador para el plan de mejora
    """
    comentarios = ""
    if respuesta.comentarios_evaluador:
        comentarios += f"   💬 Comentario del evaluador: {respuesta.comentarios_evaluador}\n"
    return comentarios


def generar_plan_mejora_auxiliar_contable(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Auxiliar Contable
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
║                           AUXILIAR CONTABLE                                  ║
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
        2: 'trabajo_en_equipo',
        3: 'mejora_continua',
        4: 'objetivos',
        5: 'compromiso_responsabilidad',
        6: 'atencion_detalle',
        7: 'planeacion_organizacion',
        8: 'manejo_office',
        9: 'manejo_puc',
        10: 'manejo_software_contable',
        11: 'conocimiento_normas_contables'
    }

    # Mapeo de claves a diccionarios de datos
    RESPUESTAS_AUXILIAR_CONTABLE = {
        'comunicacion': COMUNICACION_AUX_CONTABLE,
        'trabajo_en_equipo': TRABAJO_EQUIPO_AUX_CONTABLE,
        'mejora_continua': MEJORA_CONTINUA_AUX_CONTABLE,
        'objetivos': OBJETIVOS_AUX_CONTABLE,
        'compromiso_responsabilidad': COMPROMISO_RESPONSABILIDAD_AUX_CONTABLE,
        'atencion_detalle': ATENCION_DETALLE_AUX_CONTABLE,
        'planeacion_organizacion': PLANEACION_ORGANIZACION_AUX_CONTABLE,
        'manejo_office': MANEJO_OFFICE_AUX_CONTABLE,
        'manejo_puc': MANEJO_PUC_AUX_CONTABLE,
        'manejo_software_contable': MANEJO_SOFTWARE_CONTABLE_AUX_CONTABLE,
        'conocimiento_normas_contables': CONOCIMIENTO_NORMAS_CONTABLES_AUX_CONTABLE
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
            if clave_competencia and clave_competencia in RESPUESTAS_AUXILIAR_CONTABLE:
                competencia_data = RESPUESTAS_AUXILIAR_CONTABLE[clave_competencia]
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
