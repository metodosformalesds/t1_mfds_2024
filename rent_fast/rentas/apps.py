from django.apps import AppConfig


class RentasConfig(AppConfig):
    """
    Daniel Esqueda
    Configuración de la aplicación Rentas en Django.
    
    Esta clase hereda de `AppConfig` y permite personalizar la configuración de la aplicación
    cuando se carga en el proyecto Django. La configuración de la aplicación se define mediante
    el nombre de la aplicación y el campo predeterminado para los ID automáticos de los modelos.

    Atributos:
    - default_auto_field (str): Define el tipo de campo predeterminado para los identificadores automáticos de los modelos. En este caso, se utiliza `BigAutoField`.
    - name (str): El nombre de la aplicación Django. En este caso, la aplicación se llama 'rentas'.

    Uso:
    - Esta clase es utilizada por Django para identificar y cargar la configuración de la aplicación "rentas" dentro del proyecto.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rentas'
