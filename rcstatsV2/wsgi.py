"""
WSGI config for rcstatsV2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rcstatsV2.settings.dev")

from django.core.wsgi import get_wsgi_application
from dj_static import Cling

# Following the instructions on heroku - https://devcenter.heroku.com/articles/getting-started-with-django
# application = get_wsgi_application()
application = Cling(get_wsgi_application())
