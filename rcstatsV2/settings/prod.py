from rcstatsV2.settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# ---------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Not going to use the default key - we expect this to come from heroku side,
# we are going to use a blank since there should be no key in the repo
#     http://stackoverflow.com/questions/21683846/unable-to-access-heroku-config-vars-from-django-settings-py
#     https://devcenter.heroku.com/articles/buildpack-api
SECRET_KEY = os.environ.get('SECRET_KEY')
