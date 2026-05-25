"""
Respuestas predefinidas y lógica de evaluación para Mensajero
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

COMUNICACION_MENSAJERO = {
    'pregunta': 'COMUNICACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** La comunicación presenta deficiencias graves. No informa novedades de entregas. Los reportes son confusos. No escucha instrucciones adecuadamente.',
            'plan_mejora': 'Capacitación en comunicación efectiva. Implementar protocolo de reportes de entrega. Confirmar comprensión de instrucciones diarias.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Comunicación básica pero insuficiente. Informa solo cuando se solicita. Los reportes requieren aclaraciones. Debe mejorar escucha activa.',
            'plan_mejora': 'Desarrollar hábito de reportar novedades proactivamente. Mejorar claridad en comunicación de retrasos. Practicar escucha activa de instrucciones.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Se comunica adecuadamente. Reporta novedades generalmente a tiempo. Escucha instrucciones. **Oportunidad:** Mayor proactividad en informar situaciones.',
            'plan_mejora': 'Perfeccionar comunicación de emergencias. Anticipar necesidades de información. Mejorar reporte de evidencias de entrega.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Comunica efectivamente. Reporta oportunamente novedades, retrasos y dificultades. Facilita coordinación de actividades. Escucha activamente.',
            'plan_mejora': 'Mantener excelencia comunicativa. Servir como referente en comunicación efectiva. Capacitar a otros en protocolos de reporte.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente comunicador. Sus reportes son claros, oportunos y completos. Anticipa necesidades de información. Facilita continuidad de actividades.',
            'plan_mejora': 'Mantener excelencia. Diseñar guías de comunicación efectiva para mensajería. Ser mentor en comunicación operativa.'
        }
    }
}

TRABAJO_EQUIPO_MENSAJERO = {
    'pregunta': 'TRABAJO EN EQUIPO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No colabora con el equipo. Se aísla. No comparte información de entregas. No apoya a compañeros.',
            'plan_mejora': 'Participar en actividades de integración. Compartir información de rutas y entregas. Apoyar en períodos de alta demanda.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Colaboración limitada. Comparte información solo cuando se solicita. Apoyo a compañeros es básico.',
            'plan_mejora': 'Desarrollar cultura colaborativa. Compartir mejores prácticas de rutas. Apoyar proactivamente al equipo.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Trabaja adecuadamente en equipo. Comparte información cuando es necesario. Colabora satisfactoriamente. **Oportunidad:** Mayor proactividad.',
            'plan_mejora': 'Aumentar iniciativa de apoyo sin esperar solicitud. Compartir conocimientos de rutas eficientes. Liderar mejoras en procesos de mensajería.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente colaborador. Comparte activamente información de entregas. Apoya proactivamente a compañeros. Contribuye a objetivos del área.',
            'plan_mejora': 'Mantener colaboración. Documentar mejores prácticas. Facilitar integración de nuevos mensajeros.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Modelo de trabajo en equipo. Comparte generosamente conocimientos. Apoya constantemente. Eleva el desempeño del equipo.',
            'plan_mejora': 'Mantener excelencia. Liderar capacitación de equipo. Diseñar programa de mejora colaborativa.'
        }
    }
}

MEJORA_CONTINUA_MENSAJERO = {
    'pregunta': 'MEJORA CONTINUA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No demuestra compromiso con mejora. Realiza entregas sin buscar optimización. No propone mejoras en rutas.',
            'plan_mejora': 'Capacitación en optimización de rutas. Establecer métricas de eficiencia. Proponer al menos una mejora trimestral.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Enfoque de mejora limitado. Cumple procedimientos sin cuestionarlos. Propone pocas mejoras.',
            'plan_mejora': 'Implementar revisión de rutas periódicamente. Proponer optimizaciones en tiempos de entrega. Benchmarking con mejores prácticas.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Realiza entregas bajo estándares aceptables. Ocasionalmente propone mejoras. **Oportunidad:** Mayor proactividad en optimización.',
            'plan_mejora': 'Liderar proyecto de optimización de rutas. Proponer automatizaciones en reportes. Investigar mejores prácticas de mensajería.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Compromiso activo con mejora continua. Propone regularmente optimizaciones de rutas. Implementa estándares de calidad altos.',
            'plan_mejora': 'Mantener proactividad. Liderar mejoras en procesos de entrega. Formar parte de comité de mejora continua.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente en mejora continua. Propone e implementa optimizaciones significativas. Ha mejorado procesos clave de mensajería.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación de procesos de mensajería. Diseñar programa de optimización de rutas.'
        }
    }
}

# =====================================================================
# OBJETIVOS - EL HACER (40%)
# =====================================================================

OBJETIVOS_MENSAJERO = {
    'pregunta': 'OBJETIVOS - DILIGENCIAS EXTERNAS',
    'respuestas': {
        1: {
            'retroalimentacion': '**Desempeño insatisfactorio:** No cumple objetivos de diligencias. Entregas con retrasos frecuentes. Errores en documentos. No maneja adecuadamente recursos. **Requiere plan inmediato.**',
            'plan_mejora': 'Capacitación urgente en gestión de diligencias. Supervisión directa diaria. Revisión de protocolos de entrega. Capacitación en manejo de recursos.'
        },
        2: {
            'retroalimentacion': '**Desempeño por debajo de expectativas:** Cumple parcialmente objetivos. Entregas con retrasos ocasionales. Errores que requieren corrección. **Necesita mejora significativa.**',
            'plan_mejora': 'Entrenamiento en planificación de rutas. Implementar checklist de verificación. Capacitación en manejo de documentos. Seguimiento semanal.'
        },
        3: {
            'retroalimentacion': '**Desempeño satisfactorio:** Cumple objetivos básicos. Realiza diligencias a tiempo generalmente. Maneja documentos adecuadamente. **Oportunidad:** Mayor eficiencia y proactividad.',
            'plan_mejora': 'Desarrollar optimización de rutas. Mejorar puntualidad en todas las entregas. Dominar manejo de situaciones especiales. Proponer mejoras en procesos.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Cumple muy bien objetivos. Ejecuta diligencias eficientemente. Entregas puntuales. Maneja responsablemente recursos. Garantiza resolución oportuna de trámites.',
            'plan_mejora': 'Mantener excelencia. Asumir diligencias más complejas. Optimizar tiempos de entrega. Participar en proyectos de mejora.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente cumplimiento de objetivos. Ejecuta diligencias de manera impecable. Siempre puntual. Maneja recursos óptimamente. Es referente en gestión de diligencias.',
            'plan_mejora': 'Mantener excelencia. Liderar optimización de procesos de mensajería. Diseñar rutas modelo. Capacitar a equipo de mensajeros.'
        }
    }
}

# =====================================================================
# COMPETENCIAS INTERPERSONALES - EL SER (25%)
# =====================================================================

ATENCION_DETALLE_MENSAJERO = {
    'pregunta': 'ATENCIÓN AL DETALLE',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Poca atención al detalle. No verifica documentos ni direcciones. Genera errores en entregas. Pérdidas de documentos.',
            'plan_mejora': 'Implementar checklist de verificación obligatorio. Practicar revisión sistemática de documentos. Doble verificación antes de cada entrega.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Atención básica pero insuficiente. Detecta solo errores evidentes. Ocasionalmente omite verificaciones. Requiere reprocesos.',
            'plan_mejora': 'Desarrollar técnicas de verificación detallada. Implementar revisión sistemática de entregas. Reducir errores en documentación.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Verifica documentos adecuadamente. Detecta inconsistencias principales. **Oportunidad:** Mayor precisión en detección de errores menores.',
            'plan_mejora': 'Perfeccionar verificación de entregas. Implementar controles adicionales. Desarrollar alertas tempranas de inconsistencias.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente atención al detalle. Verifica cuidadosamente documentos, direcciones y paquetes. Detecta y reporta oportunamente inconsistencias. Evita errores.',
            'plan_mejora': 'Mantener precisión. Capacitar al equipo en técnicas de verificación. Diseñar controles de calidad para mensajería.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Atención excepcional al detalle. Identifica inconsistencias mínimas. Previene errores antes de que ocurran. Sus entregas son impecables.',
            'plan_mejora': 'Mantener excelencia. Liderar implementación de controles de calidad. Diseñar programa de certificación en precisión de entregas.'
        }
    }
}

PLANEACION_PROGRAMACION_MENSAJERO = {
    'pregunta': 'PLANEACIÓN Y PROGRAMACIÓN',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No planea rutas ni diligencias. Trabaja reactivamente. No organiza entregas. Incumple horarios frecuentemente.',
            'plan_mejora': 'Capacitación en gestión del tiempo. Elaborar cronograma diario de entregas. Planificar rutas eficientes. Coordinar diariamente con supervisor.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Planeación básica insuficiente. Organiza rutas pero no las sigue consistentemente. Ocasionalmente incumple horarios.',
            'plan_mejora': 'Implementar sistema de gestión de entregas. Seguimiento de cumplimiento de rutas. Mejorar organización de prioridades.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Planea adecuadamente rutas y entregas. Organiza secuencia de diligencias. Cumple generalmente horarios. **Oportunidad:** Mayor eficiencia.',
            'plan_mejora': 'Perfeccionar planificación de rutas complejas. Implementar seguimiento de tiempos. Desarrollar planes de contingencia para retrasos.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Planea efectivamente rutas y entregas. Organiza secuencia eficiente. Cumple oportunamente con horarios. Entregas ordenadas sin contratiempos.',
            'plan_mejora': 'Mantener excelencia. Liderar mejoras en planificación de rutas. Capacitar en gestión del tiempo. Optimizar procesos de entrega.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente planificación. Organiza rutas óptimas con anticipación. Siempre cumple horarios. Anticipa contingencias. Modelo de organización.',
            'plan_mejora': 'Mantener excelencia. Liderar planificación estratégica de mensajería. Diseñar sistema de gestión de rutas. Optimizar entregas a nivel organizacional.'
        }
    }
}

COMUNICACION_EFECTIVA_MENSAJERO = {
    'pregunta': 'COMUNICACIÓN EFECTIVA',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No informa novedades. No coordina con áreas. Genera problemas por falta de comunicación de retrasos.',
            'plan_mejora': 'Capacitación en comunicación operativa. Implementar protocolo de alertas de retrasos. Establecer canales efectivos de comunicación.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Comunicación limitada. Informa solo cuando se solicita. No es proactivo en alertas de dificultades.',
            'plan_mejora': 'Desarrollar comunicación proactiva. Implementar reportes automáticos de estado. Mejorar coordinación con áreas.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Informa adecuadamente novedades. Mantiene comunicación cuando es necesario. **Oportunidad:** Mayor inmediatez en reportes críticos.',
            'plan_mejora': 'Perfeccionar comunicación inmediata de emergencias. Desarrollar alertas tempranas de retrasos. Mejorar coordinación interdepartamental.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Mantiene comunicación clara y oportuna. Informa inmediatamente novedades, retrasos y dificultades. Facilita coordinación de actividades.',
            'plan_mejora': 'Mantener comunicación efectiva. Diseñar sistema de alertas optimizado. Implementar mejores prácticas de reporte.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Excelente comunicación. Informa proactivamente todas las novedades. Facilita continuidad. Anticipa necesidades de información.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de comunicación operativa. Diseñar sistema integrado de información. Ser mentor en comunicación efectiva.'
        }
    }
}

# =====================================================================
# COMPETENCIAS TÉCNICAS - EL SABER (25%)
# =====================================================================

PRESENTACION_PERSONAL_MENSAJERO = {
    'pregunta': 'PRESENTACIÓN PERSONAL Y REPRESENTACIÓN INSTITUCIONAL',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** Presentación personal inadecuada. No representa apropiadamente a la empresa. Recibe observaciones de entidades externas.',
            'plan_mejora': 'Capacitación en protocolo de presentación personal. Revisar estándares de imagen corporativa. Supervisión de cumplimiento de normas de presentación.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Presentación básica pero mejorable. Ocasionalmente no cumple estándares de imagen corporativa. Requiere recordatorios.',
            'plan_mejora': 'Reforzar importancia de imagen corporativa. Implementar checklist de presentación diaria. Mejorar uniformidad y pulcritud.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Mantiene presentación adecuada generalmente. Representa apropiadamente a la empresa. **Oportunidad:** Consistencia total en estándares.',
            'plan_mejora': 'Perfeccionar presentación personal constantemente. Mantener estándares altos de imagen. Ser modelo de representación institucional.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Mantiene excelente presentación personal. Representa apropiadamente a la empresa ante entidades. Sin observaciones externas. Imagen corporativa impecable.',
            'plan_mejora': 'Mantener excelencia. Servir como referente de imagen corporativa. Apoyar en orientación de nuevos mensajeros sobre presentación.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Presentación personal excepcional. Modelo de representación institucional. Genera imagen positiva de la empresa constantemente.',
            'plan_mejora': 'Mantener excelencia. Liderar estándares de imagen corporativa. Capacitar a equipo en protocolo de presentación. Ser embajador de marca.'
        }
    }
}

CONOCIMIENTO_RUTAS_MENSAJERO = {
    'pregunta': 'CONOCIMIENTO DE RUTAS Y DIRECCIONAMIENTO',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No conoce ubicaciones. Se pierde frecuentemente. Genera retrasos constantes por desconocimiento de rutas.',
            'plan_mejora': 'Capacitación intensiva en geografía de la ciudad. Estudiar ubicación de entidades principales. Usar GPS obligatoriamente. Acompañamiento en rutas.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico de rutas. Encuentra ubicaciones con dificultad. Requiere GPS constantemente. Optimización de rutas limitada.',
            'plan_mejora': 'Estudiar rutas frecuentes. Memorizar ubicaciones principales. Practicar desplazamientos eficientes. Reducir dependencia de GPS.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Conoce rutas principales. Encuentra ubicaciones adecuadamente. Realiza recorridos satisfactorios. **Oportunidad:** Optimizar tiempos de desplazamiento.',
            'plan_mejora': 'Dominar rutas alternas para contingencias. Optimizar tiempos de recorrido. Desarrollar conocimiento de zonas menos frecuentes.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Excelente conocimiento de rutas. Conoce ubicaciones de entidades, clientes y proveedores. Realiza recorridos eficientes minimizando retrasos.',
            'plan_mejora': 'Mantener dominio de rutas. Compartir mejores rutas con equipo. Actualizar conocimientos de nuevas ubicaciones. Optimizar continuamente.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Dominio excepcional de rutas. Conoce la ciudad perfectamente. Optimiza desplazamientos constantemente. Es referente en conocimiento de ubicaciones.',
            'plan_mejora': 'Mantener excelencia. Diseñar mapas de rutas óptimas. Capacitar a equipo en conocimiento de ubicaciones. Liderar optimización de desplazamientos.'
        }
    }
}

HERRAMIENTAS_TECNOLOGICAS_MENSAJERO = {
    'pregunta': 'MANEJO BÁSICO DE HERRAMIENTAS TECNOLÓGICAS',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No maneja celular ni aplicaciones adecuadamente. No usa GPS. No reporta evidencias. Genera problemas de comunicación.',
            'plan_mejora': 'Capacitación básica en uso de celular y aplicaciones. Entrenar en uso de GPS. Practicar envío de evidencias fotográficas. Tutorías diarias.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Manejo básico de herramientas. Usa GPS con dificultad. Reporta evidencias de manera desorganizada. Requiere apoyo frecuente.',
            'plan_mejora': 'Curso de aplicaciones de mensajería. Practicar uso de GPS eficientemente. Mejorar organización de reportes. Desarrollar autonomía tecnológica.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Utiliza adecuadamente herramientas básicas. Maneja GPS y aplicaciones satisfactoriamente. **Oportunidad:** Mayor eficiencia en uso de tecnología.',
            'plan_mejora': 'Especializarse en funciones avanzadas de aplicaciones. Optimizar uso de GPS. Mejorar calidad de evidencias digitales. Explorar nuevas herramientas.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Utiliza efectivamente celular, aplicaciones, GPS. Reporta oportunamente novedades y evidencias de manera organizada. Buen manejo tecnológico.',
            'plan_mejora': 'Mantener dominio tecnológico. Capacitar a equipo en uso de herramientas. Optimizar procesos mediante tecnología. Evaluar nuevas aplicaciones.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Experto en herramientas tecnológicas. Optimiza todos los procesos mediante tecnología. Sus reportes son modelo de organización digital.',
            'plan_mejora': 'Mantener excelencia. Liderar transformación digital de mensajería. Diseñar protocolos de reporte digital. Evaluar e implementar nuevas tecnologías.'
        }
    }
}

NORMAS_TRANSITO_MENSAJERO = {
    'pregunta': 'NORMAS DE TRÁNSITO Y SEGURIDAD VIAL',
    'respuestas': {
        1: {
            'retroalimentacion': '**Área de mejora crítica:** No cumple normas de tránsito. Conduce de forma insegura. Ha tenido accidentes. No cuida el vehículo. **Riesgo alto.**',
            'plan_mejora': 'Capacitación urgente en seguridad vial. Curso de conducción defensiva. Supervisión de cumplimiento de normas. Implementar protocolo de seguridad obligatorio.'
        },
        2: {
            'retroalimentacion': '**Necesita mejorar:** Conocimiento básico de normas. Ocasionalmente no cumple normas de tránsito. Conducción mejorable. Cuidado del vehículo limitado.',
            'plan_mejora': 'Curso de actualización en normas de tránsito. Entrenamiento en conducción segura. Implementar checklist de revisión de vehículo. Seguimiento de cumplimiento.'
        },
        3: {
            'retroalimentacion': '**Desempeño aceptable:** Conoce y aplica normas de tránsito generalmente. Conduce de forma responsable. Cuida el vehículo. **Oportunidad:** Perfeccionar seguridad vial.',
            'plan_mejora': 'Especializarse en conducción defensiva avanzada. Perfeccionar mantenimiento preventivo de vehículo. Desarrollar cultura de cero accidentes.'
        },
        4: {
            'retroalimentacion': '**Buen desempeño:** Conoce y aplica normas de tránsito. Se moviliza responsablemente. Previene accidentes. Cumple normas de seguridad. Cuida apropiadamente vehículo.',
            'plan_mejora': 'Mantener cultura de seguridad. Capacitar a equipo en conducción segura. Ser referente en seguridad vial. Promover cultura de prevención.'
        },
        5: {
            'retroalimentacion': '**Desempeño sobresaliente:** Experto en normas de tránsito. Conducción ejemplar. Cero accidentes. Modelo de seguridad vial. Cuida óptimamente el vehículo.',
            'plan_mejora': 'Mantener excelencia. Liderar programa de seguridad vial. Diseñar protocolo de conducción segura. Capacitar a equipo en prevención de accidentes.'
        }
    }
}

# =====================================================================
# FUNCIONES DE CÁLCULO Y GENERACIÓN DE PLAN
# =====================================================================

def calcular_puntaje_ponderado_mensajero(respuestas):
    """
    Calcula el puntaje ponderado para Mensajero
    Distribución: Org 10%, Obj 40%, Interp 25%, Tec 25%
    """
    pesos_categorias = {
        'Competencias Organizacionales': 10.0,
        'Objetivos - El Hacer': 40.0,
        'Competencias Interpersonales - El Ser': 25.0,
        'Competencias Técnicas - El Saber': 25.0
    }

    respuestas_por_categoria = {}
    for respuesta in respuestas:
        if respuesta.pregunta.categoria == 'Observación SST':
            continue
        categoria = respuesta.pregunta.categoria
        if categoria not in respuestas_por_categoria:
            respuestas_por_categoria[categoria] = []
        respuestas_por_categoria[categoria].append(respuesta)

    puntajes_categorias = {}
    for categoria, lista_respuestas in respuestas_por_categoria.items():
        suma_puntajes = sum(float(r.opcion_seleccionada.valor_numerico) for r in lista_respuestas)
        num_preguntas = len(lista_respuestas)
        promedio_categoria = suma_puntajes / num_preguntas if num_preguntas > 0 else 0
        puntajes_categorias[categoria] = promedio_categoria

    puntaje_total = 0
    detalle_categorias = {}

    for categoria, peso in pesos_categorias.items():
        if categoria in puntajes_categorias:
            promedio = puntajes_categorias[categoria]
            puntaje_categoria_porcentaje = ((promedio - 1) / 4) * 100
            contribucion = (puntaje_categoria_porcentaje * peso) / 100
            puntaje_total += contribucion

            detalle_categorias[categoria] = {
                'promedio': round(promedio, 2),
                'porcentaje': round(puntaje_categoria_porcentaje, 2),
                'ponderacion': peso,
                'contribucion': round(contribucion, 2)
            }

    puntaje_escala_5 = 1 + (puntaje_total / 100) * 4

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


def generar_plan_mejora_mensajero(respuestas_evaluacion, resultado_evaluacion):
    """
    Genera plan de mejora específico para Mensajero
    """
    planes = []

    plan_header = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║              PLAN DE MEJORA - EVALUACIÓN ANUAL DE DESEMPEÑO                  ║
║                               MENSAJERO                                      ║
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

    planes.append("EVALUACIÓN POR COMPETENCIA:\n\n")

    contador = 1

    mapeo_competencias = {
        1: 'comunicacion',
        2: 'trabajo_equipo',
        3: 'mejora_continua',
        4: 'objetivos',
        5: 'atencion_detalle',
        6: 'planeacion_programacion',
        7: 'comunicacion_efectiva',
        8: 'presentacion_personal',
        9: 'conocimiento_rutas',
        10: 'herramientas_tecnologicas',
        11: 'normas_transito'
    }

    RESPUESTAS_MENSAJERO = {
        'comunicacion': COMUNICACION_MENSAJERO,
        'trabajo_equipo': TRABAJO_EQUIPO_MENSAJERO,
        'mejora_continua': MEJORA_CONTINUA_MENSAJERO,
        'objetivos': OBJETIVOS_MENSAJERO,
        'atencion_detalle': ATENCION_DETALLE_MENSAJERO,
        'planeacion_programacion': PLANEACION_PROGRAMACION_MENSAJERO,
        'comunicacion_efectiva': COMUNICACION_EFECTIVA_MENSAJERO,
        'presentacion_personal': PRESENTACION_PERSONAL_MENSAJERO,
        'conocimiento_rutas': CONOCIMIENTO_RUTAS_MENSAJERO,
        'herramientas_tecnologicas': HERRAMIENTAS_TECNOLOGICAS_MENSAJERO,
        'normas_transito': NORMAS_TRANSITO_MENSAJERO
    }

    for respuesta in respuestas_evaluacion.order_by('pregunta__orden'):
        if respuesta.pregunta.categoria == 'Observación SST':
            continue

        numero_pregunta = respuesta.pregunta.orden
        nombre_competencia = respuesta.pregunta.pregunta
        puntuacion = int(respuesta.opcion_seleccionada.valor_numerico) if respuesta.opcion_seleccionada else 0
        clave_competencia = mapeo_competencias.get(numero_pregunta)

        plan_texto = f"{contador}. {nombre_competencia}\n"
        plan_texto += f"   Calificación: {puntuacion}/5\n"

        if respuesta.comentarios_evaluador:
            plan_texto += f"   💬 Comentario del evaluador: {respuesta.comentarios_evaluador}\n"
        plan_texto += "\n"

        if puntuacion == 5:
            plan_texto += "   ✅ ¡EXCELENTE DESEMPEÑO!\n"
            plan_texto += "   El empleado ha demostrado dominio excepcional en esta competencia.\n"
            plan_texto += "   Continue con este nivel de excelencia.\n"
        else:
            if clave_competencia and clave_competencia in RESPUESTAS_MENSAJERO:
                competencia_data = RESPUESTAS_MENSAJERO[clave_competencia]
                if puntuacion in competencia_data['respuestas']:
                    datos_respuesta = competencia_data['respuestas'][puntuacion]
                    plan_texto += f"   📋 PLAN DE ACCIÓN:\n"
                    plan_mejora_texto = datos_respuesta.get('plan_mejora', '')
                    items_plan = [item.strip() for item in plan_mejora_texto.split('.') if item.strip()]
                    for idx, item in enumerate(items_plan[:3], 1):
                        plan_texto += f"   {idx}. {item}.\n"
                    if puntuacion <= 4:
                        plan_texto += f"\n   ⚠️  REQUIERE SEGUIMIENTO BIMENSUAL\n"
                else:
                    plan_texto += f"   📋 PLAN DE ACCIÓN:\n"
                    plan_texto += f"   1. Revisar procedimientos relacionados con esta competencia.\n"
                    plan_texto += f"   2. Solicitar retroalimentación del supervisor.\n"
                    plan_texto += f"   3. Establecer metas específicas de mejora.\n"
            else:
                plan_texto += f"   📋 PLAN DE ACCIÓN:\n"
                plan_texto += f"   1. Revisar procedimientos relacionados con esta competencia.\n"
                plan_texto += f"   2. Solicitar retroalimentación del supervisor.\n"
                plan_texto += f"   3. Establecer metas específicas de mejora.\n"

        plan_texto += "\n" + "-"*80 + "\n\n"
        planes.append(plan_texto)
        contador += 1

    planes.append("="*80 + "\n")
    planes.append("OBSERVACIÓN DE SEGURIDAD Y SALUD EN EL TRABAJO (SST)\n")
    planes.append("="*80 + "\n\n")
    planes.append("Nota: La evaluación de uso de EPP se registra por separado y no afecta el puntaje general.\n")
    planes.append("Esta observación es fundamental para garantizar la seguridad del empleado.\n\n")

    planes.append("="*80 + "\n")
    planes.append("INSTRUCCIONES:\n")
    planes.append("1. Este plan debe ser revisado y aceptado por el empleado.\n")
    planes.append("2. Se realizarán 3 seguimientos bimestrales (cada 2 meses) durante 6 meses.\n")
    planes.append("3. Al finalizar el período se realizará una evaluación final del plan.\n")
    planes.append("4. Las competencias con seguimiento bimensual deben mostrar avance progresivo.\n")
    planes.append("="*80 + "\n")

    return "".join(planes)
