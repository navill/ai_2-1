import os
from datetime import timedelta
from pathlib import Path
import redis
from conf_secret import secrets

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = secrets['SECRET_KEY']

DEBUG = True

# if DEBUG:
#     from config.rest_conf import dev
# else:
#     from config.rest_conf import prod

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third party app
    'rest_framework',
    'corsheaders',
    # apps
    'accounts',
    'files',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # corsheader
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'
AUTH_USER_MODEL = 'accounts.CommonUser'
# MIGRATION_MODULES = {'accounts': 'accounts.db_migrations'}

REDIS_HOST = 'localhost'
REDIS_PORT = 6001
REDIS_DB = 1
REDIS_CONN_POOL_1 = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)

MEDIA_URL = '/storage/'
MEDIA_ROOT = os.path.join(BASE_DIR, "storage")


# from config.rest_conf.JWT_auth import CustomTokenAuth

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'djongo_db',
        'HOST': '127.0.0.1',
        'PORT': 27017,
    }
}
CORS_ORIGIN_WHITELIST = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]
CORS_ORIGIN_ALLOW_ALL = False

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
        'config.rest_conf.auth.UserAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    ),
    'EXCEPTION_HANDLER': 'exceptions.exception_handlers.custom_exception_handler',
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'file_formatter': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'datefmt': '%d/%b/%Y %H:%M:%S',
            'style': '{',
        },
        'console_formatter': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'datefmt': '%d/%b/%Y %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/logfile',
            'formatter': 'file_formatter',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 10,
        },

        'console': {
            # 'level': 'WARNING',
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console_formatter',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'project_logger': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': secrets['SECRET_KEY'],
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'username',
    'USER_ID_CLAIM': 'username',

    'AUTH_TOKEN_CLASSES': (
        'accounts.api.tokens.tokens.CustomSlidingToken',
        # 'rest_framework_simplejwt.tokens.AccessToken',
        # 'rest_framework_simplejwt.tokens.SlidingToken'
    ),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
