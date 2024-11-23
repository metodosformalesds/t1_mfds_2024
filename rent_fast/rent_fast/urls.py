"""
  Juan Carlos & Manuel Villarreal & Daniel Esqueda
Configuración de URLs para el proyecto rent_fast.

Este archivo se encarga de enrutar las URLs a las vistas correspondientes dentro del proyecto Django. A continuación se describe cada uno de los patrones de URL que se incluyen en este archivo.

Los patrones de URL permiten que Django sepa qué función o clase ejecutar para cada solicitud entrante basada en la URL solicitada por el usuario. Esto se configura a través de la lista `urlpatterns`.

"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import LandingPageView

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing_page'),
    path('admin/', admin.site.urls), 
    path("usuarios/", include("users.urls")),
    path("herramientas/", include("tools.urls")),
    path('accounts/', include('allauth.urls')),
    path('rentas/', include('rentas.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

