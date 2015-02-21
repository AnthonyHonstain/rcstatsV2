from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework.permissions import AllowAny

from core.models import TrackName, SingleRaceDetails
from raceAPI.serializers import TrackNameSerializer, SingleRaceDetailsSerializer, SingleRaceDetailsSlimSerializer


class TrackNameList(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = TrackName.objects.all()
    serializer_class = TrackNameSerializer


class SingleRaceDetailsList(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = SingleRaceDetails.objects.all()
    serializer_class = SingleRaceDetailsSerializer

    def get_queryset(self):
        trackkey = self.kwargs['trackname']
        return SingleRaceDetails.objects.filter(trackkey__exact=trackkey)


class SingleRaceDetailsSlimList(viewsets.ReadOnlyModelViewSet):
    '''
    Streamlined/basic version of the SingleRaceDetails with no additional objects.
    '''
    # TODO - I am going to need to address this here and on front end.
    # http://www.django-rest-framework.org/api-guide/pagination/
    paginate_by = None
    permission_classes = (AllowAny,)
    queryset = SingleRaceDetails.objects.all()
    serializer_class = SingleRaceDetailsSlimSerializer
