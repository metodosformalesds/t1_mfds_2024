"""
Configuración de WSGI para el proyecto rent_fast.

Este archivo expone el callable de WSGI como una variable a nivel de módulo llamada ``application``.

WSGI (Web Server Gateway Interface) es el estándar que define cómo un servidor web interactúa con las aplicaciones web en Python. 
Este archivo es utilizado para desplegar la aplicación Django en servidores de producción.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_fast.settings')

application = get_wsgi_application()
