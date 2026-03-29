"""
Respuestas predefinidas para evaluación anual de Auxiliar de Tesorería
Sistema de calificación: Escala 1-5 (Muy bajo a Muy alto)
Total de competencias: 12
Ponderación por categorías:
  - Competencias Organizacionales (10%): Preguntas 1-3
  - Objetivos (40%): Pregunta 4
  - Competencias Interpersonales (25%): Preguntas 5-7
  - Competencias Técnicas (25%): Preguntas 8-12
"""


# =============================================================================
# RESPUESTAS PREDEFINIDAS POR COMPETENCIA
# =============================================================================

RESPUESTAS_AUXILIAR_TESORERIA = {
    # =========================================================================
    # CATEGORÍA: COMPETENCIAS ORGANIZACIONALES (10%)
    # =========================================================================

    'comunicacion': {
        1: {
            'evaluacion': 'Presenta dificultades significativas para comunicarse de manera efectiva. Sus reportes y correos contienen errores frecuentes, información incompleta o poco clara. Raramente escucha con atención y suele malinterpretar instrucciones.',
            'plan_accion': [
                'Participar en taller de comunicación escrita enfocado en redacción de correos profesionales y reportes financieros.',
                'Realizar ejercicios prácticos de escucha activa con retroalimentación del supervisor.',
                'Utilizar plantillas estandarizadas para reportes de caja y movimientos bancarios.',
                'Solicitar revisión previa de comunicaciones importantes antes de enviarlas.'
            ]
        },
        2: {
            'evaluacion': 'Su comunicación es básica pero presenta deficiencias. A veces sus mensajes son ambiguos o requieren aclaraciones adicionales. Escucha parcialmente pero no siempre comprende las instrucciones a la primera.',
            'plan_accion': [
                'Desarrollar hábito de confirmar comprensión de instrucciones mediante parafraseo.',
                'Mejorar estructura de correos electrónicos utilizando formato: asunto claro + contexto + solicitud específica.',
                'Practicar comunicación asertiva en situaciones de requerimientos urgentes de pago.',
                'Recibir retroalimentación quincenal sobre claridad de sus reportes.'
            ]
        },
        3: {
            'evaluacion': 'Se comunica de manera aceptable. Sus reportes son generalmente claros aunque ocasionalmente requieren ajustes menores. Escucha con atención la mayoría del tiempo y responde adecuadamente a las solicitudes.',
            'plan_accion': [
                'Perfeccionar habilidades de síntesis para reportes ejecutivos mensuales.',
                'Desarrollar capacidad de anticipar preguntas frecuentes en sus comunicaciones.',
                'Mantener consistencia en formato y tono profesional de todas las comunicaciones.',
                'Fortalecer comunicación proactiva informando novedades antes de que se soliciten.'
            ]
        },
        4: {
            'evaluacion': 'Se comunica efectivamente tanto verbal como por escrito. Sus reportes son claros, precisos y oportunos. Escucha activamente y es receptivo a sugerencias. Mantiene informado al equipo sobre el estado de pagos y movimientos importantes.',
            'plan_accion': [
                'Desarrollar habilidades de comunicación en situaciones de conflicto (proveedores en mora, diferencias en pagos).',
                'Profundizar en técnicas de presentación de información financiera a diferentes audiencias.',
                'Servir como referente de buenas prácticas de comunicación para nuevos miembros del equipo.',
                'Participar en comité de mejora de procesos de comunicación del área financiera.'
            ]
        },
        5: {
            'evaluacion': 'Sobresale en comunicación efectiva. Sus reportes son ejemplares: claros, precisos, completos y oportunos. Escucha activamente, comprende diferentes perspectivas y adapta su comunicación a diferentes audiencias. Promueve una comunicación abierta y constructiva.',
            'plan_accion': [
                'Mentor en comunicación efectiva para otros auxiliares del área.',
                'Diseñar plantillas y guías de comunicación que puedan ser replicadas por el equipo.',
                'Liderar sesiones de mejora continua en comunicación del área financiera.',
                'Compartir mejores prácticas en reuniones departamentales.'
            ]
        }
    },

    'trabajo_en_equipo': {
        1: {
            'evaluacion': 'Trabaja de manera aislada y presenta dificultades para colaborar con otros. Raramente comparte información relevante con el equipo. Muestra resistencia a solicitudes de apoyo de compañeros.',
            'plan_accion': [
                'Participar en dinámicas de integración y trabajo colaborativo.',
                'Establecer rutina diaria de comunicación con compañeros del área.',
                'Asistir a reuniones semanales de equipo y participar activamente.',
                'Recibir mentoría sobre importancia de trabajo colaborativo en procesos financieros.'
            ]
        },
        2: {
            'evaluacion': 'Colabora ocasionalmente pero tiende a trabajar solo. Comparte información cuando se le solicita pero no de manera proactiva. Su apoyo a compañeros es limitado.',
            'plan_accion': [
                'Desarrollar cultura de compartir información relevante sin necesidad de que se solicite.',
                'Participar en al menos dos proyectos colaborativos trimestrales del área.',
                'Apoyar a compañeros en períodos de alta carga (cierre de mes, pago de nómina).',
                'Asistir a taller de trabajo en equipo y colaboración efectiva.'
            ]
        },
        3: {
            'evaluacion': 'Trabaja adecuadamente en equipo. Comparte información necesaria y colabora cuando se requiere. Contribuye a un ambiente de trabajo positivo aunque podría ser más proactivo en ofrecer apoyo.',
            'plan_accion': [
                'Aumentar iniciativa para apoyar a compañeros sin esperar solicitud explícita.',
                'Compartir conocimientos técnicos (manejo de plataformas bancarias, conciliaciones) con el equipo.',
                'Participar activamente en mejora de procesos conjuntos del área.',
                'Liderar al menos una iniciativa de mejora en colaboración con otras áreas.'
            ]
        },
        4: {
            'evaluacion': 'Excelente colaborador. Comparte activamente información, recursos y conocimientos con el equipo. Apoya proactivamente a sus compañeros y contribuye significativamente a los objetivos comunes del área.',
            'plan_accion': [
                'Servir como facilitador en proyectos que requieren coordinación entre áreas.',
                'Documentar procedimientos para facilitar incorporación de nuevos miembros.',
                'Participar en comités interdepartamentales de mejora continua.',
                'Desarrollar habilidades de liderazgo informal para fortalecer cohesión del equipo.'
            ]
        },
        5: {
            'evaluacion': 'Líder natural en trabajo colaborativo. Promueve activamente la cooperación, comparte generosamente su conocimiento y crea sinergias entre compañeros. Es modelo de trabajo en equipo y contribución a objetivos organizacionales.',
            'plan_accion': [
                'Liderar iniciativas de integración entre el área financiera y otras áreas.',
                'Mentor formal de nuevos auxiliares de tesorería.',
                'Diseñar y facilitar talleres internos de mejores prácticas.',
                'Participar en diseño de estrategias de fortalecimiento de cultura colaborativa.'
            ]
        }
    },

    'mejora_continua': {
        1: {
            'evaluacion': 'Realiza sus tareas de manera rutinaria sin buscar mejoras. No muestra interés en optimizar procesos. Presenta resistencia al cambio y a nuevas metodologías de trabajo.',
            'plan_accion': [
                'Participar en taller de introducción a mejora continua y metodologías ágiles.',
                'Identificar al menos una oportunidad de mejora mensual en sus procesos.',
                'Recibir mentoría sobre importancia de adaptación en entorno financiero cambiante.',
                'Asistir a sesiones de benchmarking sobre mejores prácticas en tesorería.'
            ]
        },
        2: {
            'evaluacion': 'Cumple con estándares mínimos de calidad. Ocasionalmente sugiere pequeñas mejoras pero no de manera consistente. Acepta cambios cuando se implementan pero no los promueve.',
            'plan_accion': [
                'Desarrollar visión crítica sobre procesos actuales identificando ineficiencias.',
                'Presentar al menos dos propuestas de mejora por trimestre al supervisor.',
                'Participar en proyectos piloto de nuevas herramientas o procesos.',
                'Capacitarse en herramientas tecnológicas que optimicen procesos de tesorería.'
            ]
        },
        3: {
            'evaluacion': 'Cumple con estándares de calidad establecidos. Propone mejoras ocasionalmente y se adapta bien a cambios en procesos y metodologías. Muestra apertura al aprendizaje.',
            'plan_accion': [
                'Aumentar frecuencia y profundidad de propuestas de mejora.',
                'Liderar implementación de al menos una mejora significativa por semestre.',
                'Capacitarse en metodologías de mejora continua (Kaizen, PDCA).',
                'Documentar lecciones aprendidas y mejores prácticas descubiertas.'
            ]
        },
        4: {
            'evaluacion': 'Comprometido activamente con la mejora continua. Identifica oportunidades de optimización y propone soluciones viables. Adopta proactivamente nuevas tecnologías y metodologías que mejoran la eficiencia.',
            'plan_accion': [
                'Liderar proyectos de innovación en procesos de tesorería.',
                'Investigar y proponer implementación de nuevas herramientas tecnológicas.',
                'Convertirse en referente de buenas prácticas para el área.',
                'Participar en grupos de trabajo de transformación digital del área financiera.'
            ]
        },
        5: {
            'evaluacion': 'Agente de cambio y mejora continua. Constantemente busca y propone optimizaciones significativas. Lidera implementación de mejoras y modernización de procesos. Es modelo de adaptabilidad y excelencia operativa.',
            'plan_accion': [
                'Diseñar estrategia de innovación para el área de tesorería.',
                'Mentor en metodologías de mejora continua para equipo financiero.',
                'Liderar benchmarking con otras organizaciones del sector.',
                'Presentar casos de éxito en foros departamentales o sectoriales.'
            ]
        }
    },

    # =========================================================================
    # CATEGORÍA: OBJETIVOS (40%)
    # =========================================================================

    'ejecutar_procesos_tesoreria': {
        1: {
            'evaluacion': 'Presenta deficiencias significativas en la ejecución de procesos de tesorería. Frecuentes errores en recaudos, pagos o consignaciones. Incumple plazos regularmente. Registros de caja y bancos con inconsistencias importantes. No mantiene custodia adecuada de recursos.',
            'plan_accion': [
                'Capacitación intensiva en procedimientos básicos de tesorería: recaudos, pagos, consignaciones.',
                'Supervisión diaria durante 30 días con revisión detallada de cada transacción.',
                'Implementar checklist obligatorio para cada proceso (pago, recaudo, consignación).',
                'Estudiar y aplicar procedimientos de control interno de tesorería.',
                'Recibir formación en manejo de efectivo y valores según política de seguridad.',
                'Establecer reuniones semanales de seguimiento con supervisor directo.'
            ]
        },
        2: {
            'evaluacion': 'Ejecuta procesos básicos de tesorería con supervisión. Comete errores ocasionales en pagos o registros que requieren corrección. A veces incumple fechas de pago o consignación. Conciliaciones bancarias con diferencias frecuentes que debe ajustar. Custodia de recursos aceptable pero mejorable.',
            'plan_accion': [
                'Reforzar capacitación en conciliaciones bancarias y análisis de diferencias.',
                'Implementar sistema de alertas para fechas de vencimiento de obligaciones.',
                'Desarrollar mayor atención al detalle mediante ejercicios prácticos.',
                'Mejorar organización de documentos soporte para agilizar procesos.',
                'Recibir retroalimentación semanal sobre calidad de registros contables.',
                'Participar en taller de gestión del tiempo y priorización de tareas.'
            ]
        },
        3: {
            'evaluacion': 'Ejecuta adecuadamente los procesos de recaudo, pagos y consignaciones. Registros de caja y bancos generalmente exactos y oportunos. Cumple la mayoría de obligaciones en fechas establecidas. Conciliaciones bancarias con diferencias menores que resuelve apropiadamente. Mantiene custodia adecuada de recursos.',
            'plan_accion': [
                'Reducir a cero los errores en transacciones mediante triple verificación.',
                'Optimizar tiempo de ejecución de conciliaciones bancarias.',
                'Desarrollar capacidad de identificar patrones en diferencias bancarias.',
                'Fortalecer conocimiento de normativa financiera y tributaria aplicable.',
                'Documentar procedimientos para estandarizar buenas prácticas.',
                'Ampliar autonomía en resolución de inconsistencias complejas.'
            ]
        },
        4: {
            'evaluacion': 'Ejecuta con alto nivel de exactitud y oportunidad todos los procesos de tesorería. Registros impecables de caja y bancos. Cumple sistemáticamente con fechas de pago sin generar mora. Conciliaciones bancarias precisas con mínimas o nulas diferencias. Excelente custodia de recursos y controles internos sólidos.',
            'plan_accion': [
                'Optimizar procesos mediante automatización de tareas repetitivas.',
                'Desarrollar indicadores de gestión para el área de tesorería.',
                'Proponer mejoras en procedimientos de control interno.',
                'Capacitarse en gestión de riesgos financieros y de tesorería.',
                'Apoyar en capacitación de otros auxiliares del área.',
                'Participar en proyectos de mejora del sistema contable.'
            ]
        },
        5: {
            'evaluacion': 'Excelencia operativa en todos los procesos de tesorería. Cero errores en recaudos, pagos y consignaciones. Registros perfectos y oportunos. Gestión proactiva que previene cualquier mora en obligaciones. Conciliaciones bancarias impecables. Liderazgo en custodia y control de recursos. Es modelo y referente del área.',
            'plan_accion': [
                'Liderar rediseño de procesos de tesorería con enfoque de mejora continua.',
                'Mentor formal de nuevos auxiliares de tesorería.',
                'Diseñar e implementar tablero de control e indicadores del área.',
                'Representar al área en comités de gestión financiera.',
                'Desarrollar manuales y procedimientos actualizados para el área.',
                'Liderar proyectos de transformación digital en tesorería.'
            ]
        }
    },

    # =========================================================================
    # CATEGORÍA: COMPETENCIAS INTERPERSONALES (25%)
    # =========================================================================

    'compromiso_responsabilidad': {
        1: {
            'evaluacion': 'Presenta deficiencias significativas en cumplimiento de compromisos. Frecuentemente requiere recordatorios para realizar consignaciones, pagos o cierres de caja. Manejo de recursos económicos requiere supervisión constante por falta de rigurosidad.',
            'plan_accion': [
                'Establecer sistema de recordatorios y alarmas para todas las tareas críticas.',
                'Supervisión diaria durante 60 días de cumplimiento de horarios y procedimientos.',
                'Recibir formación en integridad y ética en manejo de recursos financieros.',
                'Implementar autoevaluación diaria de cumplimiento de tareas asignadas.'
            ]
        },
        2: {
            'evaluacion': 'Cumple con la mayoría de compromisos pero ocasionalmente requiere recordatorios. A veces posterga consignaciones o cierres de caja. Maneja recursos con integridad básica pero podría ser más riguroso.',
            'plan_accion': [
                'Desarrollar disciplina en ejecución de rutinas diarias sin supervisión.',
                'Implementar checklist personal para verificar cumplimiento de tareas críticas.',
                'Fortalecer consciencia sobre impacto de retrasos en obligaciones financieras.',
                'Recibir retroalimentación quincenal sobre puntualidad en entregas.'
            ]
        },
        3: {
            'evaluacion': 'Cumple adecuadamente con compromisos adquiridos. Realiza consignaciones, pagos y cierres de caja en horarios establecidos la mayoría de las veces. Actúa con integridad en el manejo de recursos económicos.',
            'plan_accion': [
                'Alcanzar 100% de cumplimiento en fechas establecidas sin recordatorios.',
                'Desarrollar capacidad de anticipar necesidades y actuar proactivamente.',
                'Fortalecer liderazgo en prácticas de integridad financiera.',
                'Participar en comité de ética y manejo de recursos.'
            ]
        },
        4: {
            'evaluacion': 'Alto nivel de compromiso y responsabilidad. Realiza sistemáticamente consignaciones, pagos y cierres de caja en horarios y fechas establecidas sin necesidad de recordatorios. Maneja recursos con total integridad y transparencia.',
            'plan_accion': [
                'Servir como modelo de responsabilidad para otros miembros del equipo.',
                'Apoyar en supervisión de cumplimiento de otros auxiliares.',
                'Participar en diseño de controles y procedimientos del área.',
                'Desarrollar iniciativas de cultura de responsabilidad financiera.'
            ]
        },
        5: {
            'evaluacion': 'Ejemplo excepcional de compromiso y responsabilidad. Cumplimiento impecable sin necesidad de supervisión. Anticipación proactiva a todas las obligaciones. Integridad ejemplar en manejo de recursos. Es referente de confiabilidad y ética profesional.',
            'plan_accion': [
                'Mentor en valores de integridad y responsabilidad financiera.',
                'Liderar programa de fortalecimiento de cultura ética en el área.',
                'Participar en auditorías internas como evaluador de controles.',
                'Representar al área en comités de ética organizacional.'
            ]
        }
    },

    'atencion_al_detalle': {
        1: {
            'evaluacion': 'Frecuentes errores en procesamiento de información financiera. Regularmente pasa por alto inconsistencias entre comprobantes, soportes y valores autorizados. Sus errores generan reprocesos y afectan la confiabilidad de registros.',
            'plan_accion': [
                'Capacitación en técnicas de verificación y control de calidad.',
                'Implementar protocolo obligatorio de triple verificación para cada transacción.',
                'Reducir velocidad de ejecución priorizando exactitud sobre rapidez.',
                'Recibir supervisión y retroalimentación diaria durante 45 días.'
            ]
        },
        2: {
            'evaluacion': 'Comete errores ocasionales al revisar documentos. A veces no detecta inconsistencias entre comprobantes y soportes hasta que se evidencian problemas. Requiere revisión adicional de supervisor.',
            'plan_accion': [
                'Desarrollar método sistemático de verificación de documentos.',
                'Practicar con casos reales de errores para desarrollar ojo crítico.',
                'Implementar checklist de verificación para cada tipo de transacción.',
                'Recibir retroalimentación semanal sobre calidad de verificaciones.'
            ]
        },
        3: {
            'evaluacion': 'Revisa adecuadamente documentos antes de ejecutar transacciones. Generalmente verifica coincidencia entre comprobantes, soportes y valores autorizados. Detecta la mayoría de inconsistencias aunque ocasionalmente se le escapa algún detalle.',
            'plan_accion': [
                'Alcanzar cero errores en verificación mediante concentración enfocada.',
                'Desarrollar técnicas avanzadas de detección de inconsistencias.',
                'Reducir tiempo de verificación sin sacrificar exactitud.',
                'Documentar errores comunes para crear guías de prevención.'
            ]
        },
        4: {
            'evaluacion': 'Excelente atención al detalle. Verifica sistemáticamente que cada comprobante de pago coincida con soporte, orden y valor autorizado antes de ejecutar transacciones. Detecta proactivamente inconsistencias y las resuelve antes de que generen problemas.',
            'plan_accion': [
                'Servir como verificador secundario en transacciones de alto valor.',
                'Desarrollar guías y listas de chequeo para el equipo.',
                'Participar en auditorías internas de calidad de procesos.',
                'Capacitar a otros en técnicas de verificación efectiva.'
            ]
        },
        5: {
            'evaluacion': 'Nivel excepcional de precisión y atención al detalle. Verifica meticulosamente cada elemento antes de cualquier transacción. Identifica patrones de errores potenciales y propone mejoras en controles. Es referente de exactitud y confiabilidad en el área.',
            'plan_accion': [
                'Diseñar sistema de controles de calidad para el área de tesorería.',
                'Liderar auditorías internas de precisión en procesos financieros.',
                'Mentor en técnicas de verificación y control de calidad.',
                'Participar en diseño de sistemas de prevención de errores.'
            ]
        }
    },

    'orientacion_cliente_interno': {
        1: {
            'evaluacion': 'Actitud reactiva y poco servicial. Frecuentemente genera retrasos en pagos a proveedores. No responde oportunamente a solicitudes de reembolsos o consultas del personal. No anticipa fechas de vencimiento generando moras.',
            'plan_accion': [
                'Capacitación en servicio al cliente interno y gestión de expectativas.',
                'Establecer compromisos de tiempo de respuesta para cada tipo de solicitud.',
                'Implementar sistema de seguimiento de solicitudes pendientes.',
                'Recibir retroalimentación de clientes internos sobre calidad de atención.'
            ]
        },
        2: {
            'evaluacion': 'Atiende solicitudes cuando se le requiere pero no de manera proactiva. Ocasionalmente genera moras en pagos a proveedores por falta de anticipación. Responde consultas pero a veces con demora.',
            'plan_accion': [
                'Desarrollar sistema personal de seguimiento a fechas de vencimiento.',
                'Implementar comunicación proactiva sobre estado de solicitudes de pago.',
                'Reducir tiempo de respuesta a consultas en 50%.',
                'Solicitar retroalimentación periódica sobre oportunidad de respuestas.'
            ]
        },
        3: {
            'evaluacion': 'Atiende adecuadamente solicitudes de pagos, reembolsos y consultas. Generalmente responde oportunamente. Anticipa algunas fechas de vencimiento aunque ocasionalmente requiere recordatorios.',
            'plan_accion': [
                'Lograr cero moras por falta de anticipación a vencimientos.',
                'Implementar comunicación proactiva semanal sobre pagos programados.',
                'Desarrollar reputación de excelencia en servicio al cliente interno.',
                'Crear valor agregado anticipando necesidades antes de que se soliciten.'
            ]
        },
        4: {
            'evaluacion': 'Excelente orientación al cliente interno. Responde oportunamente solicitudes de pagos a proveedores con actitud de servicio. Anticipa proactivamente fechas de vencimiento evitando moras. Comunica estado de solicitudes sin necesidad de que se consulte.',
            'plan_accion': [
                'Diseñar indicadores de satisfacción de cliente interno.',
                'Liderar iniciativas de mejora en tiempos de respuesta del área.',
                'Servir como referente de excelencia en servicio interno.',
                'Capacitar a otros en técnicas de gestión proactiva de obligaciones.'
            ]
        },
        5: {
            'evaluacion': 'Excelencia en servicio al cliente interno. Actitud proactiva excepcional que anticipa necesidades antes de que se expresen. Gestión perfecta de vencimientos sin generar mora alguna. Comunicación proactiva y oportuna que genera confianza. Es modelo de orientación al cliente.',
            'plan_accion': [
                'Diseñar estrategia de servicio al cliente interno para el área financiera.',
                'Mentor en técnicas de anticipación y servicio proactivo.',
                'Liderar proyecto de mejora de experiencia de cliente interno.',
                'Presentar casos de éxito en foros departamentales.'
            ]
        }
    },

    # =========================================================================
    # CATEGORÍA: COMPETENCIAS TÉCNICAS (25%)
    # =========================================================================

    'manejo_plataformas_bancarias': {
        1: {
            'evaluacion': 'Conocimiento muy limitado de plataformas bancarias. Requiere asistencia constante para realizar operaciones básicas. Frecuentes errores al usar portales de ARUS, COMFAMA, PSE o bancos. No logra descargar extractos de manera autónoma.',
            'plan_accion': [
                'Capacitación básica intensiva en uso de portales bancarios.',
                'Recibir entrenamiento uno a uno con auxiliar experimentado.',
                'Practicar operaciones en ambiente de prueba hasta lograr autonomía.',
                'Crear manual personalizado con paso a paso de operaciones frecuentes.'
            ]
        },
        2: {
            'evaluacion': 'Maneja operaciones básicas en plataformas bancarias pero con inseguridad. Requiere apoyo ocasional para funciones más complejas. A veces comete errores que debe corregir. Descarga extractos pero de manera lenta.',
            'plan_accion': [
                'Profundizar en funcionalidades avanzadas de cada plataforma.',
                'Practicar escenarios complejos hasta lograr fluidez.',
                'Reducir tiempo de ejecución de operaciones rutinarias en 40%.',
                'Documentar procedimientos para cada plataforma como referencia rápida.'
            ]
        },
        3: {
            'evaluacion': 'Opera adecuadamente portales bancarios para pagos, transferencias y consultas. Descarga extractos correctamente. Maneja bien ARUS, COMFAMA, PSE y principales bancos. Ocasionalmente consulta dudas sobre funciones poco frecuentes.',
            'plan_accion': [
                'Dominar funcionalidades avanzadas y menos frecuentes de cada plataforma.',
                'Reducir tiempo de operación optimizando uso de atajos y funciones.',
                'Convertirse en usuario experto que pueda capacitar a otros.',
                'Proponer mejoras en uso institucional de plataformas bancarias.'
            ]
        },
        4: {
            'evaluacion': 'Dominio sólido de todas las plataformas bancarias utilizadas. Opera con agilidad y precisión. Resuelve autonomamente problemas o errores que se presentan. Descarga y procesa extractos eficientemente. Apoya a compañeros en operaciones complejas.',
            'plan_accion': [
                'Convertirse en superusuario y referente técnico de plataformas bancarias.',
                'Diseñar y dictar capacitaciones internas sobre uso óptimo.',
                'Investigar nuevas plataformas o servicios bancarios digitales.',
                'Participar en evaluación e implementación de nuevos proveedores bancarios.'
            ]
        },
        5: {
            'evaluacion': 'Experto en operación de todas las plataformas bancarias. Dominio completo de funcionalidades incluyendo las más avanzadas. Opera con máxima eficiencia y precisión. Es referente técnico del área y capacitador interno. Propone optimizaciones en uso institucional.',
            'plan_accion': [
                'Liderar estrategia de digitalización bancaria del área de tesorería.',
                'Evaluar y proponer adopción de nuevas tecnologías bancarias.',
                'Diseñar programa de certificación interna en plataformas bancarias.',
                'Representar a la empresa en mesas de trabajo con entidades bancarias.'
            ]
        }
    },

    'conciliaciones_bancarias': {
        1: {
            'evaluacion': 'Dificultad significativa para realizar conciliaciones bancarias. No logra identificar diferencias entre extracto y registros contables de manera efectiva. Requiere supervisión constante y sus conciliaciones frecuentemente contienen errores.',
            'plan_accion': [
                'Capacitación básica en conceptos de conciliación bancaria.',
                'Entrenamiento práctico con casos reales supervisados.',
                'Estudiar diferencias comunes (partidas en tránsito, errores, notas débito/crédito).',
                'Practicar con conciliaciones de meses anteriores hasta lograr autonomía.'
            ]
        },
        2: {
            'evaluacion': 'Realiza conciliaciones básicas pero con lentitud y errores ocasionales. Identifica diferencias evidentes pero tiene dificultad con inconsistencias complejas. Requiere apoyo para resolver diferencias significativas.',
            'plan_accion': [
                'Fortalecer análisis de causas raíz de diferencias bancarias.',
                'Practicar resolución de casos complejos con retroalimentación.',
                'Desarrollar método sistemático para clasificar y resolver diferencias.',
                'Mejorar velocidad de ejecución sin sacrificar exactitud.'
            ]
        },
        3: {
            'evaluacion': 'Realiza conciliaciones bancarias correctamente. Cruza movimientos de extracto con registros contables adecuadamente. Identifica y resuelve apropiadamente la mayoría de diferencias. Ocasionalmente requiere apoyo en casos muy complejos.',
            'plan_accion': [
                'Desarrollar capacidad de resolver autonomamente casos complejos.',
                'Reducir tiempo de ejecución de conciliaciones en 30%.',
                'Documentar tipología de diferencias y soluciones para crear base de conocimiento.',
                'Proponer mejoras en proceso de conciliación.'
            ]
        },
        4: {
            'evaluacion': 'Alto dominio de conciliaciones bancarias. Identifica rápidamente diferencias entre extracto y contabilidad. Resuelve eficientemente inconsistencias complejas. Propone ajustes contables correctos. Genera conciliaciones precisas y oportunas.',
            'plan_accion': [
                'Automatizar procesos de conciliación usando herramientas avanzadas.',
                'Capacitar a otros auxiliares en técnicas de conciliación.',
                'Diseñar indicadores de calidad de conciliaciones.',
                'Liderar proyecto de mejora del proceso de conciliación bancaria.'
            ]
        },
        5: {
            'evaluacion': 'Experto en conciliaciones bancarias. Ejecuta conciliaciones complejas con precisión y eficiencia excepcional. Identifica patrones de diferencias recurrentes y propone soluciones sistémicas. Es referente técnico y capacitador del área.',
            'plan_accion': [
                'Diseñar metodología avanzada de conciliación para la organización.',
                'Implementar herramientas tecnológicas de conciliación automática.',
                'Liderar auditorías de calidad de conciliaciones.',
                'Mentor en técnicas avanzadas de análisis financiero y conciliación.'
            ]
        }
    },

    'manejo_software_contable': {
        1: {
            'evaluacion': 'Conocimiento muy básico del software contable. Comete frecuentes errores en registro de ingresos, egresos y causaciones. Requiere supervisión constante para operaciones básicas. No comprende la lógica contable del sistema.',
            'plan_accion': [
                'Capacitación básica en uso del software contable de la empresa.',
                'Entrenamiento en lógica de registro de transacciones contables.',
                'Practicar registros en ambiente de prueba hasta lograr confianza.',
                'Recibir supervisión diaria durante 60 días en cada registro.'
            ]
        },
        2: {
            'evaluacion': 'Maneja funciones básicas del software contable. Registra ingresos y egresos simples pero con inseguridad. Comete errores ocasionales en causaciones o recibos de caja. Requiere apoyo para transacciones complejas.',
            'plan_accion': [
                'Profundizar en módulos de tesorería del sistema contable.',
                'Practicar registro de transacciones complejas con retroalimentación.',
                'Estudiar catálogo de cuentas y su correcta aplicación.',
                'Reducir tasa de error en registros en 50%.'
            ]
        },
        3: {
            'evaluacion': 'Usa adecuadamente el software contable para registros de tesorería. Registra correctamente ingresos, egresos, causaciones y recibos de caja. Comprende la lógica contable básica del sistema. Ocasionalmente consulta sobre transacciones poco frecuentes.',
            'plan_accion': [
                'Dominar funcionalidades avanzadas del módulo de tesorería.',
                'Aprender a generar reportes personalizados del sistema.',
                'Desarrollar capacidad de corregir errores contables autonomamente.',
                'Proponer mejoras en parametrización del sistema.'
            ]
        },
        4: {
            'evaluacion': 'Dominio sólido del software contable. Registra eficientemente todo tipo de transacciones de tesorería. Comprende profundamente la lógica contable del sistema. Genera reportes y consultas avanzadas. Apoya a compañeros en resolución de problemas.',
            'plan_accion': [
                'Convertirse en superusuario del módulo de tesorería.',
                'Participar en parametrización y mejoras del sistema.',
                'Capacitar a usuarios en funcionalidades del software.',
                'Colaborar en evaluación de actualizaciones o migración de sistema.'
            ]
        },
        5: {
            'evaluacion': 'Experto en el software contable. Dominio completo de todas las funcionalidades del módulo de tesorería. Parametriza, personaliza reportes y resuelve problemas técnicos. Es referente y capacitador interno. Propone optimizaciones sistémicas.',
            'plan_accion': [
                'Liderar proyecto de optimización del sistema contable.',
                'Diseñar programa de certificación interna en uso del software.',
                'Participar en comité de transformación digital del área financiera.',
                'Evaluar y proponer mejoras o cambios en software contable.'
            ]
        }
    },

    'manejo_office_excel': {
        1: {
            'evaluacion': 'Conocimiento muy básico de Excel. No logra elaborar flujos de caja, controles o reportes funcionales. Usa solo funciones elementales. No comprende fórmulas ni tablas dinámicas. Esto limita significativamente su efectividad.',
            'plan_accion': [
                'Curso básico de Excel enfocado en funciones financieras.',
                'Aprender fórmulas esenciales: SUMA, PROMEDIO, SI, BUSCARV.',
                'Practicar con plantillas existentes de flujo de caja y control de pagos.',
                'Dedicar 2 horas semanales a tutoriales y práctica de Excel.'
            ]
        },
        2: {
            'evaluacion': 'Manejo básico de Excel. Usa fórmulas simples pero con dificultad. Elabora reportes básicos pero sin formato profesional. No domina tablas dinámicas ni funciones avanzadas. Sus controles son funcionales pero poco eficientes.',
            'plan_accion': [
                'Curso intermedio de Excel con énfasis en funciones financieras.',
                'Aprender a crear y usar tablas dinámicas efectivamente.',
                'Mejorar diseño y formato de reportes para presentación profesional.',
                'Desarrollar plantillas estandarizadas para reportes recurrentes.'
            ]
        },
        3: {
            'evaluacion': 'Usa Excel adecuadamente para elaborar flujos de caja, control de pagos y reportes. Maneja fórmulas comunes y formato básico. Crea conciliaciones y reportes funcionales aunque podría optimizar su uso de herramientas avanzadas.',
            'plan_accion': [
                'Dominar funciones avanzadas: SUMAR.SI.CONJUNTO, BUSCARV/X, INDICE+COINCIDIR.',
                'Aprender a automatizar tareas repetitivas con macros básicas.',
                'Mejorar visualización de datos con gráficos y formato condicional.',
                'Crear tableros de control (dashboards) para tesorería.'
            ]
        },
        4: {
            'evaluacion': 'Dominio sólido de Excel. Elabora flujos de caja, controles y reportes profesionales con fórmulas avanzadas. Usa tablas dinámicas, formato condicional y gráficos efectivamente. Sus herramientas son eficientes y de calidad.',
            'plan_accion': [
                'Aprender automatización con macros y VBA básico.',
                'Desarrollar dashboards interactivos para gestión de tesorería.',
                'Crear biblioteca de plantillas avanzadas para el área.',
                'Capacitar a compañeros en uso efectivo de Excel.'
            ]
        },
        5: {
            'evaluacion': 'Experto en Excel aplicado a tesorería. Crea herramientas sofisticadas: flujos de caja dinámicos, controles automatizados, dashboards interactivos. Domina funciones avanzadas, macros y visualización de datos. Es referente técnico del área.',
            'plan_accion': [
                'Desarrollar herramientas de análisis predictivo de flujo de caja.',
                'Liderar automatización de reportes del área de tesorería.',
                'Diseñar programa de capacitación en Excel para área financiera.',
                'Evaluar e implementar complementos avanzados de Excel para finanzas.'
            ]
        }
    },

    'control_custodia_caja_menor': {
        1: {
            'evaluacion': 'Desconoce procedimientos de caja menor. No realiza adecuadamente apertura, manejo, arqueo o legalización. Frecuentes diferencias en arqueos. No cumple políticas internas de caja menor. Requiere supervisión constante.',
            'plan_accion': [
                'Capacitación intensiva en política y procedimientos de caja menor.',
                'Estudiar y aplicar manual de manejo de caja menor.',
                'Supervisión diaria en arqueos y legalizaciones durante 45 días.',
                'Practicar arqueos con verificación hasta lograr cero diferencias.'
            ]
        },
        2: {
            'evaluacion': 'Conocimiento básico de procedimientos de caja menor. Realiza apertura y manejo con supervisión. Ocasionales diferencias en arqueos. Cumple parcialmente con políticas internas. Legalizaciones a veces incompletas o tardías.',
            'plan_accion': [
                'Reforzar conocimiento de política interna de caja menor.',
                'Implementar checklist de verificación para arqueos y legalizaciones.',
                'Mejorar organización de soportes y documentación.',
                'Lograr cero diferencias en arqueos durante 3 meses consecutivos.'
            ]
        },
        3: {
            'evaluacion': 'Maneja adecuadamente procedimientos de caja menor. Realiza correctamente apertura, manejo, arqueo y legalización. Generalmente cumple con política interna. Diferencias ocasionales en arqueos que identifica y resuelve apropiadamente.',
            'plan_accion': [
                'Alcanzar perfección en arqueos: cero diferencias por 6 meses.',
                'Optimizar proceso de legalización reduciendo tiempos.',
                'Proponer mejoras en procedimientos de caja menor.',
                'Convertirse en referente de buenas prácticas en control de caja.'
            ]
        },
        4: {
            'evaluacion': 'Excelente manejo de caja menor. Domina completamente apertura, manejo, arqueo y legalización. Cumple estrictamente con política interna. Arqueos sin diferencias. Legalizaciones oportunas y completas. Mantiene controles sólidos.',
            'plan_accion': [
                'Diseñar mejoras en política y procedimientos de caja menor.',
                'Auditar manejo de caja menor de otras áreas o sedes.',
                'Capacitar a otros responsables de caja menor.',
                'Participar en diseño de controles de efectivo y valores.'
            ]
        },
        5: {
            'evaluacion': 'Experto en control y custodia de caja menor. Procedimientos impecables conforme a normativa y política interna. Arqueos perfectos sin diferencias. Legalizaciones ejemplares. Es modelo de control y transparencia. Propone mejoras sistémicas.',
            'plan_accion': [
                'Liderar rediseño de política de caja menor organizacional.',
                'Diseñar programa de auditoría de caja menor.',
                'Mentor en controles de efectivo y valores.',
                'Participar en comité de control interno y auditoría.'
            ]
        }
    }
}


