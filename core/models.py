from django.db import models

from django.contrib.auth.models import User


class TrackName(models.Model):
    '''
    Holds the raw track identifier for the race data being
    uploaded.
    '''
    trackname = models.CharField(max_length=200)

    def __str__(self):
        return str(self.trackname)


class SupportedTrackName(models.Model):
    '''
    This model will contain the additional meta data for race tracks so that
    they can presented in the trackdata section. These is meant to encompass
    all the additional data we want to present to the user about the track
    (especially information that is not stored in race results).
    '''
    trackkey = models.ForeignKey(TrackName)


# A single racer, their name (probably not going be be unique by default)
class Racer(models.Model):
    racerpreferredname = models.CharField(max_length=200)

    def __str__(self):
        return str(self.racerpreferredname)


class SingleRaceDetails(models.Model):
    trackkey = models.ForeignKey(TrackName)
    racedata = models.CharField(max_length=200)
    # roundnumber and racenumber do not exist in older formats
    roundnumber = models.IntegerField(null=True)
    racenumber = models.IntegerField(null=True)
    racedate = models.DateTimeField('Date of the race', db_index=True)
    uploaddate = models.DateTimeField('Date the race was uploaded')
    racelength = models.IntegerField('Number of minutes for the race')
    winninglapcount = models.IntegerField('Number of laps that won the race')
    # Need two separate columns, one for the main, and another for its main-round number
    #     The main-round number A3 may have no correlation with the race round number.
    # Example: A main -> mainevent=1 , C main -> mainevent=3
    #     Then a B1 main -> mainevent=2 maineventroundnum=1
    mainevent = models.SmallIntegerField(null=True)
    maineventroundnum = models.SmallIntegerField(null=True)
    maineventparsed = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id) + " | " +\
            str(self.trackkey) + " | " +\
            str(self.racedata) + " | " +\
            str(self.racedate)


class SingleRaceResults(models.Model):
    raceid = models.ForeignKey(SingleRaceDetails)
    racer = models.ForeignKey(Racer)
    carnum = models.SmallIntegerField('Car number for this race')
    lapcount = models.SmallIntegerField('Number of laps they completed')
    racetime = models.TimeField(null=True)
    fastlap = models.DecimalField(decimal_places=3, max_digits=6, null=True)
    behind = models.DecimalField(decimal_places=3, max_digits=6, null=True)
    finalpos = models.SmallIntegerField('Final race position')


class LapTimes(models.Model):
    raceid = models.ForeignKey(SingleRaceDetails)
    racer = models.ForeignKey(Racer)
    racelap = models.SmallIntegerField()
    raceposition = models.SmallIntegerField(null=True)
    racelaptime = models.DecimalField(decimal_places=3, max_digits=6, null=True)

    def __str__(self):
        return str(self.raceid.id) + " | " +\
            str(self.racer) + " | " +\
            str(self.racelap) + " | " +\
            str(self.raceposition) + " | " +\
            str(self.racelaptime)


class OfficialClassNames(models.Model):
    raceclass = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.raceclass


class AliasClassNames(models.Model):
    raceclass = models.CharField(max_length=200)
    officialclass = models.ForeignKey(OfficialClassNames)


class ClassEmailSubscription(models.Model):
    raceclass = models.ForeignKey(OfficialClassNames)
    user = models.ForeignKey(User)
    active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)