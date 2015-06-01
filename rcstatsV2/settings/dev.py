import os
from rcstatsV2.settings.common import *


# ---------------------------------------------------------------------------
# SECRET CONFIGURATION
# A special file to contain login/secret info not stored in the public repo
from rcstatsV2.settings.settings_secret import *
# END SECRET CONFIGURATION
# ---------------------------------------------------------------------------

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# Show stack trace for warning - http://stackoverflow.com/questions/11557119/django-how-to-get-stack-traces-for-runtime-warnings
import warnings
from django.conf.global_settings import DEFAULT_FROM_EMAIL
warnings.filterwarnings(
    'error', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*',]

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rcstatsV2',
        'USER': DEV_DB_USER,
        'PASSWORD': DEV_DB_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

THIRD_PARTY_APPS += (
    'django_extensions',
)
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# Customize the admin template - https://docs.djangoproject.com/en/1.7/intro/tutorial02/
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'core', 'templates'),
                 os.path.join(BASE_DIR, 'accounts', 'templates'),
                 os.path.join(BASE_DIR, 'rcstatsV2', 'templates')]

# ---------------------------------------------------------------------------
# Email Back-End
# ---------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = 'smtp.mandrillapp.com'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = SECRET_EMAIL_HOST_PASSWORD

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = SECRET_EMAIL_HOST_USER

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 587

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

# Adding this so madril smtp has a 'from_email' field. https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEFAULT_FROM_EMAIL
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ENABLE_RACEUPDATE_EMAIL_KILLSWITCH = True
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Django Logging https://docs.python.org/3/howto/logging.html
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    # Formatters specify the layout of log records in the final output
    'formatters': {
        'verbose': {
            # Using a different format for dev, than prod
            'format': ('%(asctime)s [%(levelname)s] %(message)s [%(process)d] ' +
                       'filename=%(filename)s line=%(lineno)s ' +
                       'funcname=%(funcName)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': LOGGING_HANDLERS,
    'loggers': LOGGING_LOGGERS,
}