# =============================================================================
# FUNCIÓN PARA FORMATEAR COMENTARIOS DEL EVALUADOR
# =============================================================================

def formatear_comentarios_evaluador(respuesta):
    """
    Extrae y formatea el comentario del evaluador de una respuesta.

    Args:
        respuesta: objeto RespuestaEvaluacion

    Returns:
        str: Comentario formateado con etiqueta de evaluador
    """
    if respuesta.comentario_evaluador:
        return f"**Comentario del evaluador:** {respuesta.comentario_evaluador}\n"
    return ""


# =============================================================================
# CÁLCULO DE PUNTAJE PONDERADO
# =============================================================================

def calcular_puntaje_ponderado_auxiliar_tesoreria(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado para evaluación de Auxiliar de Tesorería.

    Estructura de ponderación:
    - Competencias Organizacionales (10%): Preguntas 1-3 (3.33% cada una)
    - Objetivos (40%): Pregunta 4 (40%)
    - Competencias Interpersonales (25%): Preguntas 5-7 (8.33% cada una)
    - Competencias Técnicas (25%): Preguntas 8-12 (5% cada una)

    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion

    Returns:
        dict con:
            - puntaje_porcentaje: float (0-100)
            - puntaje_escala: float (0-5)
            - nivel_desempeno: str
            - detalle_categorias: dict con puntajes por categoría
    """

    # Mapeo de preguntas a categorías y pesos
    estructura_ponderacion = {
        1: {'categoria': 'Competencias Organizacionales', 'peso': 10/3},  # 3.33%
        2: {'categoria': 'Competencias Organizacionales', 'peso': 10/3},  # 3.33%
        3: {'categoria': 'Competencias Organizacionales', 'peso': 10/3},  # 3.34%
        4: {'categoria': 'Objetivos', 'peso': 40},                         # 40%
        5: {'categoria': 'Competencias Interpersonales', 'peso': 25/3},   # 8.33%
        6: {'categoria': 'Competencias Interpersonales', 'peso': 25/3},   # 8.33%
        7: {'categoria': 'Competencias Interpersonales', 'peso': 25/3},   # 8.34%
        8: {'categoria': 'Competencias Técnicas', 'peso': 5},             # 5%
        9: {'categoria': 'Competencias Técnicas', 'peso': 5},             # 5%
        10: {'categoria': 'Competencias Técnicas', 'peso': 5},            # 5%
        11: {'categoria': 'Competencias Técnicas', 'peso': 5},            # 5%
        12: {'categoria': 'Competencias Técnicas', 'peso': 5}             # 5%
    }

    # Inicializar contadores por categoría
    categorias = {
        'Competencias Organizacionales': {'puntaje_acumulado': 0, 'peso_total': 10},
        'Objetivos': {'puntaje_acumulado': 0, 'peso_total': 40},
        'Competencias Interpersonales': {'puntaje_acumulado': 0, 'peso_total': 25},
        'Competencias Técnicas': {'puntaje_acumulado': 0, 'peso_total': 25}
    }

    puntaje_total_ponderado = 0
    puntaje_escala_acumulado = 0
    total_preguntas = 0

    # Procesar cada respuesta
    for respuesta in respuestas_evaluacion:
        numero_pregunta = respuesta.pregunta.orden
        valor_respuesta = respuesta.opcion_seleccionada.valor_numerico  # 1-5

        if numero_pregunta in estructura_ponderacion:
            config = estructura_ponderacion[numero_pregunta]
            categoria = config['categoria']
            peso_pregunta = config['peso']

            # Convertir valor 1-5 a porcentaje (1→20%, 2→40%, 3→60%, 4→80%, 5→100%)
            porcentaje_pregunta = (valor_respuesta / 5) * 100

            # Calcular contribución ponderada de esta pregunta
            contribucion = (porcentaje_pregunta * peso_pregunta) / 100

            puntaje_total_ponderado += contribucion
            categorias[categoria]['puntaje_acumulado'] += contribucion

            # Para puntaje en escala 1-5
            puntaje_escala_acumulado += valor_respuesta
            total_preguntas += 1

    # Calcular puntaje en escala 1-5
    puntaje_escala = round(puntaje_escala_acumulado / total_preguntas, 2) if total_preguntas > 0 else 0

    # Determinar nivel de desempeño según porcentaje
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

    # Calcular porcentajes por categoría
    detalle_categorias = {}
    for nombre_cat, datos in categorias.items():
        porcentaje_categoria = round((datos['puntaje_acumulado'] / datos['peso_total']) * 100, 2)
        detalle_categorias[nombre_cat] = {
            'puntaje': round(datos['puntaje_acumulado'], 2),
            'peso_total': datos['peso_total'],
            'porcentaje': porcentaje_categoria
        }

    return {
        'puntaje_porcentaje': round(puntaje_total_ponderado, 2),
        'puntaje_escala': puntaje_escala,
        'nivel_desempeno': nivel_desempeno,
        'detalle_categorias': detalle_categorias
    }


# =============================================================================
# GENERACIÓN DE PLAN DE MEJORA
# =============================================================================

def generar_plan_mejora_auxiliar_tesoreria(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora personalizado para Auxiliar de Tesorería basado en respuestas.

    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion
        resultado_evaluacion: dict con resultados del cálculo de puntaje

    Returns:
        str: Plan de mejora en formato Markdown
    """

    # Mapeo de preguntas a competencias
    mapeo_competencias = {
        1: 'comunicacion',
        2: 'trabajo_en_equipo',
        3: 'mejora_continua',
        4: 'ejecutar_procesos_tesoreria',
        5: 'compromiso_responsabilidad',
        6: 'atencion_al_detalle',
        7: 'orientacion_cliente_interno',
        8: 'manejo_plataformas_bancarias',
        9: 'conciliaciones_bancarias',
        10: 'manejo_software_contable',
        11: 'manejo_office_excel',
        12: 'control_custodia_caja_menor'
    }

    # Encabezado del plan
    plan = f"""# PLAN DE MEJORA - AUXILIAR DE TESORERÍA

## Resultado de la Evaluación

**Puntaje Total:** {resultado_evaluacion['puntaje_porcentaje']}% ({resultado_evaluacion['puntaje_escala']}/5)
**Nivel de Desempeño:** {resultado_evaluacion['nivel_desempeno']}

### Detalle por Categorías

"""

    # Agregar detalle de categorías
    for categoria, datos in resultado_evaluacion['detalle_categorias'].items():
        plan += f"- **{categoria}:** {datos['porcentaje']}% ({datos['puntaje']}/{datos['peso_total']} puntos)\n"

    plan += "\n---\n\n"

    # Agregar evaluación y plan por cada competencia
    for respuesta in respuestas_evaluacion.order_by('pregunta__orden'):
        numero_pregunta = respuesta.pregunta.orden
        nombre_competencia = respuesta.pregunta.pregunta
        valor = respuesta.opcion_seleccionada.valor_numerico
        categoria = respuesta.pregunta.categoria

        # Obtener clave de competencia
        clave_competencia = mapeo_competencias.get(numero_pregunta)

        if not clave_competencia:
            continue

        # Obtener respuestas predefinidas
        competencia_data = RESPUESTAS_AUXILIAR_TESORERIA.get(clave_competencia, {})
        respuesta_predefinida = competencia_data.get(valor, {})

        evaluacion_texto = respuesta_predefinida.get('evaluacion', 'No disponible')
        planes_accion = respuesta_predefinida.get('plan_accion', [])

        # Construir sección
        plan += f"## {numero_pregunta}. {nombre_competencia}\n\n"
        plan += f"**Categoría:** {categoria}\n\n"
        plan += f"**Calificación:** {valor}/5 - {respuesta.opcion_seleccionada.opcion}\n\n"

        # Agregar comentario del evaluador si existe
        plan += formatear_comentarios_evaluador(respuesta)

        plan += f"### Evaluación\n\n{evaluacion_texto}\n\n"

        if planes_accion:
            plan += "### Plan de Acción\n\n"
            for idx, accion in enumerate(planes_accion, 1):
                plan += f"{idx}. {accion}\n"
            plan += "\n"

        plan += "---\n\n"

    # Cierre del plan
    plan += """## Compromisos y Seguimiento

El empleado se compromete a trabajar en las áreas de mejora identificadas siguiendo el plan de acción establecido. Se realizarán seguimientos bimensuales para evaluar el progreso en cada competencia.

**Fecha de elaboración del plan:** Se registrará automáticamente en el sistema.

**Próxima revisión:** Según cronograma de seguimientos bimensuales establecido.

---

*Este plan de mejora ha sido generado automáticamente basándose en los resultados de la evaluación anual de desempeño para el cargo de Auxiliar de Tesorería.*
"""

    return plan
