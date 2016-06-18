# NOTE - we import absolute imports from the future, so that OUR celery.py module will not clash with the 'celery' library
# http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rcstatsV2.settings.dev')

from django.conf import settings

app = Celery('core')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
