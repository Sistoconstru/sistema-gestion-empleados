# =============================================================================
# apps/evaluations/utils/respuestas_predefinidas.py
# Sistema de respuestas predefinidas para generación automática de planes de mejora
# =============================================================================

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# ===================== RESPUESTAS PREDEFINIDAS =====================

RESPUESTAS_PREDEFINIDAS = {
    "Trabajo en equipo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Presenta dificultades para integrarse con sus compañeros y mantener interacciones respetuosas. Es necesario mejorar la apertura al diálogo y manejo de diferencias.",
            "plan": [
                "Participar en actividades de integración.",
                "Practicar la escucha activa en reuniones.",
                "Solicitar retroalimentación de compañeros después de cada tarea en equipo."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "Demuestra disposición al trabajo en equipo en algunas situaciones, pero aún requiere fortalecer la colaboración constante y la comunicación con sus colegas.",
            "plan": [
                "Promover espacios para coordinar tareas con el equipo.",
                "Identificar situaciones donde se pueda aportar más activamente.",
                "Mantener una actitud conciliadora en momentos de desacuerdo."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Sobresale por su actitud colaborativa, respeto por la diversidad y disposición constante para apoyar al equipo.",
            "plan": [
                "Mantener los hábitos positivos actuales.",
                "Participar en la orientación de nuevos integrantes.",
                "Contribuir proponiendo mejoras para el funcionamiento del equipo."
            ]
        }
    },
    "Compromiso": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "No evidencia constancia ni disposición para apoyar las metas del proceso. A veces evita asumir responsabilidades adicionales.",
            "plan": [
                "Establecer metas personales semanales.",
                "Solicitar acompañamiento para la organización de tareas.",
                "Aumentar la autonomía en actividades de bajo riesgo."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "Se observa compromiso en ciertos momentos, pero debe reforzar la constancia y la autonomía para asumir nuevas responsabilidades.",
            "plan": [
                "Proponer voluntariamente una tarea adicional semanal.",
                "Mejorar la gestión del tiempo.",
                "Registrar avances y revisarlos con su líder."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Demuestra compromiso constante, disposición al esfuerzo adicional y autonomía para asumir actividades que aportan al logro de objetivos.",
            "plan": [
                "Continuar fortaleciendo la iniciativa.",
                "Compartir buenas prácticas con otros colaboradores.",
                "Asumir pequeños roles de liderazgo en su área."
            ]
        }
    },
    "Competencias Interpersonales": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Se requiere mejora en el área de competencias interpersonales.",
            "plan": [
                "Establecer metas específicas para mejorar en esta área.",
                "Solicitar retroalimentación y acompañamiento.",
                "Implementar acciones de mejora continua."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "Se requiere mejora en el área de competencias interpersonales.",
            "plan": [
                "Establecer metas específicas para mejorar en esta área.",
                "Solicitar retroalimentación y acompañamiento.",
                "Implementar acciones de mejora continua."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Se requiere mantener el nivel en el área de competencias interpersonales.",
            "plan": [
                "Mantener las buenas prácticas actuales.",
                "Continuar con el nivel de excelencia demostrado.",
                "Compartir conocimientos con el equipo."
            ]
        }
    },
    "Comunicación": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Tiene dificultades para expresar ideas de forma clara y para escuchar activamente, lo que afecta la coordinación con otros.",
            "plan": [
                "Preparar previamente los temas antes de reuniones.",
                "Practicar resúmenes breves para confirmar entendimiento.",
                "Solicitar retroalimentación sobre claridad comunicativa."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "Su comunicación es adecuada en varias situaciones, aunque aún pueden surgir malentendidos o falta de claridad.",
            "plan": [
                "Organizar mejor las ideas antes de expresarlas.",
                "Preguntar para confirmar acuerdos.",
                "Trabajar en mejorar el tono y la asertividad."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Se comunica de manera clara, coherente y asertiva; facilita acuerdos y demuestra excelente escucha activa.",
            "plan": [
                "Seguir fortaleciendo habilidades comunicativas.",
                "Servir como apoyo para compañeros con dificultades en el tema.",
                "Participar en actividades que requieran negociación o coordinación."
            ]
        }
    },
    "Atención al detalle": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Presenta omisiones frecuentes que afectan la calidad o exactitud del trabajo. Se requiere mejorar la observación de detalles.",
            "plan": [
                "Usar listas de verificación antes de entregar tareas.",
                "Dedicar 5 minutos adicionales a revisar cada actividad.",
                "Solicitar revisión cruzada hasta mejorar consistencia."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "Generalmente es cuidadoso, aunque en ocasiones pasa por alto detalles que pueden mejorar el resultado final.",
            "plan": [
                "Implementar un protocolo personal de revisión.",
                "Asegurar la verificación de información clave.",
                "Practicar mayor concentración en tareas repetitivas."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Demuestra excelente atención al detalle y revisa su trabajo con minuciosidad, lo que reduce errores.",
            "plan": [
                "Continuar aplicando métodos de control de calidad personal.",
                "Compartir buenas prácticas en el equipo.",
                "Apoyar procesos que requieran alto nivel de precisión."
            ]
        }
    },
    "Cumplimiento de normas y procedimientos": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Presenta incumplimientos o desconocimiento de normas internas, lo cual puede afectar la operación.",
            "plan": [
                "Revisar el manual de procedimientos de su área.",
                "Solicitar guía al líder sobre normas críticas.",
                "Realizar autoevaluaciones de cumplimiento semanal."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "Sigue la mayoría de normas, pero requiere mejorar la consistencia y evitar descuidos.",
            "plan": [
                "Aplicar recordatorios o sistemas personales de control.",
                "Revisar procedimientos antes de ejecutar tareas nuevas.",
                "Mantener comunicación con el líder sobre dudas normativas."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Evidencia cumplimiento constante, disciplina y respeto por los procedimientos institucionales.",
            "plan": [
                "Mantener el nivel de cumplimiento.",
                "Apoyar en la inducción de nuevos compañeros.",
                "Proponer mejoras a los procedimientos si identifica oportunidades."
            ]
        }
    },
    "Actitud respecto al trabajo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "Se observa falta de motivación o actitud poco positiva, lo que afecta desempeño e interacción.",
            "plan": [
                "Identificar factores personales que afectan la motivación.",
                "Establecer objetivos diarios claros.",
                "Solicitar acompañamiento del líder."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "En general demuestra una actitud positiva, aunque hay momentos de desánimo o falta de disposición.",
            "plan": [
                "Practicar técnicas de autocontrol emocional.",
                "Mantener proactividad incluso en días complejos.",
                "Pedir retroalimentación sobre su actuación."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Mantiene una actitud positiva, proactiva y orientada al crecimiento, generando un ambiente laboral favorable.",
            "plan": [
                "Continuar reforzando la disposición positiva.",
                "Aportar ideas que promuevan el ambiente laboral.",
                "Motivar a compañeros cuando sea necesario."
            ]
        }
    },
    "Calidad del trabajo": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "El trabajo presenta errores o no cumple los estándares mínimos de calidad, lo cual requiere corrección constante.",
            "plan": [
                "Revisar estándares de calidad del área.",
                "Aplicar controles de revisión antes de entregar cada tarea.",
                "Solicitar orientación técnica para mejorar exactitud."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "Cumple los criterios de calidad, aunque ocasionalmente se presentan errores evitables.",
            "plan": [
                "Incrementar la revisión final.",
                "Identificar qué tipo de errores son recurrentes.",
                "Establecer acciones preventivas."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Desarrolla trabajo de alta calidad, consistente, sin errores y con evidente cuidado y esmero.",
            "plan": [
                "Mantener su metodología de trabajo actual.",
                "Apoyar revisiones de trabajo de otros compañeros.",
                "Explorar formas de optimizar tiempos sin sacrificar calidad."
            ]
        }
    },
    "Calidad": {
        1: {
            "titulo": "⭐ Calificación 1 – No cumple",
            "recomendacion": "El trabajo presenta errores o no cumple los estándares mínimos de calidad, lo cual requiere corrección constante.",
            "plan": [
                "Revisar estándares de calidad del área.",
                "Aplicar controles de revisión antes de entregar cada tarea.",
                "Solicitar orientación técnica para mejorar exactitud."
            ]
        },
        2: {
            "titulo": "⭐ Calificación 2 – Cumple parcialmente",
            "recomendacion": "Cumple los criterios de calidad, aunque ocasionalmente se presentan errores evitables.",
            "plan": [
                "Incrementar la revisión final.",
                "Identificar qué tipo de errores son recurrentes.",
                "Establecer acciones preventivas."
            ]
        },
        3: {
            "titulo": "⭐ Calificación 3 – Cumple totalmente",
            "recomendacion": "Desarrolla trabajo de alta calidad, consistente, sin errores y con evidente cuidado y esmero.",
            "plan": [
                "Mantener su metodología de trabajo actual.",
                "Apoyar revisiones de trabajo de otros compañeros.",
                "Explorar formas de optimizar tiempos sin sacrificar calidad."
            ]
        }
    }
}

