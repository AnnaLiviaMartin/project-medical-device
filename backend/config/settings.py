"""
Django settings for config project.

Fuer die lokale Entwicklung funktionieren die Standardwerte unveraendert
(wie vorher). Fuer Deployment (z.B. Azure Container Apps) werden alle
sicherheitsrelevanten und umgebungsabhaengigen Werte ueber Umgebungs-
variablen gesteuert - siehe backend/.env.example fuer eine vollstaendige
Liste.
"""

import os
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_list(name, default):
    value = os.environ.get(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
# Lokal faellt das auf den alten Dev-Key zurueck, in Produktion MUSS
# DJANGO_SECRET_KEY gesetzt sein (siehe entrypoint.sh Warnung).
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-c%#lt89v5o-$597i#g%tso36j%v5wf2%60bhm2904wgr0uc10g",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _env_bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])


# Application definition

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',

    # Local apps
    'patients',
    'imaging',
    'ml',
    'core',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
#
# DJANGO_DB_PATH kann auf einen gemounteten, persistenten Pfad zeigen
# (z.B. /data/db.sqlite3 bei einem Azure Files Mount), damit die
# SQLite-Datei Container-Neustarts/Redeploys uebersteht.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get("DJANGO_DB_PATH", str(BASE_DIR / 'db.sqlite3')),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
#
# Werden im Container beim Start per collectstatic gesammelt und danach
# direkt von whitenoise ausgeliefert - kein separater Webserver noetig.

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Media files (user-uploaded content, z.B. Roentgenbilder, Grad-CAM-Overlays)
# https://docs.djangoproject.com/en/6.0/topics/files/
#
# DJANGO_MEDIA_ROOT kann - wie DJANGO_DB_PATH - auf einen gemounteten,
# persistenten Pfad zeigen (z.B. /data/media).

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", str(BASE_DIR / 'media'))


# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS / CSRF
#
# In Produktion auf die tatsaechliche Frontend-URL setzen, z.B.:
# DJANGO_CORS_ALLOWED_ORIGINS=https://medic-frontend.happywater-xxxx.azurecontainerapps.io

CORS_ALLOWED_ORIGINS = _env_list(
    "DJANGO_CORS_ALLOWED_ORIGINS", ["http://localhost:3000"]
)

CSRF_TRUSTED_ORIGINS = _env_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])

# Azure Container Apps terminiert TLS am Ingress und leitet intern per
# HTTP weiter - ohne das hier erkennt Django "https" Requests faelschlich
# als unsicher (wichtig fuer CSRF/sichere Cookies im Admin-Login).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
