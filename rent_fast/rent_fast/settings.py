"""
Configuraciones de Django para el proyecto rent_fast.

Este archivo contiene las configuraciones para ejecutar Django en diferentes entornos, incluyendo desarrollo y producción.
Define configuraciones clave como las conexiones a bases de datos, configuraciones de autenticación, credenciales de API de terceros, rutas de archivos estáticos y medios, configuraciones de seguridad, configuraciones de correo electrónico, y mucho más.

Las configuraciones incluyen:

- Configuraciones de seguridad para diferentes entornos (por ejemplo, producción vs desarrollo).
- Conexión a la base de datos, incluyendo credenciales de PostgreSQL desde variables de entorno.
- Claves de API de terceros para servicios como PayPal, Uber, Azure Face API, AWS Rekognition e IDAnalyzer.
- Configuración del backend de correo electrónico utilizando Gmail SMTP.
- Configuración de la capa de canales para la comunicación WebSockets.
- Configuración de internacionalización (idioma y zona horaria).
- Configuración para la carga y manejo de archivos estáticos y de medios.
- Redirecciones de autenticación y login para la gestión de usuarios.
- Configuración para la autenticación social mediante Google con `django-allauth`.

Este archivo no debe compartirse públicamente, especialmente por la inclusión de información sensible como claves API y contraseñas.
"""

from pathlib import Path

import os

import environ
PAYPAL_CLIENT_ID = "AbuWXT83G4O4wSbBHtRSTf5aThMIaKEnUvvFZxrUue5BNQPtqwvtuvgDi4dMYRjwa_zbn7CYcr-gw0qh"
PAYPAL_CLIENT_SECRET = "EJSxFjhKKUX1PssUUju1ppZSs6JtPzcmV0MAPRlvS06BOAM6CpN92p9TdpEQqop_Wr4UeIcsZGkm05mC"
PAYPAL_MODE = "sandbox"  # Cambia a "live" en producción

# Configuración para entornos de desarrollo y producción
if os.environ.get('DJANGO_ENV') == 'production':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Define BASE_DIR para obtener la ruta base del proyecto

BASE_DIR = Path(__file__).resolve().parent.parent


# Ahora puedes usar BASE_DIR para definir rutas
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configura el almacenamiento temporal de archivos
FILE_UPLOAD_TEMP_DIR = os.path.join(MEDIA_ROOT, 'tmp')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

IDANALYZER_API_KEY = env('IDANALYZER_API_KEY')
UBER_CLIENT_ID = '6QWax6cLboC1f6TdJ7eYkr3GBxvSHLTc'
UBER_CLIENT_SECRET = 'D6Hb2hWO93NEIejQmjOyhkX3ZKF_-bYU46w8DxV2'  # Copia aquí tu Client Secret de Uber


# Azure Face API settings
AZURE_FACE_API_KEY = "4R2GHd5yKi9csgHDhZbSCSASDpd8383zvQd1111VnAaxL1tfc6wOJQQJ99AKACYeBjFXJ3w3AAAKACOG27Qb"
AZURE_FACE_API_ENDPOINT = "https://rentfast12.cognitiveservices.azure.com"

AWS_ACCESS_KEY_ID = 'AKIA5FTZCUUIAEVXO7EW'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'us-east-1'  # Ajusta la región según tu preferencia

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--s+12dn1clpyqk_w5l@3seh72h012vipmuv)bxrh@!)9vt#^+5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1","35.162.85.24", "localhost", "00lar.pythonanywhere.com", "https://8000-idx-t1mfds2024git-1729092128078.cluster-3ch54x2epbcnetrm6ivbqqebjk.cloudworkstations.dev",'rentfast.live', 'www.rentfast.live']
CSRF_TRUSTED_ORIGINS = ['https://8000-idx-t1mfds2024git-1729092128078.cluster-3ch54x2epbcnetrm6ivbqqebjk.cloudworkstations.dev','https://rentfast.live', 'https://www.rentfast.live']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "formtools",
    "crispy_forms",
    "crispy_tailwind",
    'widget_tweaks',
    "requests",
    "users",
    "tools",
    'rentas',
    'channels',
#allauth appss
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
        # google
    'allauth.socialaccount.providers.google',

]

ASGI_APPLICATION = "rent_fast.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

SITE_ID = 1
 
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': {
            'profile',
            'email'},
        'OAUTH_PARAMS': {'access_type': 'online'},
        'AUTH_PKCE_ENABLED': True,
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': True,
        'CLIENT_ID': '1081665465762-0a9ippsar614nr1758utua7luc3ojnuk.apps.googleusercontent.com',  
        'SECRET': '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',  
    }
}

SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_USERNAME_REQUIRED = False
LOGIN_REDIRECT_URL = '/registro/'  
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
 
 
LOGIN_REDIRECT_URL = '/registro/'
ACCOUNT_LOGOUT_REDIRECT_URL = 'login'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'rent_fast.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates")
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.notificaciones_no_leidas',
                
            ],  
        },
    },
]

WSGI_APPLICATION = 'rent_fast.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "postgres",
        "HOST": "db-rent-fast.clqcu0mgqo6c.us-east-1.rds.amazonaws.com",
        "PORT": "5432",
        "USER": env.str("DJANGO_DB_USER"),
        "PASSWORD": env.str("DJANGO_DB_PASSWORD")
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

CRISPY_TEMPLATE_PACK = "tailwind"

LOGIN_REDIRECT_URL = '/herramientas/'

LOGOUT_REDIRECT_URL = "login"

# Credenciales de Uber Direct API
UBER_CLIENT_ID = 'HP1ZTn6E9__cvhOov8B_aWaQwqoPzl_f'
UBER_CLIENT_SECRET = 'suwS-YLA_xGousd4dOoj55gqQeli'
UBER_REDIRECT_URI = 'http://127.0.0.1:8000/herramientas/uber/callback/'

# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'rentfast64@gmail.com'  # Cambia a tu dirección de Gmail
EMAIL_HOST_PASSWORD = 'kwrzmaebrnxfllvf'  # Cambia a tu contraseña de Gmail o, preferiblemente, a una contraseña de aplicación
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LANGUAGE_CODE = 'es' 
GOOGLE_MAPS_API_KEY = "AIzaSyAWGHYEvO4RWJf0NbdEDP_x-o_zk2T-nUA"