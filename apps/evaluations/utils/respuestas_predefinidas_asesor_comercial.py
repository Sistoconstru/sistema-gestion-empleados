"""
Respuestas predefinidas y lógica de evaluación para Asesor Comercial
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

COMUNICACION_ASESOR_COMERCIAL = {
    'pregunta': 'COMUNICACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** La comunicación presenta deficiencias graves. Las propuestas comerciales son confusas y contienen errores. No comunica efectivamente con clientes ni equipo. **Acción requerida:** Mejora urgente en comunicación comercial.',
            'plan_mejora': 'Participar en taller de comunicación comercial efectiva. Usar plantillas estándar para propuestas. Practicar escucha activa en reuniones comerciales.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La comunicación es básica pero insuficiente para el cargo. Las presentaciones comerciales requieren múltiples revisiones. Debe mejorar comunicación con clientes y equipo sobre oportunidades comerciales.',
            'plan_mejora': 'Desarrollar habilidades de presentación comercial. Practicar pitch de productos. Mejorar redacción de propuestas de valor.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Se comunica adecuadamente con clientes. Las propuestas son generalmente claras aunque ocasionalmente requieren ajustes. Es receptivo a observaciones. **Oportunidad:** Mayor claridad en comunicación de valor agregado.',
            'plan_mejora': 'Perfeccionar técnicas de storytelling comercial. Desarrollar presentaciones de impacto. Comunicar proactivamente oportunidades de negocio.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Comunica efectivamente propuestas comerciales. Sus presentaciones son claras, persuasivas y profesionales. Facilita comprensión del valor de productos/servicios a clientes. **Fortaleza reconocida:** Comunicador efectivo.',
            'plan_mejora': 'Mantener excelencia comunicativa. Capacitar al equipo comercial en comunicación efectiva. Liderar presentaciones clave a clientes estratégicos.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente comunicador comercial. Sus propuestas son impecables y persuasivas. Es referente en comunicación con clientes complejos. **Fortaleza destacada:** Comunicación excepcional.',
            'plan_mejora': 'Mantener excelencia. Crear guías de comunicación comercial para el área. Ser mentor en técnicas de comunicación persuasiva.'
        }
    }
}

TRABAJO_EQUIPO_ASESOR_COMERCIAL = {
    'pregunta': 'TRABAJO EN EQUIPO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No trabaja efectivamente con el equipo comercial. Se aísla y no comparte información sobre clientes u oportunidades. No contribuye a objetivos del equipo. **Acción requerida:** Desarrollar competencias colaborativas urgentemente.',
            'plan_mejora': 'Participar en actividades de integración del equipo comercial. Compartir mejores prácticas de ventas. Colaborar activamente en cierres comerciales complejos.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El trabajo en equipo es limitado. Comparte información solo cuando se solicita. No apoya proactivamente a otros asesores. **Recomendación:** Mejorar disposición colaborativa.',
            'plan_mejora': 'Integrarse más en el equipo. Compartir leads y oportunidades. Apoyar en reuniones comerciales críticas.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Trabaja adecuadamente con el equipo. Comparte información cuando es necesario. Contribuye satisfactoriamente a objetivos comerciales. **Oportunidad:** Mayor proactividad en colaboración comercial.',
            'plan_mejora': 'Liderar iniciativas de ventas cruzadas. Crear sinergias con otras áreas. Compartir estrategias exitosas de cierre.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Trabaja muy bien en equipo. Comparte proactivamente oportunidades y conocimientos. Apoya a otros asesores y contribuye activamente a metas colectivas. **Fortaleza reconocida:** Excelente colaborador.',
            'plan_mejora': 'Mantener alto nivel de colaboración. Servir como enlace con otras áreas. Documentar mejores prácticas de trabajo colaborativo.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente trabajo en equipo y liderazgo comercial. Es modelo de colaboración. Comparte generosamente estrategias, apoya constantemente y eleva el nivel del equipo. **Fortaleza destacada:** Líder natural del equipo comercial.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de desarrollo comercial del equipo. Facilitar espacios de colaboración interdepartamental.'
        }
    }
}

MEJORA_CONTINUA_ASESOR_COMERCIAL = {
    'pregunta': 'MEJORA CONTINUA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No demuestra compromiso con mejora continua. Realiza procesos comerciales sin buscar optimización. No propone mejoras ni innovaciones. **Acción requerida:** Desarrollar mentalidad de mejora continua.',
            'plan_mejora': 'Capacitación en mejora continua de procesos comerciales. Establecer métricas de efectividad comercial. Proponer al menos una mejora trimestral en proceso de ventas.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** El enfoque de mejora continua es limitado. Cumple procedimientos sin cuestionarlos. Propone pocas mejoras en proceso comercial. **Recomendación:** Fortalecer compromiso con optimización.',
            'plan_mejora': 'Implementar ciclos de revisión de proceso de ventas. Proponer mejoras en seguimiento comercial. Benchmarking con mejores prácticas del sector.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Realiza procesos comerciales bajo estándares aceptables. Ocasionalmente propone mejoras. **Oportunidad:** Mayor proactividad en optimización de gestión comercial.',
            'plan_mejora': 'Liderar proyecto de optimización de proceso comercial específico. Proponer automatizaciones en seguimiento de clientes. Investigar mejores prácticas de ventas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Compromiso activo con mejora continua. Propone regularmente mejoras en procesos comerciales. Implementa estándares de calidad altos. **Fortaleza reconocida:** Agente de cambio en el área.',
            'plan_mejora': 'Mantener proactividad. Liderar implementación de CRM o herramientas comerciales. Formar parte de comité de mejora continua.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente en mejora continua. Propone e implementa mejoras significativas constantemente. Ha optimizado procesos clave del área comercial. **Fortaleza destacada:** Innovador en gestión comercial.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación digital del área comercial. Diseñar programa de mejora continua para toda el área de ventas.'
        }
    }
}

# =====================================================================
# OBJETIVOS - EL HACER (40%)
# =====================================================================

OBJETIVOS_ASESOR_COMERCIAL = {
    'pregunta': 'OBJETIVOS - GESTIÓN COMERCIAL',
    'respuestas': {
        1: {
            'retroalimentacion': '**Desempeño crítico:** No alcanza metas de ventas. La gestión de cartera es deficiente. No logra cerrar negocios ni generar oportunidades de fidelización. El impacto comercial es muy bajo. **Acción urgente:** Plan de acción inmediato requerido.',
            'plan_mejora': 'Implementar plan de acción comercial intensivo. Capacitación en cierre de ventas. Acompañamiento diario por coordinador comercial. Establecer metas semanales de actividades comerciales.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Alcanza menos del 70% de la meta de ventas. El seguimiento de cotizaciones es irregular. Cierra pocos negocios. La fidelización de clientes es limitada. **Recomendación:** Mejorar gestión comercial integral.',
            'plan_mejora': 'Curso de técnicas de ventas y negociación. Implementar sistema de seguimiento estructurado. Establecer rutina de prospección diaria. Acompañamiento en visitas comerciales clave.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Alcanza entre 70-90% de la meta de ventas. Gestiona adecuadamente la cartera de clientes. Cierra negocios satisfactoriamente. La fidelización es aceptable. **Oportunidad:** Aumentar efectividad comercial.',
            'plan_mejora': 'Desarrollar técnicas de venta consultiva. Mejorar conversión de cotizaciones. Implementar estrategias de upselling y cross-selling. Fortalecer seguimiento post-venta.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Cumple o supera la meta de ventas (90-110%). Gestiona efectivamente la cartera. Cierra negocios consistentemente. Logra buena satisfacción y fidelización de clientes. **Fortaleza reconocida:** Gestor comercial efectivo.',
            'plan_mejora': 'Mantener alto desempeño. Enfocarse en clientes estratégicos de mayor valor. Liderar prospección de nuevos sectores. Compartir estrategias exitosas con el equipo.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Supera consistentemente la meta de ventas (+110%). Amplía significativamente la cartera. Cierra negocios complejos y estratégicos. Genera alta fidelización y referencias. **Fortaleza destacada:** Excelencia comercial.',
            'plan_mejora': 'Mantener excelencia. Liderar gestión de cuentas clave. Desarrollar nuevos segmentos de mercado. Ser mentor de asesores junior en gestión comercial integral.'
        }
    }
}

# =====================================================================
# COMPETENCIAS INTERPERSONALES - EL SER (25%)
# =====================================================================

ORIENTACION_CLIENTE_ASESOR_COMERCIAL = {
    'pregunta': 'ORIENTACIÓN AL CLIENTE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No demuestra orientación al cliente. No detecta ni anticipa necesidades. El seguimiento post-venta es inexistente. Los clientes reportan insatisfacción. **Acción requerida:** Desarrollar enfoque al cliente urgentemente.',
            'plan_mejora': 'Capacitación en servicio al cliente y orientación comercial. Implementar rutina de seguimiento post-venta. Obtener retroalimentación de clientes sobre servicio.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La orientación al cliente es básica. Detecta necesidades solo cuando son evidentes. El seguimiento post-venta es irregular. **Recomendación:** Fortalecer enfoque proactivo al cliente.',
            'plan_mejora': 'Desarrollar escucha activa en reuniones comerciales. Implementar calendario de seguimiento post-venta. Anticipar necesidades estacionales de clientes.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Demuestra orientación al cliente adecuada. Detecta necesidades básicas. Hace seguimiento post-venta ocasional. **Oportunidad:** Anticipar necesidades antes de que el cliente las manifieste.',
            'plan_mejora': 'Perfeccionar técnicas de identificación de necesidades implícitas. Crear plan de seguimiento sistemático post-venta. Estudiar tendencias del negocio del cliente.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente orientación al cliente. Detecta y anticipa necesidades efectivamente. Hace seguimiento post-venta consistente. Los clientes expresan alta satisfacción. **Fortaleza reconocida:** Centrado en el cliente.',
            'plan_mejora': 'Mantener enfoque al cliente. Desarrollar relaciones estratégicas de largo plazo. Implementar programa de voz del cliente con clientes clave.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Orientación excepcional al cliente. Anticipa necesidades antes de que surjan. El seguimiento post-venta es proactivo y genera valor adicional. Clientes lo reconocen como asesor de confianza. **Fortaleza destacada:** Champion del cliente.',
            'plan_mejora': 'Mantener excelencia. Desarrollar programa de experiencia del cliente. Ser referente en gestión de relaciones comerciales de largo plazo.'
        }
    }
}

PERSUASION_INFLUENCIA_ASESOR_COMERCIAL = {
    'pregunta': 'PERSUASIÓN E INFLUENCIA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No logra persuadir ni influenciar clientes. Las negociaciones fracasan frecuentemente. No genera confianza. Compromete márgenes sin lograr cierres. **Acción requerida:** Desarrollar habilidades de persuasión urgentemente.',
            'plan_mejora': 'Curso intensivo de técnicas de persuasión y negociación. Practicar manejo de objeciones con role-playing. Acompañamiento en negociaciones críticas.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La capacidad de persuasión es limitada. Genera confianza básica pero no influye en decisiones complejas. En negociaciones acepta rápidamente posición del cliente. **Recomendación:** Fortalecer técnicas de persuasión.',
            'plan_mejora': 'Desarrollar argumentación basada en valor. Practicar escucha activa para identificar motivadores. Mejorar manejo de objeciones comerciales.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Demuestra capacidad de persuasión adecuada. Genera confianza con la mayoría de clientes. En negociaciones logra acuerdos aceptables. **Oportunidad:** Mejorar influencia en decisiones estratégicas.',
            'plan_mejora': 'Perfeccionar técnicas de negociación ganar-ganar. Desarrollar argumentación consultiva. Estudiar psicología del comprador en sector específico.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Alta capacidad de persuasión e influencia. Genera confianza sólida con clientes. Cierra negociaciones generando valor sin comprometer márgenes. **Fortaleza reconocida:** Negociador efectivo.',
            'plan_mejora': 'Mantener efectividad. Liderar negociaciones de cuentas estratégicas. Capacitar equipo en técnicas de persuasión consultiva.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Capacidad excepcional de persuasión e influencia. Genera confianza inmediata y profunda. Cierra negociaciones complejas con resultados óptimos para todas las partes. **Fortaleza destacada:** Maestro de la negociación.',
            'plan_mejora': 'Mantener excelencia. Ser mentor en negociación estratégica. Documentar mejores prácticas de persuasión e influencia comercial.'
        }
    }
}

ORIENTACION_RESULTADOS_ASESOR_COMERCIAL = {
    'pregunta': 'ORIENTACIÓN A RESULTADOS',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No demuestra orientación a resultados. No cumple metas de ventas. No mantiene actualizado el pipeline de oportunidades. Falta sentido de urgencia comercial. **Acción requerida:** Desarrollar enfoque a resultados urgentemente.',
            'plan_mejora': 'Establecer metas diarias y semanales específicas. Implementar tablero de control comercial. Reuniones diarias de seguimiento de actividades y resultados.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La orientación a resultados es limitada. Cumple parcialmente metas. El pipeline de oportunidades está desactualizado. **Recomendación:** Fortalecer enfoque a resultados comerciales.',
            'plan_mejora': 'Implementar sistema de seguimiento de metas. Actualizar CRM diariamente. Establecer rutina comercial estructurada orientada a resultados.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Demuestra orientación a resultados adecuada. Cumple satisfactoriamente metas de ventas. Mantiene pipeline actualizado generalmente. **Oportunidad:** Mayor sentido de urgencia en cierre de oportunidades.',
            'plan_mejora': 'Perfeccionar gestión del tiempo comercial. Priorizar oportunidades de alto valor. Implementar seguimiento semanal de conversión de pipeline.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Alta orientación a resultados. Cumple o supera consistentemente metas de ventas. Mantiene pipeline actualizado y activo. Demuestra sentido de urgencia apropiado. **Fortaleza reconocida:** Enfocado en resultados.',
            'plan_mejora': 'Mantener alto desempeño. Optimizar conversión de oportunidades. Liderar iniciativas de aceleración de cierres comerciales.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Orientación excepcional a resultados. Supera consistentemente metas. Su pipeline es modelo de gestión comercial. Demuestra sentido de urgencia óptimo sin comprometer calidad. **Fortaleza destacada:** Máquina de resultados.',
            'plan_mejora': 'Mantener excelencia. Compartir metodología de gestión de pipeline. Liderar programa de aceleración comercial para el equipo.'
        }
    }
}

INICIATIVA_PROACTIVIDAD_ASESOR_COMERCIAL = {
    'pregunta': 'INICIATIVA Y PROACTIVIDAD',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No demuestra iniciativa ni proactividad. Espera instrucciones constantes. No prospera nuevos clientes. No identifica oportunidades comerciales. **Acción requerida:** Desarrollar autonomía comercial urgentemente.',
            'plan_mejora': 'Establecer metas de prospección diaria. Desarrollar plan de prospección autónomo. Capacitación en identificación de oportunidades comerciales.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** La iniciativa es limitada. Requiere dirección frecuente. La prospección de nuevos clientes es mínima. **Recomendación:** Fortalecer proactividad comercial.',
            'plan_mejora': 'Implementar rutina de prospección autónoma. Proponer estrategias de fidelización. Investigar nuevos mercados potenciales.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Demuestra iniciativa adecuada. Prospera nuevos clientes ocasionalmente. Identifica algunas oportunidades comerciales. **Oportunidad:** Mayor proactividad en generación de oportunidades.',
            'plan_mejora': 'Perfeccionar técnicas de prospección proactiva. Desarrollar estrategias innovadoras de fidelización. Proponer mejoras en proceso comercial.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Alta iniciativa y proactividad. Prospera consistentemente nuevos clientes sin esperar instrucciones. Propone estrategias efectivas de fidelización. Identifica oportunidades valiosas. **Fortaleza reconocida:** Comercial autónomo.',
            'plan_mejora': 'Mantener proactividad. Desarrollar nuevos segmentos de mercado. Liderar iniciativas de innovación comercial.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Iniciativa y proactividad excepcionales. Constantemente identifica y cierra nuevas oportunidades. Propone e implementa estrategias innovadoras. Es modelo de autonomía comercial. **Fortaleza destacada:** Emprendedor comercial.',
            'plan_mejora': 'Mantener excelencia. Liderar desarrollo de nuevos mercados. Ser mentor en proactividad y autonomía comercial para el equipo.'
        }
    }
}

# =====================================================================
# COMPETENCIAS TÉCNICAS - EL SABER (25%)
# =====================================================================

CONOCIMIENTO_PRODUCTO_ASESOR_COMERCIAL = {
    'pregunta': 'CONOCIMIENTO DEL PRODUCTO/SERVICIO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Conocimiento del portafolio muy deficiente. No puede explicar características ni beneficios. No identifica aplicaciones. Los clientes perciben falta de expertise. **Acción requerida:** Capacitación urgente en productos/servicios.',
            'plan_mejora': 'Capacitación intensiva en todo el portafolio. Estudiar fichas técnicas y aplicaciones. Acompañamiento en visitas técnicas con expertos de producto.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico del portafolio pero insuficiente. Explica características superficialmente. Le cuesta identificar ventajas competitivas. **Recomendación:** Profundizar conocimiento técnico.',
            'plan_mejora': 'Estudiar casos de aplicación exitosos. Capacitación en características técnicas. Benchmarking con competencia para identificar ventajas.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Conoce adecuadamente el portafolio principal. Explica características y beneficios satisfactoriamente. Identifica aplicaciones básicas. **Oportunidad:** Profundizar en ventajas competitivas diferenciadoras.',
            'plan_mejora': 'Especializarse en productos de mayor margen. Desarrollar argumentario de ventajas competitivas. Estudiar tendencias del mercado y nuevas aplicaciones.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Conocimiento profundo del portafolio. Explica técnicamente características, beneficios y aplicaciones. Identifica claramente ventajas competitivas. Los clientes reconocen su expertise. **Fortaleza reconocida:** Experto en productos.',
            'plan_mejora': 'Mantener actualización constante. Ser referente técnico interno. Capacitar equipo en conocimiento de productos.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Conocimiento excepcional del portafolio. Domina a profundidad características, aplicaciones y ventajas competitivas. Es consultor de confianza para clientes en soluciones técnicas. **Fortaleza destacada:** Autoridad técnica.',
            'plan_mejora': 'Mantener excelencia. Desarrollar material técnico-comercial. Liderar capacitación de nuevos productos al equipo comercial.'
        }
    }
}

TECNICAS_VENTAS_ASESOR_COMERCIAL = {
    'pregunta': 'TÉCNICAS DE VENTAS Y NEGOCIACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No maneja técnicas de venta consultiva. El manejo de objeciones es deficiente. Los cierres son muy poco efectivos. **Acción requerida:** Capacitación urgente en técnicas de ventas.',
            'plan_mejora': 'Curso de venta consultiva y manejo de objeciones. Practicar técnicas de cierre con role-playing. Acompañamiento en proceso completo de ventas.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo básico de técnicas de venta. El enfoque consultivo es limitado. Le cuesta manejar objeciones complejas. **Recomendación:** Fortalecer metodología de ventas.',
            'plan_mejora': 'Capacitación en metodología SPIN o similar. Desarrollar habilidad de manejo de objeciones. Practicar técnicas de cierre efectivo.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Maneja adecuadamente técnicas de venta consultiva. El manejo de objeciones es satisfactorio. Logra cierres efectivos en ventas estándar. **Oportunidad:** Perfeccionar cierre de ventas complejas.',
            'plan_mejora': 'Especializar en venta consultiva avanzada. Perfeccionar manejo de objeciones difíciles. Estudiar técnicas de cierre de negocios complejos.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Dominio sólido de técnicas de venta consultiva. Maneja efectivamente objeciones. Cierra negocios con alta efectividad. **Fortaleza reconocida:** Vendedor consultivo.',
            'plan_mejora': 'Mantener efectividad. Especializarse en venta estratégica de cuentas clave. Capacitar equipo en técnicas de ventas consultivas.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Maestría en técnicas de venta consultiva. El manejo de objeciones es ejemplar. Cierra negocios complejos con excelencia. Es referente en metodología de ventas. **Fortaleza destacada:** Maestro de ventas.',
            'plan_mejora': 'Mantener excelencia. Desarrollar metodología propia de ventas. Liderar programa de formación en técnicas de ventas para el equipo.'
        }
    }
}

CUMPLIMIENTO_PRESUPUESTO_ASESOR_COMERCIAL = {
    'pregunta': 'CUMPLIMIENTO DE PRESUPUESTO Y GESTIÓN DE CARTERA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Cumplimiento muy bajo del presupuesto de ventas (<60%). La gestión de cartera es deficiente. Alto porcentaje de cartera vencida. **Acción requerida:** Plan de acción comercial y financiero urgente.',
            'plan_mejora': 'Establecer plan de recuperación de ventas. Implementar gestión disciplinada de cartera. Capacitación en análisis financiero de clientes y cobros.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Cumplimiento bajo del presupuesto (60-80%). La gestión de cartera tiene oportunidades de mejora. Algunas facturas se vencen. **Recomendación:** Mejorar efectividad comercial y financiera.',
            'plan_mejora': 'Implementar seguimiento semanal de presupuesto. Establecer rutina de gestión de cartera. Coordinar con área financiera en prevención de vencimientos.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Cumple presupuesto satisfactoriamente (80-95%). La gestión de cartera es adecuada. La mayoría de facturas se recaudan en tiempo. **Oportunidad:** Optimizar gestión integral comercial-financiera.',
            'plan_mejora': 'Perfeccionar análisis de rentabilidad por cliente. Implementar alertas tempranas de vencimiento. Optimizar mix de productos vendidos.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Cumple o supera presupuesto (95-110%). Excelente gestión de cartera. Alto porcentaje de recaudo en tiempo. Equilibra ventas con rentabilidad. **Fortaleza reconocida:** Gestor comercial-financiero efectivo.',
            'plan_mejora': 'Mantener alto desempeño. Enfocarse en clientes de mayor rentabilidad. Optimizar plazos de pago sin afectar competitividad.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Supera consistentemente presupuesto (+110%). Gestión de cartera ejemplar. Recaudo prácticamente 100% en tiempo. Maximiza rentabilidad de ventas. **Fortaleza destacada:** Excelencia comercial-financiera.',
            'plan_mejora': 'Mantener excelencia. Compartir mejores prácticas de gestión de cartera. Liderar desarrollo de políticas comerciales rentables.'
        }
    }
}

MANEJO_OFFICE_ASESOR_COMERCIAL = {
    'pregunta': 'MANEJO DE OFFICE Y ELABORACIÓN DE COTIZACIONES',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Manejo muy deficiente de herramientas Office. Las cotizaciones contienen errores y están mal presentadas. Los informes comerciales son inadecuados. **Acción requerida:** Capacitación urgente en Office.',
            'plan_mejora': 'Capacitación intensiva en Excel para cotizaciones. Aprender uso de plantillas de PowerPoint comerciales. Mejorar redacción de propuestas en Word.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo básico de Office pero insuficiente. Las cotizaciones son funcionales pero requieren revisión. Las presentaciones son simples. **Recomendación:** Mejorar dominio de herramientas.',
            'plan_mejora': 'Curso de Excel intermedio (fórmulas, tablas dinámicas). Desarrollar habilidades en PowerPoint para presentaciones de impacto. Mejorar formato de propuestas.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Manejo adecuado de Office. Las cotizaciones son correctas y profesionales. Los informes son satisfactorios. **Oportunidad:** Optimizar uso de herramientas para mayor impacto comercial.',
            'plan_mejora': 'Perfeccionar uso de Excel para análisis comercial. Crear presentaciones de alto impacto en PowerPoint. Desarrollar propuestas comerciales persuasivas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Buen dominio de Office. Las cotizaciones son precisas, profesionales y de presentación impecable. Los informes comerciales son claros y analíticos. **Fortaleza reconocida:** Competente en herramientas.',
            'plan_mejora': 'Mantener calidad. Desarrollar plantillas avanzadas de cotización. Crear dashboards comerciales en Excel para seguimiento.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Dominio avanzado de Office. Las cotizaciones son impecables y persuasivas. Las presentaciones son de nivel ejecutivo. Los informes son analíticos y profesionales. **Fortaleza destacada:** Experto en herramientas comerciales.',
            'plan_mejora': 'Mantener excelencia. Crear biblioteca de plantillas comerciales para el equipo. Capacitar en uso avanzado de herramientas Office.'
        }
    }
}


# =====================================================================
# FUNCIONES DE CÁLCULO Y GENERACIÓN DE PLANES
# =====================================================================

def calcular_puntaje_ponderado_asesor_comercial(respuestas):
    """
    Calcula el puntaje ponderado para la evaluación de Asesor Comercial.

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

            # Actualizar detalle
            detalle_categorias[categoria]['porcentaje'] = round(porcentaje_categoria, 2)

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


