"""
===============================================================
⚙️ SETTINGS.PY — Configuración principal del proyecto KarMind Core
===============================================================

Este archivo define la configuración base del proyecto Django,
incluyendo parámetros de seguridad, internacionalización,
bases de datos, correo electrónico, archivos estáticos y
servicios externos como Google reCAPTCHA.

La configuración está pensada para ser segura, escalable y
compatible con entornos de desarrollo y producción, 
usando variables de entorno (.env) para proteger credenciales sensibles.
"""

# =======================================================
# 🧩 IMPORTACIONES PRINCIPALES
# =======================================================

from pathlib import Path
import os
from dotenv import load_dotenv       # Carga variables desde .env
from decouple import config           # Lectura segura de variables
load_dotenv()

# =======================================================
# 🏗️ RUTAS BASE DEL PROYECTO
# =======================================================

# BASE_DIR apunta al directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent


# =======================================================
# 🔐 SEGURIDAD BÁSICA
# =======================================================

# Clave secreta de Django — debe almacenarse solo en .env en producción
SECRET_KEY = 'django-insecure-rt_vq18nvy1y*&-t^p$hw-n96pia2!j_&(w#aazr_&*jw(+4=1'

# Activar modo debug (solo en desarrollo)
DEBUG = True

# Hosts permitidos (debe configurarse en despliegue)
ALLOWED_HOSTS = []


# =======================================================
# 🧱 APLICACIONES INSTALADAS
# =======================================================

INSTALLED_APPS = [

    # --- Django Core ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # --- Aplicaciones Locales ---
    'core',  # App principal del sitio (gestión de entidades y configuración)

    # --- Aplicaciones de Terceros ---
    'import_export',     # Importación/exportación de datos desde admin
    'django_recaptcha',  # Protección con Google reCAPTCHA v2
]


# =======================================================
# 🧩 MIDDLEWARE
# =======================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =======================================================
# 🌐 CONFIGURACIÓN DE URLS Y TEMPLATES
# =======================================================

ROOT_URLCONF = 'karmind_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Ruta personalizada para los templates en el directorio frontend
        'DIRS': [BASE_DIR.parent / 'frontend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'karmind_core.wsgi.application'


# =======================================================
# 🧮 CONFIGURACIÓN DE BASE DE DATOS
# =======================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}


# =======================================================
# 🔑 VALIDADORES DE CONTRASEÑA
# =======================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =======================================================
# 🌎 INTERNACIONALIZACIÓN Y LOCALIZACIÓN
# =======================================================

LANGUAGE_CODE = 'es-co'          # Español (Colombia)
TIME_ZONE = 'America/Bogota'     # GMT-5
USE_I18N = True
USE_L10N = True
USE_TZ = True


# =======================================================
# 🖼️ ARCHIVOS ESTÁTICOS Y MULTIMEDIA
# =======================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'frontend' / 'static',
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'frontend', 'media')

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'core.User'


# =======================================================
# 🛡️ CONFIGURACIÓN DE GOOGLE reCAPTCHA
# =======================================================

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')
CAPTCHA_WIDGET_TEMPLATE = 'captcha/widgets/checkbox.html'  # Plantilla personalizada


# =======================================================
# 📧 CONFIGURACIÓN DE CORREO ELECTRÓNICO
# =======================================================

# Credenciales seguras (desde .env)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Configuración estándar para Gmail con TLS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
DEFAULT_RECIPIENT_EMAIL = config('DEFAULT_RECIPIENT_EMAIL')
