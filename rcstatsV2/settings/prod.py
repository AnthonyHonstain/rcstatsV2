import os
from rcstatsV2.settings.common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get('DJANGO_DEBUG', None) == '1' else False

TEMPLATE_DEBUG = True if os.environ.get('DJANGO_DEBUG', None) == '1' else False

# ---------------------------------------------------------------------------
# Following the heroku instructions - https://devcenter.heroku.com/articles/getting-started-with-django

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {'default': dj_database_url.config()}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# ---------------------------------------------------------------------------

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

ADMINS = [os.environ.get('ADMINS', 'your_email@example.com'), ]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Not going to use the default key - we expect this to come from heroku side,
# we are going to use a blank since there should be no key in the repo
#     http://stackoverflow.com/questions/21683846/unable-to-access-heroku-config-vars-from-django-settings-py
#     https://devcenter.heroku.com/articles/buildpack-api
SECRET_KEY = os.environ.get('SECRET_KEY')

# Customize the admin template - https://docs.djangoproject.com/en/1.7/intro/tutorial02/
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'rcstatsV2', 'templates')]

# ---------------------------------------------------------------------------
# Email Back-End
# ---------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your_email@example.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

# Adding this so madril smtp has a 'from_email' field. https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEFAULT_FROM_EMAIL
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
# ---------------------------------------------------------------------------