# ===================== FUNCIONES PARA GENERACIÓN AUTOMÁTICA =====================

def generar_plan_automatico(respuestas_evaluacion):
    """
    Genera un plan de mejora automático basado en las respuestas de la evaluación
    Mantiene el orden original de las preguntas
    
    Args:
        respuestas_evaluacion: QuerySet de RespuestaEvaluacion
    
    Returns:
        str: Plan de mejora completo con formato específico
    """
    planes = []
    contador_pregunta = 1
    
    print(f"DEBUG: Iniciando generación de plan con {respuestas_evaluacion.count()} respuestas")
    
    # Mapeo de categorías más específico para capturar todas las variaciones
    mapeo_categorias = {
        # Palabras clave para cada categoría
        "Trabajo en equipo": ["trabajo en equipo"],
        "Compromiso": ["compromiso"],
        "Competencias Interpersonales": ["competencias interpersonales", "competencia interpersonal", "interpersonales"],
        "Comunicación": ["comunicacion", "comunicación"],
        "Atención al detalle": ["atención al detalle", "atencion al detalle"],
        "Cumplimiento de normas y procedimientos": ["cumplimiento de las normas", "cumplimiento de normas", "normas y procedimientos"],
        "Actitud respecto al trabajo": ["actitud respecto al trabajo", "actitud respecto"],
        "Calidad del trabajo": ["calidad del trabajo"],
        "Calidad": ["calidad"]  # Para el caso donde solo aparece "Calidad"
    }
    
    # Procesar respuestas manteniendo el orden de las preguntas
    for respuesta in respuestas_evaluacion.order_by('pregunta__orden'):
        categoria_original = respuesta.pregunta.categoria or ""
        pregunta_texto = respuesta.pregunta.pregunta or ""
        puntuacion = int(respuesta.opcion_seleccionada.valor_numerico) if respuesta.opcion_seleccionada else 0
        orden_pregunta = respuesta.pregunta.orden
        
        print(f"DEBUG: Pregunta {orden_pregunta} - '{pregunta_texto[:80]}...' - Categoría: '{categoria_original}' - Puntuación: {puntuacion}")
        
        # Mostrar TODAS las respuestas para diagnóstico
        if puntuacion not in [1, 2, 3]:
            print(f"DEBUG: OMITIDA - Puntuación {puntuacion} no está en rango 1-3")
            continue
        
        # Generar plan para puntuaciones 1, 2 y 3
        categoria_mapeada = None
        categoria_lower = categoria_original.lower().strip()
        pregunta_lower = pregunta_texto.lower().strip()
        
        print(f"DEBUG: Buscando mapeo para categoría '{categoria_original}' y pregunta '{pregunta_texto[:50]}'")
        
        # Primero intentar mapeo exacto por categoría original
        for categoria_destino, palabras_clave in mapeo_categorias.items():
            for palabra in palabras_clave:
                if palabra.lower() == categoria_lower or palabra.lower() in categoria_lower:
                    categoria_mapeada = categoria_destino
                    print(f"DEBUG: Mapeada a '{categoria_destino}' por coincidencia con '{palabra}'")
                    break
            if categoria_mapeada:
                break
        
        # Si no se encontró mapeo, verificar si la categoría original existe directamente
        if not categoria_mapeada and categoria_original:
            # Intentar con diferentes formatos de la categoría original
            formatos_categoria = [
                categoria_original,
                categoria_original.title(),
                categoria_original.strip(),
                categoria_original.title().strip()
            ]
            
            for formato in formatos_categoria:
                if formato in RESPUESTAS_PREDEFINIDAS:
                    categoria_mapeada = formato
                    print(f"DEBUG: Usando categoría original directa: '{formato}'")
                    break
        
        # Si aún no se encontró, usar fallback
        if not categoria_mapeada:
            categoria_mapeada = categoria_original.title() if categoria_original else f"Pregunta {orden_pregunta}"
            print(f"DEBUG: Usando fallback: '{categoria_mapeada}'")
        
        # Generar el plan para esta pregunta específica
        plan_texto = ""
        
        if categoria_mapeada in RESPUESTAS_PREDEFINIDAS and puntuacion in RESPUESTAS_PREDEFINIDAS[categoria_mapeada]:
            datos_plan = RESPUESTAS_PREDEFINIDAS[categoria_mapeada][puntuacion]
            
            # Usar el número de pregunta original
            plan_texto = f"{orden_pregunta}. {categoria_mapeada}: {datos_plan['titulo']}\n"
            plan_texto += f"Recomendación:\n{datos_plan['recomendacion']}\n\n"
            plan_texto += "Plan de mejora:\n"
            
            for item in datos_plan['plan']:
                plan_texto += f"{item}\n"
            
            # Marcar si requiere seguimiento (solo para puntajes 1 y 2)
            if puntuacion in [1, 2]:
                plan_texto += "REQUIERE_SEGUIMIENTO\n"
            
            print(f"DEBUG: Plan generado para pregunta {orden_pregunta}, categoría '{categoria_mapeada}' con puntuación {puntuacion}")
        else:
            # Fallback para categorías no mapeadas
            if puntuacion == 1:
                titulo = "⭐ Calificación 1 – No cumple"
            elif puntuacion == 2:
                titulo = "⭐ Calificación 2 – Cumple parcialmente"
            else:
                titulo = "⭐ Calificación 3 – Cumple totalmente"
            
            plan_texto = f"{orden_pregunta}. {categoria_mapeada}: {titulo}\n"
            plan_texto += f"Recomendación:\nSe requiere {'mejora' if puntuacion <= 2 else 'mantener el nivel'} en el área de {categoria_original.lower()}.\n\n"
            plan_texto += "Plan de mejora:\n"
            
            if puntuacion <= 2:
                plan_texto += "Establecer metas específicas para mejorar en esta área.\n"
                plan_texto += "Solicitar retroalimentación y acompañamiento.\n"
                plan_texto += "Implementar acciones de mejora continua.\n"
                plan_texto += "REQUIERE_SEGUIMIENTO\n"
            else:
                plan_texto += "Mantener las buenas prácticas actuales.\n"
                plan_texto += "Continuar con el nivel de excelencia demostrado.\n"
                plan_texto += "Compartir conocimientos con el equipo.\n"
            
            print(f"DEBUG: Plan fallback generado para pregunta {orden_pregunta}, categoría '{categoria_mapeada}' con puntuación {puntuacion}")
        
        plan_texto += "\n"
        planes.append(plan_texto)
    
    print(f"DEBUG: Total de preguntas procesadas: {len(planes)}")
    
    if not planes:
        return "No se requiere plan de mejora específico. El empleado ha demostrado un desempeño satisfactorio en todas las áreas evaluadas."
    
    plan_final = "".join(planes)
    plan_final += "Observaciones del evaluador:\n[Campo opcional para comentarios adicionales del evaluador]\n"
    
    return plan_final

