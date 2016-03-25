# NOTE - we import absolute imports from the future, so that OUR celery.py module will not clash with the 'celery' library
# http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
from __future__ import absolute_import

import os

from celery import Celery

from core.celery_manager import mail_all_users

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rcstatsV2.settings.dev')

app = Celery('proj')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

import logging
log = logging.getLogger('defaultlogger')

import sys  # TODO - Remove after testing
import random

'''
The general architecture here is that the tasks defined and managed here, but all the
heavy lifting is implemented and tested in another module.

So we can work and test the outgoing email logic without having to think very much 
about the celery job and the external dependencies that make the whole system dance.
'''

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    sys.stdout.flush()  # TODO - Remove after testing
    return random.randint(0, 100)


@app.task(bind=True)
def mail_single_race(self, single_race_details_id):
    print('Request: {0!r} {1}'.format(self.request.task, single_race_details_id))

    mail_all_users(single_race_details_id)
    sys.stdout.flush()  # TODO - Remove after testing
    return
