from django.shortcuts import render, get_object_or_404
from core.models import TrackName, SingleRaceDetails


def index(request):
    # Get the most recent TRCR race if it exists.
    # Just grab the first valid Track (assumed to be TRCR).
    trackname = TrackName.objects.all().first()
    # We want to most recent main event.
    singleracedetail = SingleRaceDetails.objects.filter(
        trackkey__exact=trackname.id,
        maineventparsed__isnull=False).order_by('-racedate').first()

    return render(request, 'index.html', {'trackname': trackname, 'singleracedetail': singleracedetail})


def single_race_details(request, single_race_detail_id):
    single_race_detail = get_object_or_404(SingleRaceDetails, pk=single_race_detail_id)
    trackname = single_race_detail.trackkey
    return render(request, 'single_race_detail.html',
                  {'trackname': trackname, 'singleracedetail': single_race_detail})
