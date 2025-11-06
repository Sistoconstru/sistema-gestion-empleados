from django.apps import AppConfig

class EmployeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.employees'  # Asegúrate que este sea el nombre correcto de tu app

    def ready(self):
        import apps.employees.signals  # Importa las señales
        import apps.employees.signals_evaluaciones  # Importa el signal de evaluaciones por cargo