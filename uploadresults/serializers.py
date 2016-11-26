from uploadresults import models
from core.models import Track
from rest_framework import serializers


class EasyUploaderPrimaryRecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.EasyUploaderPrimaryRecord
        fields = ('id', 'ip', 'filecount', 'filecountsucceed', 'uploadstart', 'uploadfinish')


class EasyUploadRecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.EasyUploadRecord
        fields = ('id', 'uploadrecord', 'origfilename', 'filename', 'processed')


from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class TrackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Track
        fields = ('id', 'name')


class SingleRaceUploadSerializer(serializers.HyperlinkedModelSerializer):
    '''
    To provide backwards compatibility for the old uploader apps, I am going to
    continue to expose track as "trackname".
        http://stackoverflow.com/questions/22958058/how-to-change-field-name-in-django-rest-framework
    '''
    id = serializers.IntegerField(read_only=True)
    primaryrecord = serializers.ReadOnlyField(source='primaryrecord.id')
    uploadrecord = serializers.ReadOnlyField(source='uploadrecord.id')
    owner = serializers.ReadOnlyField(source='owner.username')
    ip = serializers.ReadOnlyField()
    # NOTE - we are mapping "trackname" to the model's "track" column.
    trackname = serializers.PrimaryKeyRelatedField(source='track', queryset=Track.objects.all())
    filename = serializers.CharField(allow_blank=False)
    data = serializers.CharField(allow_blank=False, min_length=10)

    class Meta:
        model = models.SingleRaceData
        fields = ('id', 'primaryrecord', 'uploadrecord', 'owner', 'ip', 'trackname', 'filename', 'data')
