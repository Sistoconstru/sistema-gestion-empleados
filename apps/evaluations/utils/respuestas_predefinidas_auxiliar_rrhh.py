"""
Respuestas predefinidas para evaluación anual de Auxiliar de RRHH
Sistema de calificación: Escala 1-5 (Muy bajo a Muy alto)
Total de competencias: 11
Ponderación por categorías:
  - Competencias Organizacionales (10%): Preguntas 1-3
  - Objetivos (40%): Pregunta 4
  - Competencias Interpersonales (25%): Preguntas 5-7
  - Competencias Técnicas (25%): Preguntas 8-11
"""


# =============================================================================
# RESPUESTAS PREDEFINIDAS POR COMPETENCIA
# =============================================================================

RESPUESTAS_AUXILIAR_RRHH = {
    # =========================================================================
    # CATEGORÍA: COMPETENCIAS ORGANIZACIONALES (10%)
    # =========================================================================

    'comunicacion': {
        1: {
            'evaluacion': 'Presenta dificultades significativas para comunicarse de manera efectiva. Sus correos y comunicados contienen errores frecuentes o información poco clara. Raramente escucha con atención y suele malinterpretar instrucciones.',
            'plan_accion': [
                'Participar en taller de comunicación escrita enfocado en redacción profesional.',
                'Realizar ejercicios prácticos de escucha activa con retroalimentación del supervisor.',
                'Utilizar plantillas estandarizadas para comunicaciones de RRHH.',
                'Solicitar revisión previa de comunicaciones importantes antes de enviarlas.'
            ]
        },
        2: {
            'evaluacion': 'Su comunicación es básica pero presenta deficiencias. A veces sus mensajes son ambiguos o requieren aclaraciones adicionales. Escucha parcialmente pero no siempre comprende las instrucciones a la primera.',
            'plan_accion': [
                'Desarrollar hábito de confirmar comprensión de instrucciones mediante parafraseo.',
                'Mejorar estructura de comunicaciones utilizando formato claro y profesional.',
                'Practicar comunicación asertiva en situaciones sensibles de RRHH.',
                'Recibir retroalimentación quincenal sobre claridad de sus comunicaciones.'
            ]
        },
        3: {
            'evaluacion': 'Se comunica de manera aceptable. Sus comunicaciones son generalmente claras aunque ocasionalmente requieren ajustes menores. Escucha con atención la mayoría del tiempo y responde adecuadamente a las solicitudes.',
            'plan_accion': [
                'Perfeccionar habilidades de síntesis para comunicaciones ejecutivas.',
                'Desarrollar capacidad de anticipar preguntas frecuentes en sus comunicaciones.',
                'Mantener consistencia en formato y tono profesional.',
                'Fortalecer comunicación proactiva informando novedades antes de que se soliciten.'
            ]
        },
        4: {
            'evaluacion': 'Se comunica efectivamente tanto verbal como por escrito. Sus comunicaciones son claras, precisas y oportunas. Escucha activamente y es receptivo a sugerencias. Mantiene informado al personal sobre novedades de RRHH de manera proactiva.',
            'plan_accion': [
                'Desarrollar habilidades de comunicación en situaciones de conflicto laboral.',
                'Profundizar en técnicas de presentación de información de RRHH a diferentes audiencias.',
                'Servir como referente de buenas prácticas de comunicación para nuevos miembros del equipo.',
                'Participar en comité de mejora de comunicación interna.'
            ]
        },
        5: {
            'evaluacion': 'Sobresale en comunicación efectiva. Sus comunicaciones son ejemplares: claras, precisas, completas y oportunas. Escucha activamente, comprende diferentes perspectivas y adapta su comunicación a diferentes audiencias. Promueve una comunicación abierta y constructiva.',
            'plan_accion': [
                'Mentor en comunicación efectiva para otros auxiliares del área.',
                'Diseñar plantillas y guías de comunicación que puedan ser replicadas por el equipo.',
                'Liderar sesiones de mejora continua en comunicación del área de RRHH.',
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
                'Recibir mentoría sobre importancia de trabajo colaborativo en procesos de RRHH.'
            ]
        },
        2: {
            'evaluacion': 'Colabora ocasionalmente pero tiende a trabajar solo. Comparte información cuando se le solicita pero no de manera proactiva. Su apoyo a compañeros es limitado.',
            'plan_accion': [
                'Desarrollar cultura de compartir información relevante sin necesidad de que se solicite.',
                'Participar en al menos dos proyectos colaborativos trimestrales del área.',
                'Apoyar a compañeros en períodos de alta carga (cierre de nómina, contrataciones masivas).',
                'Asistir a taller de trabajo en equipo y colaboración efectiva.'
            ]
        },
        3: {
            'evaluacion': 'Trabaja adecuadamente en equipo. Comparte información necesaria y colabora cuando se requiere. Contribuye a un ambiente de trabajo positivo aunque podría ser más proactivo en ofrecer apoyo.',
            'plan_accion': [
                'Aumentar iniciativa para apoyar a compañeros sin esperar solicitud explícita.',
                'Compartir conocimientos técnicos (nómina, afiliaciones, legislación) con el equipo.',
                'Participar activamente en mejora de procesos conjuntos del área.',
                'Liderar al menos una iniciativa de mejora en colaboración con otras áreas.'
            ]
        },
        4: {
            'evaluacion': 'Excelente colaborador. Comparte activamente información, recursos y conocimientos con el equipo. Apoya proactivamente a sus compañeros y contribuye significativamente a los objetivos comunes del área de RRHH.',
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
                'Liderar iniciativas de integración entre el área de RRHH y otras áreas.',
                'Mentor formal de nuevos auxiliares de RRHH.',
                'Diseñar y facilitar talleres internos de mejores prácticas.',
                'Participar en diseño de estrategias de fortalecimiento de cultura colaborativa.'
            ]
        }
    },

    'mejora_continua': {
        1: {
            'evaluacion': 'Realiza sus tareas de manera rutinaria sin buscar mejoras. No muestra interés en optimizar procesos. Presenta resistencia al cambio y a nuevas metodologías de trabajo en RRHH.',
            'plan_accion': [
                'Participar en taller de introducción a mejora continua y metodologías ágiles.',
                'Identificar al menos una oportunidad de mejora mensual en sus procesos.',
                'Recibir mentoría sobre importancia de adaptación en gestión humana moderna.',
                'Asistir a sesiones de benchmarking sobre mejores prácticas en RRHH.'
            ]
        },
        2: {
            'evaluacion': 'Cumple con estándares mínimos de calidad. Ocasionalmente sugiere pequeñas mejoras pero no de manera consistente. Acepta cambios cuando se implementan pero no los promueve.',
            'plan_accion': [
                'Desarrollar visión crítica sobre procesos actuales identificando ineficiencias.',
                'Presentar al menos dos propuestas de mejora por trimestre al supervisor.',
                'Participar en proyectos piloto de nuevas herramientas o procesos de RRHH.',
                'Capacitarse en herramientas tecnológicas que optimicen procesos de gestión humana.'
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
            'evaluacion': 'Comprometido activamente con la mejora continua. Identifica oportunidades de optimización y propone soluciones viables. Adopta proactivamente nuevas tecnologías y metodologías que mejoran la eficiencia en RRHH.',
            'plan_accion': [
                'Liderar proyectos de innovación en procesos de RRHH.',
                'Investigar y proponer implementación de nuevas herramientas tecnológicas.',
                'Convertirse en referente de buenas prácticas para el área.',
                'Participar en grupos de trabajo de transformación digital del área de RRHH.'
            ]
        },
        5: {
            'evaluacion': 'Agente de cambio y mejora continua. Constantemente busca y propone optimizaciones significativas. Lidera implementación de mejoras y modernización de procesos. Es modelo de adaptabilidad y excelencia operativa.',
            'plan_accion': [
                'Diseñar estrategia de innovación para el área de RRHH.',
                'Mentor en metodologías de mejora continua para equipo de gestión humana.',
                'Liderar benchmarking con otras organizaciones del sector.',
                'Presentar casos de éxito en foros departamentales o sectoriales.'
            ]
        }
    },

    # =========================================================================
    # CATEGORÍA: OBJETIVOS (40%)
    # =========================================================================

    'apoyar_procesos_rrhh': {
        1: {
            'evaluacion': 'Presenta deficiencias significativas en los procesos de RRHH. Frecuentes errores en novedades de nómina, afiliaciones incompletas, retrasos en archivo de hojas de vida. No cumple con seguimiento a evaluaciones. Incumple normatividad laboral regularmente.',
            'plan_accion': [
                'Capacitación intensiva en procesos básicos de gestión humana.',
                'Supervisión diaria durante 30 días con revisión detallada de cada proceso.',
                'Implementar checklist obligatorio para cada proceso de RRHH.',
                'Estudiar y aplicar normatividad laboral vigente.',
                'Recibir formación en manejo de información confidencial de personal.',
                'Establecer reuniones semanales de seguimiento con supervisor directo.'
            ]
        },
        2: {
            'evaluacion': 'Ejecuta procesos básicos de RRHH con supervisión. Comete errores ocasionales en novedades de nómina o afiliaciones que requieren corrección. A veces se retrasa en control de asistencia o archivo de documentos. Cumplimiento parcial de normatividad laboral.',
            'plan_accion': [
                'Reforzar capacitación en liquidación de nómina y novedades.',
                'Implementar sistema de alertas para fechas de afiliaciones y vencimientos de contratos.',
                'Desarrollar mayor atención al detalle mediante ejercicios prácticos.',
                'Mejorar organización de documentos de personal.',
                'Recibir retroalimentación semanal sobre cumplimiento normativo.',
                'Participar en taller de gestión del tiempo y priorización de tareas de RRHH.'
            ]
        },
        3: {
            'evaluacion': 'Ejecuta adecuadamente los procesos de selección, contratación y administración de personal. Gestiona novedades de nómina y afiliaciones correctamente la mayoría de las veces. Mantiene control de asistencia aceptable. Archivo de hojas de vida organizado. Cumple normatividad laboral básica.',
            'plan_accion': [
                'Reducir a cero los errores en novedades de nómina mediante triple verificación.',
                'Optimizar tiempo de ejecución de afiliaciones y trámites de seguridad social.',
                'Desarrollar capacidad de identificar inconsistencias en documentación.',
                'Fortalecer conocimiento de normativa laboral actualizada.',
                'Documentar procedimientos para estandarizar buenas prácticas.',
                'Ampliar autonomía en resolución de casos complejos de RRHH.'
            ]
        },
        4: {
            'evaluacion': 'Ejecuta con alto nivel de exactitud y oportunidad todos los procesos de RRHH. Novedades de nómina impecables. Afiliaciones completas y oportunas. Control de asistencia riguroso. Archivo de hojas de vida y seguimiento a evaluaciones muy bien gestionados. Excelente cumplimiento de normatividad laboral.',
            'plan_accion': [
                'Optimizar procesos mediante automatización de tareas repetitivas de RRHH.',
                'Desarrollar indicadores de gestión para el área de recursos humanos.',
                'Proponer mejoras en procedimientos de administración de personal.',
                'Capacitarse en gestión del talento humano y desarrollo organizacional.',
                'Apoyar en capacitación de otros auxiliares del área.',
                'Participar en proyectos de mejora del sistema de gestión humana.'
            ]
        },
        5: {
            'evaluacion': 'Excelencia operativa en todos los procesos de RRHH. Cero errores en nómina y afiliaciones. Gestión proactiva de selección y contratación. Control perfecto de asistencia. Archivo impecable. Seguimiento riguroso a evaluaciones. Cumplimiento ejemplar de normatividad laboral. Es modelo y referente del área.',
            'plan_accion': [
                'Liderar rediseño de procesos de RRHH con enfoque de mejora continua.',
                'Mentor formal de nuevos auxiliares de recursos humanos.',
                'Diseñar e implementar tablero de control e indicadores del área.',
                'Representar al área en comités de gestión de talento humano.',
                'Desarrollar manuales y procedimientos actualizados para el área.',
                'Liderar proyectos de transformación digital en RRHH.'
            ]
        }
    },

    # =========================================================================
    # CATEGORÍA: COMPETENCIAS INTERPERSONALES (25%)
    # =========================================================================

    'orientacion_cliente_interno': {
        1: {
            'evaluacion': 'Actitud reactiva y poco servicial. Frecuentemente no responde oportunamente consultas del personal sobre liquidaciones, certificaciones o novedades. Genera malestar por demoras o falta de claridad en sus respuestas.',
            'plan_accion': [
                'Capacitación en servicio al cliente interno y gestión de expectativas.',
                'Establecer compromisos de tiempo de respuesta para cada tipo de consulta.',
                'Implementar sistema de seguimiento de solicitudes pendientes de personal.',
                'Recibir retroalimentación de empleados sobre calidad de atención.'
            ]
        },
        2: {
            'evaluacion': 'Atiende solicitudes cuando se le requiere pero no de manera proactiva. Ocasionalmente demora en responder consultas sobre liquidaciones o certificaciones. Respuestas a veces incompletas o poco claras.',
            'plan_accion': [
                'Desarrollar sistema personal de seguimiento a solicitudes de personal.',
                'Implementar comunicación proactiva sobre estado de trámites.',
                'Reducir tiempo de respuesta a consultas en 50%.',
                'Solicitar retroalimentación periódica sobre oportunidad de respuestas.'
            ]
        },
        3: {
            'evaluacion': 'Atiende adecuadamente solicitudes de personal sobre liquidaciones, certificaciones y novedades. Generalmente responde oportunamente. Anticipa algunas necesidades aunque ocasionalmente requiere recordatorios.',
            'plan_accion': [
                'Lograr respuesta oportuna en 100% de consultas sin recordatorios.',
                'Implementar comunicación proactiva sobre novedades de nómina.',
                'Desarrollar reputación de excelencia en servicio al cliente interno.',
                'Crear valor agregado anticipando necesidades antes de que se soliciten.'
            ]
        },
        4: {
            'evaluacion': 'Excelente orientación al cliente interno. Responde oportunamente consultas del personal con actitud de servicio. Anticipa proactivamente necesidades de certificaciones, liquidaciones o novedades. Comunica estado de solicitudes sin necesidad de que se consulte.',
            'plan_accion': [
                'Diseñar indicadores de satisfacción de cliente interno.',
                'Liderar iniciativas de mejora en tiempos de respuesta del área.',
                'Servir como referente de excelencia en servicio interno.',
                'Capacitar a otros en técnicas de atención proactiva al personal.'
            ]
        },
        5: {
            'evaluacion': 'Excelencia en servicio al cliente interno. Actitud proactiva excepcional que anticipa necesidades antes de que se expresen. Respuestas oportunas, completas y claras. Comunicación proactiva que genera confianza. Es modelo de orientación al personal.',
            'plan_accion': [
                'Diseñar estrategia de servicio al cliente interno para el área de RRHH.',
                'Mentor en técnicas de anticipación y servicio proactivo.',
                'Liderar proyecto de mejora de experiencia del empleado.',
                'Presentar casos de éxito en foros departamentales.'
            ]
        }
    },

    'discrecion_confidencialidad': {
        1: {
            'evaluacion': 'No mantiene adecuada reserva de información sensible. Ha compartido datos personales o laborales fuera de canales autorizados. No comprende la importancia de la confidencialidad en RRHH. Genera riesgos de privacidad.',
            'plan_accion': [
                'Capacitación urgente en manejo de información confidencial y protección de datos.',
                'Estudiar política de privacidad y confidencialidad de la empresa.',
                'Recibir formación en ética profesional y consecuencias legales de filtración de datos.',
                'Supervisión estricta durante 60 días en manejo de información de personal.'
            ]
        },
        2: {
            'evaluacion': 'Manejo básico de confidencialidad. Ocasionalmente comparte información que debería mantener reservada. No siempre identifica qué información es sensible. Necesita refuerzo en protección de datos personales.',
            'plan_accion': [
                'Reforzar conocimiento sobre tipos de información confidencial en RRHH.',
                'Implementar regla de verificación antes de compartir cualquier dato de personal.',
                'Asistir a taller de protección de datos y legislación de privacidad.',
                'Recibir retroalimentación quincenal sobre manejo de información.'
            ]
        },
        3: {
            'evaluacion': 'Maneja adecuadamente información confidencial. Protege datos personales y laborales sin compartirlos fuera de canales autorizados. Comprende la importancia de la discreción en RRHH. Ocasionalmente requiere recordatorios sobre protocolos.',
            'plan_accion': [
                'Alcanzar cero incidentes de manejo inadecuado de información.',
                'Fortalecer conocimiento de normativa de protección de datos personales.',
                'Desarrollar cultura de confidencialidad absoluta.',
                'Servir como referente de buenas prácticas en privacidad.'
            ]
        },
        4: {
            'evaluacion': 'Alto nivel de discreción y confidencialidad. Maneja con absoluta reserva información sensible de personal. Identifica proactivamente qué datos requieren protección especial. Cumple rigurosamente protocolos de privacidad. Genera confianza en el equipo.',
            'plan_accion': [
                'Participar en diseño de políticas de privacidad y confidencialidad.',
                'Apoyar en auditorías de cumplimiento de protección de datos.',
                'Capacitar a otros en manejo de información confidencial.',
                'Servir como custodio de información crítica de RRHH.'
            ]
        },
        5: {
            'evaluacion': 'Ejemplo excepcional de discreción y confidencialidad. Manejo impecable de información sensible con ética profesional ejemplar. Protege datos de manera proactiva. Identifica riesgos de privacidad y actúa preventivamente. Es modelo de confiabilidad absoluta.',
            'plan_accion': [
                'Liderar programa de cultura de confidencialidad en la organización.',
                'Diseñar protocolos de protección de datos para el área de RRHH.',
                'Mentor en ética profesional y manejo de información sensible.',
                'Participar en comités de cumplimiento y protección de datos.'
            ]
        }
    },

    'capacidad_planeacion_organizacion': {
        1: {
            'evaluacion': 'Deficiente organización de tareas. Frecuentemente incumple cronogramas de nómina. Olvida vencimientos de contratos. No realiza seguimiento oportuno a fechas de evaluación. Su desorganización genera retrasos críticos.',
            'plan_accion': [
                'Implementar agenda digital con alarmas para todas las fechas críticas.',
                'Recibir capacitación en gestión del tiempo y priorización de tareas.',
                'Supervisión diaria durante 45 días de cumplimiento de cronogramas.',
                'Utilizar herramientas de gestión de tareas (Trello, Asana, etc.).'
            ]
        },
        2: {
            'evaluacion': 'Organización básica pero con deficiencias. Ocasionalmente se retrasa en cronogramas de nómina. A veces pasa por alto vencimientos de contratos. Requiere recordatorios para fechas de evaluación. Gestión reactiva más que proactiva.',
            'plan_accion': [
                'Desarrollar sistema personal de planificación semanal y mensual.',
                'Implementar checklist de tareas recurrentes (nómina, contratos, evaluaciones).',
                'Mejorar anticipación a fechas críticas con alertas tempranas.',
                'Recibir retroalimentación semanal sobre cumplimiento de plazos.'
            ]
        },
        3: {
            'evaluacion': 'Organiza adecuadamente sus tareas. Cumple cronogramas de nómina la mayoría de las veces. Generalmente anticipa vencimientos de contratos. Realiza seguimiento aceptable a fechas de evaluación. Ocasionales retrasos menores.',
            'plan_accion': [
                'Alcanzar 100% de cumplimiento en cronogramas sin retrasos.',
                'Optimizar gestión de múltiples procesos simultáneos.',
                'Desarrollar capacidad de priorización en situaciones de alta carga.',
                'Documentar sistema de organización para compartir con el equipo.'
            ]
        },
        4: {
            'evaluacion': 'Excelente capacidad de planeación y organización. Cumple sistemáticamente cronogramas de nómina sin retrasos. Anticipa proactivamente vencimientos de contratos. Seguimiento riguroso a fechas de evaluación. Gestiona múltiples tareas simultáneamente con eficiencia.',
            'plan_accion': [
                'Optimizar procesos mediante herramientas avanzadas de planificación.',
                'Diseñar sistema de gestión de tareas para el área de RRHH.',
                'Apoyar a compañeros en organización de su trabajo.',
                'Liderar proyecto de mejora de cronogramas y procesos del área.'
            ]
        },
        5: {
            'evaluacion': 'Nivel excepcional de planeación y organización. Cumplimiento perfecto de todos los cronogramas. Anticipación proactiva a todas las fechas críticas. Gestión impecable de múltiples procesos simultáneos. Es modelo de eficiencia organizacional.',
            'plan_accion': [
                'Diseñar metodología de planificación para el área de RRHH.',
                'Mentor en técnicas de gestión del tiempo y organización.',
                'Liderar implementación de herramientas de productividad.',
                'Presentar mejores prácticas en foros de gestión organizacional.'
            ]
        }
    },

    # =========================================================================
    # CATEGORÍA: COMPETENCIAS TÉCNICAS (25%)
    # =========================================================================

    'gestion_nomina_seguridad_social': {
        1: {
            'evaluacion': 'Conocimiento muy limitado de liquidación de nómina. Comete frecuentes errores en cálculo de horas extras, vacaciones y prestaciones. No comprende afiliaciones a EPS, ARL, AFP y Caja. Requiere asistencia constante.',
            'plan_accion': [
                'Capacitación intensiva en liquidación de nómina y conceptos salariales.',
                'Estudiar legislación sobre prestaciones sociales y seguridad social.',
                'Entrenamiento práctico con casos reales supervisados.',
                'Recibir mentoría de auxiliar experimentado durante 60 días.'
            ]
        },
        2: {
            'evaluacion': 'Conocimiento básico de nómina. Liquida conceptos simples pero con inseguridad. Comete errores ocasionales en horas extras o vacaciones. Comprende afiliaciones básicas pero requiere apoyo en casos complejos.',
            'plan_accion': [
                'Profundizar en liquidación de prestaciones sociales.',
                'Practicar cálculos de nómina con diferentes escenarios.',
                'Estudiar normativa de seguridad social y afiliaciones.',
                'Reducir tasa de error en liquidaciones en 50%.'
            ]
        },
        3: {
            'evaluacion': 'Liquida adecuadamente nómina con conceptos regulares. Calcula correctamente horas extras y vacaciones en casos estándar. Maneja bien afiliaciones a EPS, ARL, AFP y Caja. Ocasionalmente consulta sobre casos especiales.',
            'plan_accion': [
                'Dominar liquidaciones especiales (incapacidades, licencias, terminaciones).',
                'Aprender a resolver inconsistencias en aportes de seguridad social.',
                'Desarrollar autonomía en casos complejos de nómina.',
                'Proponer mejoras en procesos de liquidación.'
            ]
        },
        4: {
            'evaluacion': 'Dominio sólido de liquidación de nómina. Calcula con precisión todo tipo de conceptos: horas extras, recargos, vacaciones, prestaciones. Maneja expertamente afiliaciones y novedades en seguridad social. Resuelve casos complejos autonomamente.',
            'plan_accion': [
                'Convertirse en referente técnico de nómina y seguridad social.',
                'Capacitar a otros auxiliares en liquidación de nómina.',
                'Investigar actualizaciones en normativa de seguridad social.',
                'Participar en optimización del sistema de nómina.'
            ]
        },
        5: {
            'evaluacion': 'Experto en gestión de nómina y seguridad social. Dominio completo de liquidación de todo tipo de conceptos incluyendo casos especiales. Manejo impecable de afiliaciones y novedades. Es referente técnico y capacitador interno.',
            'plan_accion': [
                'Liderar actualización de procedimientos de nómina.',
                'Diseñar programa de certificación interna en liquidación de nómina.',
                'Representar a la empresa ante entidades de seguridad social.',
                'Evaluar e implementar mejoras en sistema de nómina.'
            ]
        }
    },

    'legislacion_laboral': {
        1: {
            'evaluacion': 'Conocimiento muy limitado del Código Sustantivo del Trabajo. Desconoce tipos de contrato, cesantías y liquidaciones. No identifica situaciones que requieren aplicación de normativa laboral. Genera riesgos legales.',
            'plan_accion': [
                'Capacitación urgente en legislación laboral básica.',
                'Estudiar Código Sustantivo del Trabajo: contratos, jornada, salarios.',
                'Recibir formación en prestaciones sociales y liquidaciones.',
                'Supervisión estricta en aplicación de normativa laboral.'
            ]
        },
        2: {
            'evaluacion': 'Conocimiento básico de legislación laboral. Comprende tipos de contrato pero con limitaciones. Conoce cesantías y primas de manera superficial. Requiere apoyo frecuente para aplicar normativa correctamente.',
            'plan_accion': [
                'Profundizar en Código Sustantivo del Trabajo.',
                'Estudiar casos prácticos de aplicación de normativa laboral.',
                'Asistir a seminarios de actualización en legislación laboral.',
                'Desarrollar capacidad de interpretar normas laborales.'
            ]
        },
        3: {
            'evaluacion': 'Dominio básico del Código Sustantivo del Trabajo. Conoce tipos de contrato, cesantías, primas y liquidaciones estándar. Aplica normativa laboral correctamente en casos comunes. Ocasionalmente consulta sobre situaciones especiales.',
            'plan_accion': [
                'Estudiar normativa laboral especial (maternidad, incapacidades, terminaciones).',
                'Desarrollar capacidad de análisis de casos complejos.',
                'Mantenerse actualizado en reformas laborales.',
                'Proponer mejoras en aplicación de normativa en la empresa.'
            ]
        },
        4: {
            'evaluacion': 'Buen dominio de legislación laboral. Conoce profundamente tipos de contrato, prestaciones sociales y liquidaciones. Aplica correctamente normativa en casos complejos. Identifica riesgos legales y propone soluciones.',
            'plan_accion': [
                'Convertirse en referente técnico de legislación laboral.',
                'Capacitar a otros en aplicación de normativa laboral.',
                'Participar en auditorías de cumplimiento legal.',
                'Investigar jurisprudencia laboral relevante para la empresa.'
            ]
        },
        5: {
            'evaluacion': 'Experto en legislación laboral. Dominio completo del Código Sustantivo del Trabajo y normativa complementaria. Aplica expertamente la ley en todo tipo de situaciones. Previene riesgos legales. Es referente y consultor interno.',
            'plan_accion': [
                'Liderar programa de cumplimiento normativo laboral.',
                'Diseñar capacitaciones en legislación laboral para la organización.',
                'Representar a la empresa en mesas de trabajo legal.',
                'Participar en diseño de políticas laborales de la empresa.'
            ]
        }
    },

    'manejo_software_rrhh_office': {
        1: {
            'evaluacion': 'Conocimiento muy limitado de herramientas ofimáticas y software de RRHH. No logra generar reportes básicos. Manejo deficiente de Excel para control de personal. Requiere asistencia constante.',
            'plan_accion': [
                'Curso básico de Excel enfocado en gestión de personal.',
                'Capacitación en uso del software de RRHH de la empresa.',
                'Aprender funciones básicas para reportes de nómina y personal.',
                'Practicar con plantillas existentes hasta lograr autonomía.'
            ]
        },
        2: {
            'evaluacion': 'Manejo básico de Office y software de RRHH. Genera reportes simples pero con dificultad. Usa funciones elementales de Excel. No domina módulos avanzados del sistema de gestión humana.',
            'plan_accion': [
                'Curso intermedio de Excel con énfasis en análisis de datos de personal.',
                'Profundizar en módulos del software de RRHH (nómina, selección, evaluaciones).',
                'Aprender a crear reportes profesionales.',
                'Desarrollar habilidades en manejo de bases de datos de personal.'
            ]
        },
        3: {
            'evaluacion': 'Usa adecuadamente herramientas ofimáticas y software de RRHH. Genera reportes de nómina y control de personal correctamente. Maneja Excel con funciones intermedias. Opera bien el sistema de gestión humana.',
            'plan_accion': [
                'Dominar funciones avanzadas de Excel (tablas dinámicas, BUSCARV, fórmulas complejas).',
                'Aprender funcionalidades avanzadas del software de RRHH.',
                'Mejorar diseño de reportes con visualización de datos.',
                'Desarrollar dashboards para indicadores de gestión humana.'
            ]
        },
        4: {
            'evaluacion': 'Dominio sólido de herramientas ofimáticas y software de RRHH. Genera reportes profesionales con análisis de datos. Usa Excel avanzado para gestión de personal. Opera expertamente el sistema de gestión humana.',
            'plan_accion': [
                'Aprender automatización con macros y VBA.',
                'Desarrollar reportes automáticos y dashboards interactivos.',
                'Convertirse en superusuario del software de RRHH.',
                'Capacitar a compañeros en uso de herramientas.'
            ]
        },
        5: {
            'evaluacion': 'Experto en herramientas ofimáticas y software de RRHH. Crea reportes sofisticados y análisis avanzados. Domina Excel a nivel experto. Opera y personaliza el sistema de gestión humana. Es referente técnico.',
            'plan_accion': [
                'Liderar optimización del software de RRHH.',
                'Desarrollar herramientas de analytics de gestión humana.',
                'Diseñar programa de capacitación en herramientas para el área.',
                'Evaluar e implementar nuevas tecnologías de RRHH.'
            ]
        }
    },

    'gestion_documental_personal': {
        1: {
            'evaluacion': 'Organización deficiente de expedientes de personal. Hojas de vida incompletas o desactualizadas. Contratos sin archivar correctamente. Evaluaciones y afiliaciones sin custodia adecuada. Genera riesgos de pérdida de información.',
            'plan_accion': [
                'Capacitación en gestión documental y archivo de personal.',
                'Estudiar política de custodia de documentos de la empresa.',
                'Reorganizar expedientes existentes bajo supervisión.',
                'Implementar sistema de verificación de completitud de documentos.'
            ]
        },
        2: {
            'evaluacion': 'Organización básica de documentos de personal. Mantiene hojas de vida y contratos pero con inconsistencias. A veces falta documentación en expedientes. Custodia aceptable pero mejorable.',
            'plan_accion': [
                'Mejorar sistema de archivo y clasificación de documentos.',
                'Implementar checklist de documentos obligatorios por expediente.',
                'Desarrollar hábito de verificación de completitud.',
                'Digitalizar documentos para respaldo y consulta rápida.'
            ]
        },
        3: {
            'evaluacion': 'Organiza adecuadamente expedientes de personal. Mantiene hojas de vida, contratos, evaluaciones y afiliaciones correctamente archivados. Custodia apropiada de documentos. Ocasionalmente falta algún documento menor.',
            'plan_accion': [
                'Alcanzar 100% de completitud en todos los expedientes.',
                'Optimizar sistema de archivo para consulta rápida.',
                'Implementar digitalización sistemática de documentos.',
                'Proponer mejoras en gestión documental del área.'
            ]
        },
        4: {
            'evaluacion': 'Excelente gestión documental de personal. Expedientes completos y perfectamente organizados. Hojas de vida actualizadas. Contratos, evaluaciones y afiliaciones impecablemente archivados. Custodia segura. Fácil consulta y trazabilidad.',
            'plan_accion': [
                'Liderar proyecto de digitalización de expedientes de personal.',
                'Diseñar sistema de gestión documental electrónica.',
                'Capacitar a otros en buenas prácticas de archivo.',
                'Implementar mejoras en seguridad y custodia de documentos.'
            ]
        },
        5: {
            'evaluacion': 'Experto en gestión documental de personal. Sistema de archivo ejemplar. Expedientes completos, organizados y digitalizados. Trazabilidad perfecta. Custodia segura con controles sólidos. Es modelo y referente del área.',
            'plan_accion': [
                'Diseñar estrategia de gestión documental para RRHH.',
                'Liderar implementación de sistema de archivo electrónico.',
                'Mentor en organización y custodia de documentos.',
                'Participar en auditorías de gestión documental.'
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
    if respuesta.comentarios_evaluador:
        return f"**Comentario del evaluador:** {respuesta.comentarios_evaluador}\n"
    return ""


# =============================================================================
# CÁLCULO DE PUNTAJE PONDERADO
# =============================================================================

def calcular_puntaje_ponderado_auxiliar_rrhh(respuestas_evaluacion):
    """
    Calcula el puntaje ponderado para evaluación de Auxiliar de RRHH.

    Estructura de ponderación:
    - Competencias Organizacionales (10%): Preguntas 1-3 (3.33% cada una)
    - Objetivos (40%): Pregunta 4 (40%)
    - Competencias Interpersonales (25%): Preguntas 5-7 (8.33% cada una)
    - Competencias Técnicas (25%): Preguntas 8-11 (6.25% cada una)

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
        8: {'categoria': 'Competencias Técnicas', 'peso': 25/4},          # 6.25%
        9: {'categoria': 'Competencias Técnicas', 'peso': 25/4},          # 6.25%
        10: {'categoria': 'Competencias Técnicas', 'peso': 25/4},         # 6.25%
        11: {'categoria': 'Competencias Técnicas', 'peso': 25/4}          # 6.25%
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
        valor_respuesta = float(respuesta.opcion_seleccionada.valor_numerico)  # Convertir a float para cálculos

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

    # Calcular porcentajes por categoría y promedios
    detalle_categorias = {}

    # Contar preguntas por categoría
    preguntas_por_categoria = {
        'Competencias Organizacionales': 3,  # preguntas 1-3
        'Objetivos': 1,  # pregunta 4
        'Competencias Interpersonales': 3,  # preguntas 5-7
        'Competencias Técnicas': 4  # preguntas 8-11
    }

    for nombre_cat, datos in categorias.items():
        num_preguntas = preguntas_por_categoria.get(nombre_cat, 1)
        porcentaje_categoria = round((datos['puntaje_acumulado'] / datos['peso_total']) * 100, 2)
        promedio_categoria = puntaje_escala_acumulado / total_preguntas if total_preguntas > 0 else 0

        detalle_categorias[nombre_cat] = {
            'ponderacion': datos['peso_total'],
            'promedio': round(promedio_categoria, 2),
            'porcentaje': porcentaje_categoria,
            'contribucion': round(datos['puntaje_acumulado'], 2)
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

def generar_plan_mejora_auxiliar_rrhh(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Auxiliar de RRHH
    basado en respuestas y resultado ponderado.

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
║                           AUXILIAR DE RRHH                                   ║
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
        4: 'apoyar_procesos_rrhh',
        5: 'orientacion_cliente_interno',
        6: 'discrecion_confidencialidad',
        7: 'capacidad_planeacion_organizacion',
        8: 'gestion_nomina_seguridad_social',
        9: 'legislacion_laboral',
        10: 'manejo_software_rrhh_office',
        11: 'gestion_documental_personal'
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
            if clave_competencia and clave_competencia in RESPUESTAS_AUXILIAR_RRHH:
                competencia_data = RESPUESTAS_AUXILIAR_RRHH[clave_competencia]
                if puntuacion in competencia_data:
                    datos_plan = competencia_data[puntuacion]
                    planes_accion = datos_plan.get('plan_accion', [])

                    plan_texto += f"   📋 PLAN DE ACCIÓN:\n"

                    # Tomar solo los primeros 3 items del plan
                    items_plan = planes_accion[:3]

                    for idx, item in enumerate(items_plan, 1):
                        plan_texto += f"   {idx}. {item}\n"

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
    planes.append("2. Se realizarán 3 seguimientos bimensuales (cada 2 meses) durante 6 meses.\n")
    planes.append("3. Al finalizar el período se realizará una evaluación final del plan.\n")
    planes.append("4. Las competencias con seguimiento bimensual deben mostrar avance progresivo.\n")
    planes.append("="*80 + "\n")

    return "".join(planes)
