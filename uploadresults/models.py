from django.db import models
from django.contrib.auth.models import User
from core.models import SingleRaceDetails, Track, SupportedTrack


class EasyUploaderPrimaryRecord(models.Model):
    """
    Serves as the primary record in the easy uploader system, this tracks all the separate files
    that were uploaded (:model:`uploadresults.EasyUploadRecord`)and some basic information about the transaction.
    """
    user = models.ForeignKey(User)
    ip = models.GenericIPAddressField()
    filecount = models.IntegerField()
    filecountsucceed = models.IntegerField()
    uploadstart = models.DateTimeField('Datetime upload was started.')
    uploadfinish = models.DateTimeField('Datetime the upload was completed.', null=True)
    track = models.ForeignKey(Track, null=True)  # In the future I can see letting you set the track at the next page.

    def __str__(self):
        return '<EasyUploadPrimaryRecord id:' + str(self.id) + "|" +\
            str(self.user) + "|" +\
            str(self.track) + '>'


class EasyUploadRecord(models.Model):
    uploadrecord = models.ForeignKey(EasyUploaderPrimaryRecord)
    origfilename = models.CharField(max_length=200)
    filename = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User)
    ip = models.GenericIPAddressField()
    filesize = models.BigIntegerField()
    filemd5 = models.CharField(max_length=200, null=True)
    uploadstart = models.DateTimeField('Date the file was uploaded.', null=True)
    uploadfinish = models.DateTimeField('Date the file was finished uploaded and processed', null=True)
    track = models.ForeignKey(Track, null=True)
    processed = models.BooleanField('We processed some or all of the file (still possible there was an error)', default=False)
    errorenum = models.IntegerField(null=True)

    def __str__(self):
        return '<EasyUploadRecord id:' + str(self.id) + "|" +\
            str(self.filename) + "|" +\
            str(self.uploadstart) + "|" +\
            str(self.processed) + "|" +\
            str(self.errorenum) + '>'


class SingleRaceData(models.Model):
    """
    I think in the future we could probably condense this into the EasyUploadRecord
    """
    primaryrecord = models.ForeignKey(EasyUploaderPrimaryRecord)
    uploadrecord = models.ForeignKey(EasyUploadRecord)
    owner = models.ForeignKey('auth.User')
    ip = models.GenericIPAddressField()
    track = models.ForeignKey(Track, null=False)
    filename = models.CharField(max_length=200, null=False)
    data = models.TextField('The contents of the race file.', null=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '<SingleRaceData id:' + str(self.id) + '>'


class EasyUploadedRaces(models.Model):
    """
    Stores the relationship between the original file that was uploaded :model:`uploadresults.EasyUploadRecord`
    and the race record we store in the db :model:`rcdata.SingleRaceDetails`
    """
    upload = models.ForeignKey(EasyUploadRecord)
    racedetails = models.ForeignKey(SingleRaceDetails)
