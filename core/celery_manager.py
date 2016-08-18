from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from core.models import SingleRaceDetails
from core.models import SingleRaceResults
from core.models import ClassEmailSubscription
from core.models import OfficialClassNames
from core.models import TrackName

from core.sharedmodels.king_of_the_hill_summary import KoHSummary

# Using Site to get the link for them the click through in the outgoing email
# http://stackoverflow.com/questions/892997/how-do-i-get-the-server-name-in-django-for-a-complete-url
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

import json
import pytz
from django.utils import timezone
import datetime
from collections import defaultdict

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


def _collect_koh_data(trackname_id, official_class_name, koh_timeframe):
    single_race_results = SingleRaceResults.objects.filter(
        raceid__trackkey__exact=trackname_id,
        raceid__racedata__exact=official_class_name.raceclass,
        raceid__racedate__gt=koh_timeframe)\
      .select_related('racerid').order_by('racerid')

    return single_race_results


def _compute_koh_scores(official_class_name, single_race_results):
    '''
    Calculate the KoH scores for a single class.
    '''
    computed_result = []
    starting_score = 21 # Remeber the racer's final standing is not zero based indexing.

    # We are going to start everyone off with a score of 0, then
    # just work our way through all the results.
    racer_temp_dict = defaultdict(int)
    for result in single_race_results:
        #print('for racer', result.racerid.id, ' finished:', result.finalpos, ' score:', starting_score - result.finalpos)
        racer_temp_dict[result.racerid] += starting_score - result.finalpos
        #print('    ', racer_temp_dict[result.racerid])

    # Now that we know all the racers and their scores, lets build
    # the final object.
    for key in racer_temp_dict.keys():
        koh_summary = KoHSummary(
            official_class_name.id,
            official_class_name.raceclass,
            key.id,
            key.racerpreferredname,
            racer_temp_dict[key]) 
        computed_result.append(koh_summary)

    computed_result.sort(key=lambda x: x.score, reverse=True)

    log.debug('metric=KoH_user_count class=%d count=%d', official_class_name.id, len(computed_result))
    return computed_result


def _cache_results(trackname, official_class_name, computed_scores):
    '''
    I am not sure if this should cache to redis or if I should just toss it in DB.
    In the past I have had availability issues with redis in heroku (still on free stack).
    '''
    def from_KoHSummary(obj):
        if isinstance(obj, KoHSummary):
            return obj.__dict__
        return obj

    cache.set(
        '{}_{}'.format(trackname.trackname, official_class_name.raceclass), 
        json.dumps(computed_scores, default=from_KoHSummary), 
        settings.KING_OF_THE_HILL_CACHE_TTL)


def _compute_king_of_the_hill(trackname, official_class_name, koh_timeframe):
    log.debug('metric=Compute_the_KoH  track=%d class=%d duration="%s"', trackname.id, official_class_name.id, koh_timeframe)
    single_race_results = _collect_koh_data(trackname.id, official_class_name, koh_timeframe)

    computed_scores = _compute_koh_scores(official_class_name, single_race_results)

    _cache_results(trackname, official_class_name, computed_scores)


def find_king_of_the_hill_classes():
    '''
    Look up all of the track and race classes being considered for King of the Hill
    '''
    tracknames = TrackName.objects.all()
    official_class_names = OfficialClassNames.objects.filter(active=True)

    track_and_class_list = []
    for trackname in tracknames:
        for official_class_name in official_class_names:
            track_and_class_list.append((trackname.id, official_class_name.id))
    return track_and_class_list


def compute_koh_by_track_class(trackname_id, official_class_name_id):
    '''
    Compute the KoH score for a specific track and class.
    '''
    trackname = TrackName.objects.get(pk=trackname_id)
    official_class_name = OfficialClassNames.objects.get(pk=official_class_name_id)

    # TODO - have I picked the right time here, now that I am computing it offline,
    # and in no way related to the user, I have to make a choice about tz.

    now = timezone.now()
    #utcnow = datetime.datetime.utcnow()
    #utcnow.replace(tzinfo=pytz.utc)
    koh_timeframe = now - datetime.timedelta(days=settings.KING_OF_THE_HILL_DAYS)

    _compute_king_of_the_hill(trackname, official_class_name, koh_timeframe)
