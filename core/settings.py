from datetime import timedelta
from pathlib import Path

from decouple import config as env_config

from .config.configuration_manager import ConfigurationManager

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = env_config('SECRET_KEY', 'django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

DEBUG = env_config('DEBUG', cast=bool, default=False)
DDT = env_config('DDT', cast=bool, default=False)
SILK = env_config('SILK', cast=bool, default=False)
DEV_ENV = env_config('DEV_ENV', default='staging')
LOCAL_DEV = env_config('LOCAL_DEV', cast=bool, default=False)
ALLOWED_HOSTS = env_config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')], default='')
CSRF_TRUSTED_ORIGINS = env_config('CSRF_TRUSTED_ORIGINS', cast=lambda v: [s.strip() for s in v.split(',')], default='')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # THIRD PARTY APPS
    'rest_framework',
    'corsheaders',
    'django_extensions',
    'django_filters',
    'django_celery_results',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'rest_framework_simplejwt',
    'imagekit',
    'django_celery_beat',
    # CUSTOM APPS
    'authentication',
    'utilities',
    'wallets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

if DDT:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

if SILK:

    def custom_intercept(request):
        SILKY_IGNORE_PATHS = ['/api/silk', '/api/docs', '/api/v1/schema', '/api/admin']
        return not any([path in request.path for path in SILKY_IGNORE_PATHS])

    INSTALLED_APPS.append('silk')
    MIDDLEWARE.append('silk.middleware.SilkyMiddleware')
    # SILKY_PYTHON_PROFILER = True
    SILKY_INTERCEPT_FUNC = custom_intercept


def show_toolbar(request):
    return DDT


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = "core.asgi.application"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': ConfigurationManager.db_name(),
        'USER': ConfigurationManager.db_username(),
        'PASSWORD': ConfigurationManager.db_password(),
        'HOST': ConfigurationManager.db_host(),
        'PORT': ConfigurationManager.db_port(),
        "OPTIONS": {
            "pool": {
                "min_size": 5,
                "max_size": 10,
                "timeout": 120,
                "max_lifetime": 3600,
                "max_idle": 600,
                "reconnect_timeout": 300,
            },
        },
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': ConfigurationManager.db_name(),
        'USER': ConfigurationManager.db_username(),
        'PASSWORD': ConfigurationManager.db_password(),
        'HOST': ConfigurationManager.replica_host(),
        'PORT': ConfigurationManager.db_port(),
        "OPTIONS": {
            "pool": {
                "min_size": 5,
                "max_size": 10,
                "timeout": 120,
                "max_lifetime": 3600,
                "max_idle": 600,
                "reconnect_timeout": 300,
            },
        },
    },
}

DATABASE_ROUTERS = [
    "core.routers.DBRouter",
]


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


AUTH_USER_MODEL = 'authentication.User'


REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'utils.custom_paginator.CustomPaginator',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'core.auth.authentication.XAPIKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'burst': '10/minute',
    },
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
SEARCH_PARAM = 'search'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1) if DEV_ENV == 'staging' or LOCAL_DEV else timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30) if DEV_ENV == 'staging' or LOCAL_DEV else timedelta(days=1),
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'UPDATE_LAST_LOGIN': True,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Digital Wallet APIs',
    'VERSION': '1.0.0',
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'COMPONENT_SPLIT_REQUEST': True,
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_PUBLIC': False,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env_config('REDIS_URL', default='redis://localhost:6379/1'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


CORS_ALLOW_ORIGINS = env_config('CORS_ALLOW_ORIGINS', cast=lambda v: [s.strip() for s in v.split(',')], default='')
CORS_ALLOW_HEADERS = (
    'accept',
    'authorization',
    'content-type',
    'Content-Type',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-api-key',
    'content-disposition',
)
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',  # Include OPTIONS method to allow preflight requests
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'api/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'api/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": MEDIA_ROOT,
            "base_url": MEDIA_URL,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CELERY_BROKER_URL = env_config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env_config('CELERY_RESULT_BACKEND', default='django-db')
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_WORKER_CONCURRENCY = env_config('CELERY_WORKER_CONCURRENCY', cast=int, default=2)
CELERY_WORKER_PREFETCH_MULTIPLIER = env_config('CELERY_PREFETCH_MULTIPLIER', cast=int, default=1)
CELERY_CACHE_BACKEND = env_config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_TASK_TRACK_STARTED = env_config('CELERY_TASK_TRACK_STARTED', cast=bool, default=True)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = env_config('CELERY_TASK_TRACK_STARTED', cast=bool, default=True)
CELERY_BROKER_CONNECTION_MAX_RETRIES = env_config('CELERY_BROKER_CONNECTION_MAX_RETRIES', cast=int, default=3)
