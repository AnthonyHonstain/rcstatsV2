from core.models import TrackName, SingleRaceDetails, SingleRaceResults, LapTimes, Racer
from rest_framework import serializers, models


class TrackNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TrackName
        fields = ('id', 'trackname')


class SingleRaceResultsSerializer(serializers.HyperlinkedModelSerializer):
    # Instead of using the PK, we are going to retrieve their actual name.
    racer = serializers.ReadOnlyField(source='racer.racerpreferredname')
    racetime = serializers.TimeField(format="%M:%S.%f")

    class Meta:
        model = SingleRaceResults
        fields = (
            'id',
            'racer',
            'carnum',
            'lapcount',
            'racetime',
            'fastlap',
            'finalpos',
        )


class SingleRaceDetailsByTrackSerializer(serializers.HyperlinkedModelSerializer):
    # We will include the entire race result object by specifying the SingleRaceResultsSerializer
    raceresults = SingleRaceResultsSerializer(source='singleraceresults_set', many=True)
    # Specifying the PK related field here overrides the hyperlink functionality.
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


class SingleRaceDetailsSlimSerializer(serializers.HyperlinkedModelSerializer):
    # Specifying the PK related field here overrides the hyperlink functionality.
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
        )


class RacerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Racer


class LapTimesSerializer(serializers.HyperlinkedModelSerializer):
    # We are going to use a PK here just for validation, since they used the
    # SingleRaceDetails pk to find these laps in the first place.
    raceid = serializers.PrimaryKeyRelatedField(queryset=SingleRaceDetails.objects.all())

    racer = serializers.PrimaryKeyRelatedField(queryset=Racer.objects.all())

    class Meta:
        model = LapTimes
        fields = (
            'id',
            'raceid',
            'racer',
            'racelap',
            'raceposition',
            'racelaptime',
        )


class SingleRaceDetailsSerializer(serializers.HyperlinkedModelSerializer):
    # Specifying the PK related field here overrides the hyperlink functionality.
    #trackkey = serializers.PrimaryKeyRelatedField(queryset=TrackName.objects.all())

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
        )
