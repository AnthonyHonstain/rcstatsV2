from django.shortcuts import render, get_object_or_404, redirect
from core.models import TrackName, SingleRaceDetails, SingleRaceResults, OfficialClassNames
from core.models import RacerId
from core.models import ClassEmailSubscription
from django.db.models import Count
from django.contrib.auth.decorators import login_required

import logging
logger = logging.getLogger('defaultlogger')


def index(request):
    logger.debug('metric=index')
    # Get the most recent TRCR race if it exists.
    # Just grab the first valid Track (assumed to be TRCR).
    trackname = TrackName.objects.all().first()
    # We want to most recent main event.
    singleracedetail = SingleRaceDetails.objects.filter(
        trackkey__exact=trackname.id,
        mainevent__isnull=False).order_by('-racedate').first()

    return render(request, 'index.html', {'trackname': trackname, 'singleracedetail': singleracedetail})


def single_race_details(request, single_race_detail_id):
    logger.debug('metric=singleracedetail single_race_detail_id=%s', single_race_detail_id)

    single_race_detail = get_object_or_404(SingleRaceDetails, pk=single_race_detail_id)
    race_results = SingleRaceResults.objects.filter(raceid=single_race_detail.id)\
        .order_by('finalpos').select_related('racerid')

    if single_race_detail.maineventparsed is None:
        single_race_detail.maineventparsed = ''
    trackname = single_race_detail.trackkey
    return render(request, 'single_race_detail.html',
                  {'trackname': trackname, 'singleracedetail': single_race_detail, 'raceresults': race_results})


def racer_list(request, track_id):
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

    return render(request, 'racer_list.html', {
        'trackname': trackname, 
        'track_race_count': track_race_count,
        'tracks_first_race':tracks_first_race, 
        'racerid_and_counts':racerid_and_counts})


def single_racer_race_list(request, track_id, racerid_id):
    trackname = get_object_or_404(TrackName, pk=track_id)
    racerid = get_object_or_404(RacerId, pk=racerid_id)

    races = SingleRaceResults.objects.filter(
        raceid__trackkey__exact=trackname.id,
        racerid__exact=racerid.id
        ).select_related('raceid').order_by('-raceid__racedate')

    return render(request, 'single_racer_race_list.html', {
        'trackname': trackname,
        'racerid': racerid,
        'races':races})


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
