from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics

from core.models import TrackName, SingleRaceDetails
from raceAPI.serializers import TrackNameSerializer, SingleRaceDetailsSerializer


class TrackNameList(viewsets.ReadOnlyModelViewSet):
    queryset = TrackName.objects.all()
    serializer_class = TrackNameSerializer


class SingleRaceDetailsList(viewsets.ReadOnlyModelViewSet):
    queryset = SingleRaceDetails.objects.all()
    serializer_class = SingleRaceDetailsSerializer

    def get_queryset(self):
        trackkey = self.kwargs['trackname']
        return SingleRaceDetails.objects.filter(trackkey__exact=trackkey)
