# apps/recognition/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import TipoActividad, HistorialPuntos
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='training.InscripcionCapacitacion')
def asignar_puntos_capacitacion_completada(sender, instance, created, **kwargs):
    """
    Signal para asignar puntos automáticamente cuando se completa una capacitación
    Se activa cuando el estado de una inscripción cambia a 'aprobado'
    """
    if not created and instance.estado == 'aprobado':
        # Solo asignar puntos si no se han asignado antes
        if not HistorialPuntos.objects.filter(
            empleado=instance.empleado,
            tipo_actividad__codigo='CAP_COMPLETADA',
            objeto_relacionado_tipo='training.InscripcionCapacitacion',
            objeto_relacionado_id=instance.id
        ).exists():
            
            try:
                tipo_actividad = TipoActividad.objects.get(codigo='CAP_COMPLETADA')
                
                # Calcular puntos base con multiplicador si aplica
                puntos = int(tipo_actividad.puntos_base * tipo_actividad.multiplicador_complejidad)
                
                # Crear historial de puntos
                HistorialPuntos.objects.create(
                    empleado=instance.empleado,
                    tipo_actividad=tipo_actividad,
                    puntos=puntos,
                    descripcion=f'Capacitación completada: {instance.capacitacion.nombre}',
                    objeto_relacionado_tipo='training.InscripcionCapacitacion',
                    objeto_relacionado_id=instance.id,
                    validado=True,
                    validado_por=None  # Sistema automático
                )
                
                logger.info(f"Puntos asignados automáticamente: {puntos} pts a {instance.empleado.nombre_completo} por completar {instance.capacitacion.nombre}")
                
            except TipoActividad.DoesNotExist:
                logger.error("TipoActividad 'CAP_COMPLETADA' no encontrado")


@receiver(post_save, sender='evaluations.IntentoValoracion')
def asignar_puntos_evaluacion_aprobada(sender, instance, created, **kwargs):
    """
    Signal para asignar puntos automáticamente cuando se aprueba una evaluación
    Se activa cuando se marca como aprobado=True y completado=True
    """
    if instance.aprobado and instance.completado:
        # Solo asignar puntos si no se han asignado antes
        if not HistorialPuntos.objects.filter(
            empleado=instance.inscripcion.empleado,
            objeto_relacionado_tipo='evaluations.IntentoValoracion',
            objeto_relacionado_id=instance.id
        ).exists():
            
            try:
                # Determinar tipo de actividad según el porcentaje de acierto
                codigo_tipo = 'EVAL_SATISFACTORIA'  # Por defecto
                
                if instance.porcentaje_acierto:
                    if instance.porcentaje_acierto >= 95:
                        codigo_tipo = 'EVAL_EXCELENTE'
                    elif instance.porcentaje_acierto >= 85:
                        codigo_tipo = 'EVAL_BUENA'
                    else:
                        codigo_tipo = 'EVAL_SATISFACTORIA'
                
                tipo_actividad = TipoActividad.objects.get(codigo=codigo_tipo)
                
                # Calcular puntos base con multiplicador
                puntos = int(tipo_actividad.puntos_base * tipo_actividad.multiplicador_complejidad)
                
                # Crear historial de puntos
                HistorialPuntos.objects.create(
                    empleado=instance.inscripcion.empleado,
                    tipo_actividad=tipo_actividad,
                    puntos=puntos,
                    descripcion=f'Evaluación aprobada con {instance.porcentaje_acierto}% de acierto',
                    objeto_relacionado_tipo='evaluations.IntentoValoracion',
                    objeto_relacionado_id=instance.id,
                    validado=True,
                    validado_por=None  # Sistema automático
                )
                
                logger.info(f"Puntos asignados automáticamente: {puntos} pts a {instance.inscripcion.empleado.nombre_completo} por evaluación ({codigo_tipo})")
                
            except TipoActividad.DoesNotExist:
                logger.error(f"TipoActividad '{codigo_tipo}' no encontrado")


