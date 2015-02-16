from core.models import TrackName, SingleRaceDetails, SingleRaceResults
from rest_framework import serializers, models


class TrackNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TrackName
        fields = ('id', 'trackname')


class SingleRaceResultsSerializer(serializers.HyperlinkedModelSerializer):
    racerid = serializers.ReadOnlyField(source='racerid.racerpreferredname')
    racetime = serializers.TimeField(format="%M:%S.%f")

    class Meta:
        model = SingleRaceResults
        fields = (
            'id',
            'racerid',
            'carnum',
            'lapcount',
            'racetime',
            'fastlap',
            'finalpos',
        )


class SingleRaceDetailsSerializer(serializers.HyperlinkedModelSerializer):
    raceresults = SingleRaceResultsSerializer(source='singleraceresults_set', many=True)
    trackkey = serializers.PrimaryKeyRelatedField(queryset=TrackName.objects.all())

    class Meta:
        model = SingleRaceDetails
        fields = (
            'id',
            'trackkey',
            'racedata',
            'roundnumber',
            'racenumber',
            'racedate',
            'racelength',
            'maineventparsed',
            'raceresults'
        )



