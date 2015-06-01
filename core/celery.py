# NOTE - we import absolute imports from the future, so that OUR celery.py module will not clash with the 'celery' library
# http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# Experimenting with outgoing email tasks
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from core.models import SingleRaceDetails
from core.models import SingleRaceResults
# Using Site to get the link for them the click through.
# http://stackoverflow.com/questions/892997/how-do-i-get-the-server-name-in-django-for-a-complete-url
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
import pytz

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rcstatsV2.settings.dev')

app = Celery('proj')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

import sys  # TODO - Remove after testing
import random


def _mail_single_race(user, single_race_detail):
    '''
    Send a single race result to a user in the system
    '''
    los_angels_tz = pytz.timezone("America/Los_Angeles")
    racetime = los_angels_tz.normalize(single_race_detail.racedate)

    subject = '{0} Rnd:{1} {2}'.format(single_race_detail.racedata,
                                       single_race_detail.roundnumber,
                                       racetime.strftime('%b %d'))
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    plaintext = get_template('email.txt')
    htmly = get_template('email.html')

    single_race_results = SingleRaceResults.objects.filter(raceid=single_race_detail).order_by('finalpos')

    context = Context({
        'host': Site.objects.get_current(),
        'username': user.username,
        'single_race_detail': single_race_detail,
        'single_race_results': single_race_results,
    })

    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    #print('Subject ' + subject)
    #print(html_content)
    #print(text_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")

    # TODO - clean this up so its more clear what is going on
    # We want to be able to toggle this functionality from the configs
    if settings.ENABLE_RACEUPDATE_EMAIL_KILLSWITCH:
        msg.send(fail_silently=False)
    return


def _mail_all_users(single_race_details_id):
    # TODO - filter down to just OPT IN users
    # Get all the users
    single_race_details = SingleRaceDetails.objects.get(pk=single_race_details_id)
    users = User.objects.filter(email__isnull=False, is_active=True).exclude(email__exact='')

    for user in users:
        # TODO - replace with real logging
        print('Mailing user {0} {1}'.format(user.id, user.username))
        _mail_single_race(user, single_race_details)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    sys.stdout.flush()  # TODO - Remove after testing
    return random.randint(0, 100)


@app.task(bind=True)
def mail_single_race(self, sinlge_race_details_id):
    print('Request: {0!r}'.format(self.request))

    _mail_all_users(sinlge_race_details_id)
    sys.stdout.flush()  # TODO - Remove after testing
    return
