from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework.permissions import AllowAny

from core.models import TrackName, SingleRaceDetails, LapTimes, Racer
from raceAPI.serializers import TrackNameSerializer, SingleRaceDetailsSerializer, SingleRaceDetailsSlimSerializer
from raceAPI.serializers import LapTimesSerializer, RacerSerializer, SingleRaceDetailsByTrackSerializer


# ##################################################################################
# Basic Views to support the serializers.HyperlinkedModelSerializer functionality.
# ##################################################################################
'''
Be sure to review:
    * ViewSet - http://www.django-rest-framework.org/api-guide/viewsets/#readonlymodelviewset
    * Hyperlinked Relationships - http://www.django-rest-framework.org/tutorial/5-relationships-and-hyperlinked-apis/
These are all tightly dependent on the lookup names generated in the urls.py routing and
the relationships defined in the serializer.
'''


class TrackNameList(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = TrackName.objects.all()
    serializer_class = TrackNameSerializer


class RacerList(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # We are only implementing GET functionality, we don't want to LIST
    # every single racer at once.
    permission_classes = (AllowAny,)
    queryset = Racer.objects.all()
    serializer_class = RacerSerializer


class SingleRaceDetailsList(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # We are only implementing GET functionality, we don't want to LIST ever race.
    permission_classes = (AllowAny,)
    queryset = SingleRaceDetails.objects.all()
    serializer_class = SingleRaceDetailsSerializer


# ##################################################################################
# Special end points to support client behavior
# ##################################################################################
class SingleRaceDetailsByTrackList(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = SingleRaceDetails.objects.all()
    serializer_class = SingleRaceDetailsByTrackSerializer

    def get_queryset(self):
        trackkey = self.kwargs['trackname']
        return SingleRaceDetails.objects.filter(trackkey__exact=trackkey)


class SingleRaceDetailsSlimList(viewsets.ReadOnlyModelViewSet):
    '''
    Streamlined/basic version of the SingleRaceDetailsByTrack with no additional objects.
    '''
    # Using limit offset pagination now
    # http://www.django-rest-framework.org/api-guide/pagination/
    max_limit = 10

    permission_classes = (AllowAny,)
    queryset = SingleRaceDetails.objects.all()
    serializer_class = SingleRaceDetailsSlimSerializer

    def get_queryset(self):
        trackkey = self.kwargs['trackname']
        # Note - this doesn't have good test coverage, I just hacked it together to make TRCR in PT timezone
        # return nice results, the race computer does insane things with time so I am trying to cobble them together.
        # postgres - http://www.postgresql.org/docs/9.1/static/datatype-datetime.html#DATATYPE-TIMEZONES
        #   http://www.postgresql.org/docs/9.1/static/functions-datetime.html
        # orm - http://stackoverflow.com/questions/4236226/ordering-a-django-queryset-by-a-datetimes-month-day
        return SingleRaceDetails.objects.filter(trackkey__exact=trackkey)\
            .extra(select={'raceday':'date_trunc(\'day\', racedate AT TIME ZONE \'america/los_angeles\')'})\
            .order_by('-raceday', '-roundnumber', '-racenumber')


class LapTimesList(viewsets.ReadOnlyModelViewSet):
    '''
    Display the lap times for a track+singleracedetails, this is mainly for the flot graph
    '''
    paginate_by = None
    page_size = 10
    permission_classes = (AllowAny,)
    queryset = LapTimes.objects.all()
    serializer_class = LapTimesSerializer

    def get_queryset(self):
        single_race_details = self.kwargs['singleracedetails']
        return LapTimes.objects.filter(raceid__exact=single_race_details).order_by('racer', 'racelap')




