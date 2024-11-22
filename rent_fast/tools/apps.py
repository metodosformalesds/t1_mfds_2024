from django.apps import AppConfig


class ToolsConfig(AppConfig):
    """
    Configuración de la aplicación 'tools' en Django.

    Esta clase hereda de AppConfig y se utiliza para configurar las opciones específicas de la aplicación.
    Django utiliza esta clase para gestionar la configuración y comportamiento de la aplicación dentro del proyecto.

    Atributos:
    default_auto_field (str): Define el tipo de campo que se utilizará por defecto para los identificadores 
    (claves primarias) de los modelos en esta aplicación. Se ha establecido como 'BigAutoField', que es un 
    campo de auto-incremento que utiliza un tipo de datos más grande.
    
    name (str): El nombre de la aplicación. Django usará esta propiedad para identificar y registrar la 
    aplicación dentro del proyecto. En este caso, la aplicación se llama 'tools'.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tools'
