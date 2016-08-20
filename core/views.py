from django.shortcuts import render, get_object_or_404, redirect
from core.models import TrackName, SingleRaceDetails, SingleRaceResults, OfficialClassNames
from core.models import RacerId
from core.models import ClassEmailSubscription
from core.sharedmodels.king_of_the_hill_summary import KoHSummary
from core.celery_manager import compute_koh_by_track_class

from django.views.decorators.cache import cache_page
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.conf import settings

import json

from django.utils import timezone
import datetime
from collections import defaultdict

import logging
logger = logging.getLogger('defaultlogger')


#@cache_page(60*15) # TODO - cache doesn't work with unit tests.
def index(request):
    logger.debug('metric=index')
    # Get the most recent TRCR race if it exists.
    # Just grab the first valid Track (assumed to be TRCR).
    trackname = TrackName.objects.all().first()
    # We want to most recent main event.
    singleracedetail = SingleRaceDetails.objects.filter(
        trackkey__exact=trackname.id,
        mainevent__isnull=False).order_by('-racedate').first()

    # We will use the most recent race to use for the KoH stats.
    koh_summarys = []
    if singleracedetail:
        official_class_name = OfficialClassNames.objects.filter(
            raceclass__exact=singleracedetail.racedata).first()
        if official_class_name:
            koh_summarys = get_koh_data(trackname, official_class_name, count=3, database_fallback=False)

    racer_count = RacerId.objects.all().count()

    return render(request, 'index.html', {
        'trackname': trackname,
        'singleracedetail': singleracedetail,
        'koh_summarys': koh_summarys,
        'racer_count': racer_count,
        })


def single_race_details(request, single_race_detail_id):
    '''
    Show the details for a single race.
    '''
    logger.debug('metric=singleracedetail single_race_detail_id=%s', single_race_detail_id)

    single_race_detail = get_object_or_404(SingleRaceDetails, pk=single_race_detail_id)
    race_results = SingleRaceResults.objects.filter(raceid=single_race_detail.id)\
        .order_by('finalpos').select_related('racerid')

    if single_race_detail.maineventparsed is None:
        single_race_detail.maineventparsed = ''
    trackname = single_race_detail.trackkey
    return render(request, 'single_race_detail.html',
                  {'trackname': trackname, 'singleracedetail': single_race_detail, 'raceresults': race_results})


@cache_page(60*60*6) # Doing an extra long cache on this since its expensive but relatively unchanged.
def racer_list(request, track_id):
    '''
    Lists all the racers for a given track, along with a count of races.
    '''
    logger.debug('metric=racer_list track_id=%s', track_id)
    trackname = get_object_or_404(TrackName, pk=track_id)

    track_race_count = SingleRaceResults.objects.filter(raceid__trackkey__exact=trackname.id)\
        .count()
    tracks_first_race = SingleRaceDetails.objects.filter(trackkey__exact=trackname.id)\
        .order_by('racedate')[1]

    racerid_and_counts = SingleRaceResults.objects.filter(raceid__trackkey__exact=trackname.id)\
      .select_related('racerid')\
      .values('racerid', 'racerid__racerpreferredname')\
      .annotate(racerid_count=Count('racerid'))\
      .order_by('-racerid_count')

    return render(request, 'racer_list/racer_list.html', {
        'trackname': trackname, 
        'track_race_count': track_race_count,
        'tracks_first_race':tracks_first_race, 
        'racerid_and_counts':racerid_and_counts})


def single_racer_race_list(request, track_id, racerid_id):
    '''
    For a track, list all of a single racer's results.
    '''
    logger.debug('metric=single_racer_race_list track_id=%s racerid_id=%s', track_id, racerid_id)

    trackname = get_object_or_404(TrackName, pk=track_id)
    racerid = get_object_or_404(RacerId, pk=racerid_id)

    races = SingleRaceResults.objects.filter(
        raceid__trackkey__exact=trackname.id,
        racerid__exact=racerid.id
        ).select_related('raceid').order_by('-raceid__racedate')

    return render(request, 'racer_list/single_racer_race_list.html', {
        'trackname': trackname,
        'racerid': racerid,
        'races':races})


class KoHSummaryDemo():
    def __init__(self, official_class_name, racerid, score):
        self.official_class_name = official_class_name
        self.racerid = racerid
        self.score = score
    def __repr__(self):
        return '{} {} {}'.format(
            self.official_class_name.raceclass,
            self.racerid.racerpreferredname,
            self.score)


