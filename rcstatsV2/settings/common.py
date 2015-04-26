"""
Django settings for rcstatsV2 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from __future__ import absolute_import
# ^^^ The above is required if you want to import from the celery
# library.  If you don't have this then `from celery.schedules import`
# becomes `proj.celery.schedules` in Python 2.x since it allows
# for relative imports by default.


# SECURITY WARNING: keep the secret key used in production secret!
# See settings_secret.py_TEMPLATE

import os
redis_url = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379/0')

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
# http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

# Celery settings
BROKER_URL = redis_url  # 'amqp://guest:guest@localhost//'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# You need the CELERYBEAT_SCHEDULER if you want to configures period tasks through the admin page.
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
)

THIRD_PARTY_APPS = (
    # django-userena - account management app
    'userena',
    'guardian',
    'easy_thumbnails',
    'rest_framework',
    'djcelery',
    'kombu.transport.django.KombuAppConfig',
)

LOCAL_APPS = (
    'core',
    'accounts',
    'uploadresults',
    'raceAPI',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rcstatsV2.urls'

WSGI_APPLICATION = 'rcstatsV2.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_NAME = 'RC-STATS'

# For the sites framework https://docs.djangoproject.com/en/1.7/ref/contrib/sites/#enabling-the-sites-framework
SITE_ID = 1

# ---------------------------------------------------------------------------
# Userena Registration
# ---------------------------------------------------------------------------
# http://docs.django-userena.org/en/latest/installation.html
# http://docs.django-userena.org/en/latest/installation.html#id2
ANONYMOUS_USER_ID = -1
AUTH_PROFILE_MODULE = 'accounts.UserProfile'

LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Django Rest Framework - http://www.django-rest-framework.org/tutorial/quickstart/
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGINATE_BY': 10
}

# ---------------------------------------------------------------------------
# Django Logging https://docs.python.org/3/howto/logging.html
# ---------------------------------------------------------------------------
# Handlers send the log records to the appropriate destination
LOGGING_HANDLERS = {
    'null': {
        'level': 'DEBUG',
        'class': 'logging.NullHandler',
    },
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose'
    }
}
# Expose the interface for application code to directly interact with
LOGGING_LOGGERS = {
    # A good default logger for heroku
    'defaultlogger': {
        'handlers': ['console'],
        'level': 'DEBUG',
    }
}
