"""
Django settings for project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import datetime
import socket
from django.conf import global_settings
from os.path import join, dirname

from dotenv import load_dotenv, find_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Load the .env file
load_dotenv(find_dotenv())

DATA_DIR = os.path.join(BASE_DIR, '..', '..', 'data')
CERTS_DIR = os.path.join(BASE_DIR, '..', '..', 'certs')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ['DEBUG'] == '1'

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')

HOSTNAME = socket.gethostname()

# Application definition

INTERNAL_IPS = ('127.0.0.1',)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'rest_framework',

    'sema2',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'debug_toolbar',

    'bootstrap3',
    'template_email',
    'boosted_uplink',
    'push_notifications',
    # 'opbeat.contrib.django',
)

MIDDLEWARE_CLASSES = (
    # 'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'sema2.exception_middleware.ProcessExceptionMiddleware',
)

# OPBEAT = {
#     'ORGANIZATION_ID': os.environ['OPBEAT_ORGANISATION_ID'],
#     'APP_ID': os.environ['OPBEAT_APP_ID'],
#     'SECRET_TOKEN': os.environ['OPBEAT_SECRET_TOKEN'],
# }

LOGIN_REDIRECT_URL = '/'

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'

JWT_SECRET = os.environ['JWT_SECRET']

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 57600}

CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_IMPORTS = ('sema2.tasks', )
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}

global_settings.AUTHENTICATION_BACKENDS += (
    "allauth.account.auth_backends.AuthenticationBackend",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",

    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(weeks=12),
    'JWT_ALLOW_REFRESH': True
}

EMAIL_BACKEND = 'django_mailgun.MailgunBackend'

MAILGUN_ACCESS_KEY = os.environ['MAILGUN_ACCESS_KEY']
MAILGUN_SERVER_NAME = os.environ['MAILGUN_SERVER_NAME']

SITE_ID = 1

if DEBUG:
    LOG_FILEPATH = '/dev/null'
    TASK_LOG_FILEPATH = '/dev/null'
else:
    LOG_FILEPATH = os.path.join(BASE_DIR, '..', '..', 'logs', 'app.log')
    TASK_LOG_FILEPATH = os.path.join(BASE_DIR, '..', '..', 'logs', 'task.log')

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, '..', '..', 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', 'media')
MEDIA_URL = '/media/'

# AFTER DYNAMIC SETTINGS
BROKER_URL = os.environ['CELERY_BROKER_URL']  # 'redis://localhost:6400/0'
CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_URL']  # 'redis://localhost:6400/0'

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB_NAME'],
        'USER': os.environ['POSTGRES_DB_USER'],
        'PASSWORD': os.environ['POSTGRES_DB_PASSWORD'],
        'HOST': os.environ['POSTGRES_DB_HOST'],
        'PORT': '',
    }
}

# CERTS
IOS_PUSH_CERT_NAME = 'production_push_cert.pem'
DEFAULT_IOS_APP_ID = os.environ['IOS_APP_ID']

PUSH_NOTIFICATIONS_SETTINGS = {
        "GCM_API_KEY": os.environ['NOTIFICATIONS_GCM_API_KEY'],
        "APNS_CERTIFICATE": os.path.join(CERTS_DIR, IOS_PUSH_CERT_NAME), # Still put this in but we use the mapping dict below
}

# Support for mapping multiple app ids to push notifications
# Uses the default app id and cert name
PUSH_NOTIFICATION_APP_ID_TO_CERT_MAPPING = {
    DEFAULT_IOS_APP_ID: os.path.join(CERTS_DIR, IOS_PUSH_CERT_NAME),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        }
    },

    'handlers': {

        'logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_FILEPATH,
            'formatter': 'standard',
        },

        'tasklogfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': TASK_LOG_FILEPATH,
            'formatter': 'standard',
        },

        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },

        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },

    'loggers': {

        'django': {
            'handlers': [],
            'propagate': True,
            'level': 'DEBUG',
        },

        'django.request': {
            'handlers': ['mail_admins'],
            'propagate': True,
            'level': 'ERROR',
        },

        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },

        'sema2': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'sema2.tasks': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

if not DEBUG:
    if not os.path.exists(LOG_FILEPATH):
        with open(LOG_FILEPATH, 'a'):
            os.utime(LOG_FILEPATH, None)

    if not os.path.exists(TASK_LOG_FILEPATH):
        with open(TASK_LOG_FILEPATH, 'a'):
            os.utime(TASK_LOG_FILEPATH, None)
        
if DEBUG:
    LOGGING['loggers']['sema2.tasks']['handlers'].insert(0, 'console')
    LOGGING['loggers']['sema2']['handlers'].insert(0, 'console')
    LOGGING['loggers']['django']['handlers'].insert(0, 'console')
else:
    LOGGING['loggers']['sema2.tasks']['handlers'].insert(0, 'tasklogfile')
    LOGGING['loggers']['sema2']['handlers'].insert(0, 'logfile')
    LOGGING['loggers']['django']['handlers'].insert(0, 'logfile')

CELERYBEAT_SCHEDULE = {
    'update-compliance': {
        'task': 'tasks.update_compliance',
        'schedule': datetime.timedelta(minutes=30),
    },
}

CELERY_TIMEZONE = 'UTC'
