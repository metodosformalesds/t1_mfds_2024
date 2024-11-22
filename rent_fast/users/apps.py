from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuración de la aplicación Users en Django.

    Esta clase define la configuración de la aplicación 'users', que es responsable de gestionar
    los usuarios del sistema, incluyendo arrendadores y arrendatarios.

    Atributos:
    - default_auto_field: Define el tipo de campo para las claves primarias (en este caso, BigAutoField).
    - name: El nombre completo de la aplicación, que debe coincidir con el nombre de la carpeta de la app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