def generar_plan_mejora_asesor_comercial(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera el plan de mejora personalizado para Asesor Comercial
    siguiendo el formato estándar con estructura numerada
    """

    # Diccionario de competencias
    competencias = {
        'COMUNICACIÓN': COMUNICACION_ASESOR_COMERCIAL,
        'TRABAJO EN EQUIPO': TRABAJO_EQUIPO_ASESOR_COMERCIAL,
        'MEJORA CONTINUA': MEJORA_CONTINUA_ASESOR_COMERCIAL,
        'Gestionar y ampliar la cartera de clientes': OBJETIVOS_ASESOR_COMERCIAL,
        'ORIENTACIÓN AL CLIENTE': ORIENTACION_CLIENTE_ASESOR_COMERCIAL,
        'PERSUASIÓN E INFLUENCIA': PERSUASION_INFLUENCIA_ASESOR_COMERCIAL,
        'ORIENTACIÓN A RESULTADOS': ORIENTACION_RESULTADOS_ASESOR_COMERCIAL,
        'INICIATIVA Y PROACTIVIDAD': INICIATIVA_PROACTIVIDAD_ASESOR_COMERCIAL,
        'CONOCIMIENTO DEL PRODUCTO': CONOCIMIENTO_PRODUCTO_ASESOR_COMERCIAL,
        'TÉCNICAS DE VENTAS Y NEGOCIACIÓN': TECNICAS_VENTAS_ASESOR_COMERCIAL,
        'CUMPLIMIENTO DE PRESUPUESTO': CUMPLIMIENTO_PRESUPUESTO_ASESOR_COMERCIAL,
        'MANEJO DE OFFICE': MANEJO_OFFICE_ASESOR_COMERCIAL,
    }

    # Encabezado
    plan = "╔═══════════════════════════════════════════════════════════════════════════════╗\n"
    plan += "║            PLAN DE MEJORA - EVALUACIÓN ANUAL ASESOR COMERCIAL                ║\n"
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
    plan += "1. Revisar este plan con el empleado en reunión de retroalimentación\n"
    plan += "2. Priorizar acciones según áreas de mayor impacto\n"
    plan += "3. Establecer cronograma de seguimiento trimestral\n"
    plan += "4. Documentar avances en cada revisión\n"
    plan += "═══════════════════════════════════════════════════════════════════════════════\n"

    return plan
