#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Ejecuta tareas administrativas de Django.

    Este script es utilizado para ejecutar diversos comandos de administración de Django
    como iniciar el servidor, aplicar migraciones, crear superusuario, entre otros. 
    Configura el entorno de Django, establece el módulo de configuración y ejecuta 
    los comandos necesarios.

    Se asegura de que Django esté instalado y disponible en el entorno actual antes de
    proceder a ejecutar el comando solicitado.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_fast.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
