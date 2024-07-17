from pathlib import Path
import os
from django.contrib.messages import constants as messages
import dj_database_url
from decouple import config

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta (asegúrate de usar una variable de entorno en producción)
SECRET_KEY = config('SECRET_KEY', default='jb&s#=pvct5k#4!w=!lrw7^a(%83%ossrl4j4m&y6as*h2--xq')

# Configuración de depuración
DEBUG = config('DEBUG', default=False, cast=bool)

# Hosts permitidos
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mainapp',
    'widget_tweaks',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Configuración de URLs
ROOT_URLCONF = 'cine_en_tus_manos.urls'

# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuración WSGI
WSGI_APPLICATION = 'cine_en_tus_manos.wsgi.application'

# Configuración de base de datos
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}

# Validadores de contraseñas
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

# Internacionalización
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Archivos estáticos y media
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'mainapp/static'),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Almacenamiento de archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración de la cookie de sesión
SESSION_COOKIE_AGE = 300

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'mainapp.User'

# Redirección de login
LOGIN_URL = 'login'

# Etiquetas de mensajes
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# Configuración de zona horaria
TIME_ZONE = 'America/Mexico_City'
USE_TZ = True
