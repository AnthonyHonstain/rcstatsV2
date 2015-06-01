from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework.permissions import AllowAny

from core.models import TrackName, SingleRaceDetails, LapTimes, RacerId
from raceAPI.serializers import TrackNameSerializer, SingleRaceDetailsSerializer, SingleRaceDetailsSlimSerializer
from raceAPI.serializers import LapTimesSerializer, RacerIdSerializer, SingleRaceDetailsByTrackSerializer


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


class RacerIdList(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # We are only implementing GET functionality, we don't want to LIST
    # every single racer at once.
    permission_classes = (AllowAny,)
    queryset = RacerId.objects.all()
    serializer_class = RacerIdSerializer


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
    # TODO - I am going to need to address this here and on front end.
    # http://www.django-rest-framework.org/api-guide/pagination/
    paginate_by = None
    permission_classes = (AllowAny,)
    queryset = SingleRaceDetails.objects.all()
    serializer_class = SingleRaceDetailsSlimSerializer

    def get_queryset(self):
        trackkey = self.kwargs['trackname']
        return SingleRaceDetails.objects.filter(trackkey__exact=trackkey).order_by('-racedate')


class LapTimesList(viewsets.ReadOnlyModelViewSet):
    '''
    Display the lap times for a track+singleracedetails, this is mainly for the flot graph
    '''
    paginate_by = None
    permission_classes = (AllowAny,)
    queryset = LapTimes.objects.all()
    serializer_class = LapTimesSerializer

    def get_queryset(self):
        single_race_details = self.kwargs['singleracedetails']
        return LapTimes.objects.filter(raceid__exact=single_race_details).order_by('racerid', 'racelap')




