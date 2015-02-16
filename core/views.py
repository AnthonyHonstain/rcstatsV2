from django.shortcuts import render
from core.models import TrackName, SingleRaceDetails


def index(request):
    # Get the most recent TRCR race if it exists.
    # Just grab the first valid Track (assumed to be TRCR).
    trackname = TrackName.objects.all().first()
    # We want to most recent main event.
    singleracedetail = SingleRaceDetails.objects.filter(
        trackkey__exact=trackname.id,
        maineventparsed__isnull=False).order_by('-id').first()

    return render(request, 'index.html', {'trackname': trackname, 'singleracedetail': singleracedetail})
