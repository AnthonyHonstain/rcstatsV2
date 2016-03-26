
# Experimenting with outgoing email tasks
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from core.models import SingleRaceDetails
from core.models import SingleRaceResults
from core.models import ClassEmailSubscription
from core.models import OfficialClassNames

# Using Site to get the link for them the click through in the outgoing email
# http://stackoverflow.com/questions/892997/how-do-i-get-the-server-name-in-django-for-a-complete-url
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
import pytz

from django.conf import settings

import logging
log = logging.getLogger('defaultlogger')


def mail_all_users(single_race_details_id):
    single_race_details = SingleRaceDetails.objects.get(pk=single_race_details_id)

    log.debug('metric=EmailCheck racedata=%s', single_race_details.racedata)

    official_class = OfficialClassNames.objects.filter(raceclass=single_race_details.racedata)
    if (official_class == None):
        log.debug('metric=EmailCheckUnknownClass racedata=%s', single_race_details.racedata)
        return

    # Open question - do we want to check the User table AND the subscription table?
    #       Should I join them, or just trust the sub scription table?
    subscriptions = ClassEmailSubscription.objects.filter(
        raceclass=official_class, active=True).select_related('user')

    active_subscribers = []
    for sub in subscriptions:
        if (sub.user.email != None and sub.user.is_active == True):
            active_subscribers.append(sub)

    log.debug('metric=ActiveSubscribers active_subs=%d total_subs=%d',
        len(active_subscribers), len(subscriptions))

    for active_sub in active_subscribers:
        log.debug('metric=MailUser user_id=%d raceclass=%s subscription=%d',
            active_sub.user.id, active_sub.raceclass.raceclass, active_sub.id)
        _mail_single_race(active_sub.user, single_race_details)


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