def crear_seguimientos_bimensuales(plan_mejora):
    """
    Crea automáticamente seguimientos bimensuales para un plan de mejora
    
    Args:
        plan_mejora: Instancia de PlanMejoraPredefinido
    """
    from ..models import SeguimientoBimensual
    
    fecha_inicio = timezone.now().date()
    
    # Crear 3 seguimientos (bimestre 1, 2 y 3 = 6 meses total)
    for i in range(1, 4):
        fecha_seguimiento = fecha_inicio + relativedelta(months=2*i)
        
        SeguimientoBimensual.objects.get_or_create(
            plan_mejora=plan_mejora,
            numero_bimestre=i,
            defaults={
                'fecha_limite': fecha_seguimiento,
                'estado': 'pendiente'
            }
        )

def obtener_plan_por_categoria_y_nivel(categoria, nivel):
    """
    Obtiene un plan específico por categoría y nivel

    Args:
        categoria (str): Nombre de la categoría
        nivel (int): Nivel de puntuación (1, 2, 3)

    Returns:
        dict: Datos del plan de mejora
    """
    if categoria in RESPUESTAS_PREDEFINIDAS and nivel in RESPUESTAS_PREDEFINIDAS[categoria]:
        return RESPUESTAS_PREDEFINIDAS[categoria][nivel]
    return None

def puede_generar_evaluacion_final(plan_mejora):
    """
    Verifica si se puede generar la evaluación final del plan de mejora
    Se requiere que todos los seguimientos bimensuales estén completados (3 seguimientos)

    Args:
        plan_mejora: Instancia de PlanMejoraPredefinido

    Returns:
        bool: True si se pueden generar la evaluación final, False en caso contrario
    """
    from ..models import SeguimientoBimensual

    # Obtener todos los seguimientos del plan
    seguimientos = SeguimientoBimensual.objects.filter(plan_mejora=plan_mejora)

    # Verificar que existan 3 seguimientos
    if seguimientos.count() != 3:
        return False

    # Verificar que todos estén completados
    completados = seguimientos.filter(estado='completado').count()

    return completados == 3