@login_required()
def king_of_the_hill_summary(request, track_id):
    trackname = get_object_or_404(TrackName, pk=track_id)

    # We want a summary for the active classes.
    official_class_names = OfficialClassNames.objects.filter(active=True)

    two_weeks_ago = timezone.now() - datetime.timedelta(days=settings.KING_OF_THE_HILL_DAYS)

    # So for this track, and these classes, we want to show the top performers.
    koh_summary_by_class = {}

    for class_name in official_class_names:
        koh_summary_by_class[class_name] = get_koh_data(trackname, class_name, 3)

    #import pprint
    #pprint.pprint(race_summary)

    return render(request, 'king_of_the_hill/king_of_the_hill_summary.html', {
        'trackname': trackname,
        'start_time': two_weeks_ago,
        'koh_summary_by_class': koh_summary_by_class,
        })


@login_required()
def king_of_the_hill_class(request, track_id, official_class_name_id):
    trackname = get_object_or_404(TrackName, pk=track_id)
    official_class_name = get_object_or_404(OfficialClassNames, pk=official_class_name_id)

    two_weeks_ago = timezone.now() - datetime.timedelta(days=settings.KING_OF_THE_HILL_DAYS)

    koh_summarys = get_koh_data(trackname, official_class_name)

    return render(request, 'king_of_the_hill/king_of_the_hill_class.html', {
        'trackname': trackname,
        'official_class_name': official_class_name,
        'start_time': two_weeks_ago,
        'koh_summarys': koh_summarys,
        })


def get_koh_data(trackname, offical_class_name, count=None, database_fallback=True):
    '''
    I probably want to pull this to a special KoH module.

    Parameters
    ----------
    count : int
        Count of the first n results to turn (sorted by score)
    database_fallback : boolean
        If the cache hit fails, attempt to recompute the data from the database.
    '''
    koh_summarys = []

    result = cache.get('{}_{}'.format(trackname.trackname, offical_class_name.raceclass))

    if result:
        json_dicts = json.loads(result)
        for json_dict in json_dicts[0:count]:
            #print(json_dict)
            koh_summarys.append(KoHSummary(**json_dict))
            #koh_summarys.append(json_dict)

        return koh_summarys
    elif database_fallback:
        logger.error('metric=koh_cache_fail trackname=%d official_class_name=%d',
            trackname.id, offical_class_name.id)

        # TODO - need to robustify this and add more test coverage.
        complete_results = compute_koh_by_track_class(trackname.id, offical_class_name.id)
        return complete_results[0:count]
    else:
        logger.error('metric=koh_cache_fail trackname=%d official_class_name=%d',
            trackname.id, offical_class_name.id)
        return koh_summarys


from django import forms

class EmailRaceListForm(forms.Form):
    def __init__(self, *args, **kwargs):
        race_class_names_dict = kwargs.pop('class_names_dict')
        super(EmailRaceListForm, self).__init__(*args, **kwargs)
    #def __init__(self, race_class_names):
        for name,value in race_class_names_dict.items():
            self.fields[name] = forms.BooleanField(label=name, required=False, initial=value)


@login_required()
def race_emails(request):
    '''
    View and update all the classes a user is subscribed to.
    '''

    logger.debug('metric=race_emails user=%s method=%s', request.user, request.method);

    # get the users list
    class_names_data = OfficialClassNames.objects.filter(active=True)
    class_names_dict = {x.raceclass:False for x in class_names_data}
    class_names_lookup = {x.raceclass:x for x in class_names_data}

    current_subscriptions = ClassEmailSubscription.objects.filter(user=request.user)
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EmailRaceListForm(request.POST, class_names_dict=class_names_dict)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            existing_sub_dict = {}

            # Make the updates (races they are turning off or on)
            for existing_sub in current_subscriptions:
                class_name = existing_sub.raceclass.raceclass

                if (class_name in form.cleaned_data and
                    existing_sub.active != form.cleaned_data[class_name]):

                    existing_sub.active = form.cleaned_data[class_name]
                    existing_sub.save()
                existing_sub_dict[class_name] = None

            # Make the insert (races they are turning on)
            for key,value in form.cleaned_data.items():
                if value and key not in existing_sub_dict:
                    new_sub = ClassEmailSubscription(
                        raceclass=class_names_lookup[key],
                        user=request.user,
                        active=True)
                    new_sub.save()
                    logger.debug('metric=newSub raceclass=%d user=%d username=%s', 
                        new_sub.raceclass.id, new_sub.user.id, new_sub.user.username)

            # redirect to a new URL:
            return redirect('/')

    else:
        for current_sub in current_subscriptions:
            if current_sub.raceclass.raceclass in class_names_dict and current_sub.active:
                class_names_dict[current_sub.raceclass.raceclass] = True

        form = EmailRaceListForm(class_names_dict=class_names_dict)

    return render(request, 'race_emails.html', {'form': form});