@receiver(post_save, sender='surveys.ParticipacionEncuesta')
def asignar_puntos_encuesta_completada(sender, instance, created, **kwargs):
    """
    Signal para asignar puntos automáticamente cuando se completa una encuesta
    Se activa cuando completada=True
    """
    if instance.completada and instance.empleado:  # Solo si no es anónima
        # Solo asignar puntos si no se han asignado antes
        if not HistorialPuntos.objects.filter(
            empleado=instance.empleado,
            tipo_actividad__codigo='ENCUESTA_RESP',
            objeto_relacionado_tipo='surveys.ParticipacionEncuesta',
            objeto_relacionado_id=instance.id
        ).exists():
            
            try:
                tipo_actividad = TipoActividad.objects.get(codigo='ENCUESTA_RESP')
                
                # Calcular puntos base con multiplicador
                puntos = int(tipo_actividad.puntos_base * tipo_actividad.multiplicador_complejidad)
                
                # Crear historial de puntos
                HistorialPuntos.objects.create(
                    empleado=instance.empleado,
                    tipo_actividad=tipo_actividad,
                    puntos=puntos,
                    descripcion=f'Encuesta completada: {instance.encuesta.nombre}',
                    objeto_relacionado_tipo='surveys.ParticipacionEncuesta',
                    objeto_relacionado_id=instance.id,
                    validado=True,
                    validado_por=None  # Sistema automático
                )
                
                logger.info(f"Puntos asignados automáticamente: {puntos} pts a {instance.empleado.nombre_completo} por completar encuesta {instance.encuesta.nombre}")
                
            except TipoActividad.DoesNotExist:
                logger.error("TipoActividad 'ENCUESTA_RESP' no encontrado")


@receiver(post_save, sender='evaluations.ResultadoEvaluacion')
def asignar_puntos_evaluacion_desempeno(sender, instance, created, **kwargs):
    """
    Signal para asignar puntos automáticamente cuando se finaliza una evaluación de desempeño
    Se activa cuando estado='finalizada' y tiene calificación final
    """
    if hasattr(instance, 'estado') and instance.estado == 'finalizada' and instance.calificacion_final:
        # Solo asignar puntos si no se han asignado antes
        if not HistorialPuntos.objects.filter(
            empleado=instance.empleado_evaluado,
            objeto_relacionado_tipo='evaluations.ResultadoEvaluacion',
            objeto_relacionado_id=instance.id
        ).exists():
            
            try:
                # Determinar tipo de actividad según la calificación final
                codigo_tipo = 'EVAL_SATISFACTORIA'  # Por defecto
                
                # Asumir escala de 1-5, ajustar según tu sistema
                if instance.calificacion_final >= 4.5:
                    codigo_tipo = 'EVAL_EXCELENTE'
                elif instance.calificacion_final >= 3.5:
                    codigo_tipo = 'EVAL_BUENA'
                else:
                    codigo_tipo = 'EVAL_SATISFACTORIA'
                
                tipo_actividad = TipoActividad.objects.get(codigo=codigo_tipo)
                
                # Calcular puntos base con multiplicador
                puntos = int(tipo_actividad.puntos_base * tipo_actividad.multiplicador_complejidad)
                
                # Crear historial de puntos
                HistorialPuntos.objects.create(
                    empleado=instance.empleado_evaluado,
                    tipo_actividad=tipo_actividad,
                    puntos=puntos,
                    descripcion=f'Evaluación de desempeño finalizada con calificación {instance.calificacion_final}',
                    objeto_relacionado_tipo='evaluations.ResultadoEvaluacion',
                    objeto_relacionado_id=instance.id,
                    validado=True,
                    validado_por=None  # Sistema automático
                )
                
                logger.info(f"Puntos asignados automáticamente: {puntos} pts a {instance.empleado_evaluado.nombre_completo} por evaluación de desempeño ({codigo_tipo})")
                
            except TipoActividad.DoesNotExist:
                logger.error(f"TipoActividad '{codigo_tipo}' no encontrado")
            except AttributeError as e:
                logger.error(f"Error en estructura del modelo ResultadoEvaluacion: {e}")