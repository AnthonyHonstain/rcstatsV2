from uploadresults import models
from core.models import TrackName
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


class TrackNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TrackName
        fields = ('id', 'trackname')


class SingleRaceUploadSerializer(serializers.HyperlinkedModelSerializer):
    pk = serializers.IntegerField(read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    ip = serializers.ReadOnlyField()
    trackname = serializers.PrimaryKeyRelatedField(queryset=TrackName.objects.all())

    class Meta:
        model = models.SingleRaceData
        fields = ('pk', 'owner', 'ip', 'trackname', 'filename', 'data')
