
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

from django.conf import settings

import logging
log = logging.getLogger('defaultlogger')


def mail_all_users(single_race_details_id):
    # TODO - filter down to just OPT IN users
    # Get all the users
    single_race_details = SingleRaceDetails.objects.get(pk=single_race_details_id)

    log.debug('metric=EmailCheck racedata=%s', single_race_details.racedata)
    if single_race_details.racedata == 'Mod Buggy':
        log.info('metric=Email single_race_details=%s', single_race_details.id)
    else:
        # TODO - improve this, going to just jump out (I am just starting the rewrite)
        return

    users = User.objects.filter(email__isnull=False, is_active=True).exclude(email__exact='')

    print('Found {0} many users to email.'.format(len(users)))
    for user in users:
        # TODO - replace with real logging
        print('Mailing user {0} {1}'.format(user.id, user.username))
        _mail_single_race(user, single_race_details)


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
    if settings.ENABLE_OUTGOING_EMAIL:
        msg.send(fail_silently=False)
    else:
        print('='*20)
        print('Outgoing email disabled')
        print('='*20)
        print(context)
        print('='*20)
    return