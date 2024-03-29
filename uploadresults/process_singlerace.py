from core.database_cleanup import collapse_alias_classnames, collapse_racer_names

from core.models import (
    TrackName,
    LapTimes,
    SingleRaceResults,
    SingleRaceDetails,
    Racer)

import datetime
import pytz
from django.utils import timezone

import logging
log = logging.getLogger('defaultlogger')

# TODO - this is a short term fix, when I create the auto uploader it should
# specific the timezone its being uploaded from.
TIMEZONE_HACK = pytz.timezone('America/Los_Angeles')


def create_single_race_details(single_race):
    '''
    Insert the information in the single_race object into the DB.

    Conditions - The trackname is already in the db.

    Parameters
    ----------
    single_race : SingleRace object
       SingleRace contains the raw data parsed from the original race file, this is
       just a generalized object for race data prior to putting it in the database

    Returns
    ----------
    SingleRaceDetails
        The newly created SingleRaceDetails record.
    '''

    # ====================================================
    # Trackname
    # ====================================================
    # Track - We assume it has already been validated that this is a known track.
    #    NOTE - we do not want to be creating new tracks in this code, if the track
    #    is new it probably means they are not uploading appropriately.
    track_obj = TrackName.objects.get(trackname=single_race.trackName)

    # ====================================================
    # Get additional meta info for creating the race details
    # ====================================================
    # Find race length
    racelength = _calculate_race_length(single_race.raceHeaderData)

    # Find Winning lap count
    maxlaps = 0
    for racer in single_race.raceHeaderData:
        if (racer['Laps'] > maxlaps):
            maxlaps = racer['Laps']

    # Parse this '10:32:24 PM  8/13/2011'
    # TODO - let the uploader specific the current timezone.
    unaware = datetime.datetime.strptime(single_race.date, "%I:%M:%S %p %m/%d/%Y")
    formatedtime = unaware.replace(tzinfo=TIMEZONE_HACK)
    currenttime = timezone.now()

    # ====================================================
    # Check for duplicates
    # ====================================================
    # We want to stop if this race is already in the database
    test_objs = SingleRaceDetails.objects.filter(
        # trackkey=track_obj, # I dont want to accidentally upload results across tracks
        # racedata=single_race.raceClass, # This gets modified by the collapse names code.
        roundnumber=single_race.roundNumber,
        racenumber=single_race.raceNumber,
        racedate=formatedtime,
        racelength=racelength,
        winninglapcount=maxlaps,
        mainevent=single_race.mainEvent,
        maineventroundnum=single_race.mainEventRoundNum,
        maineventparsed=single_race.mainEventParsed)

    if (len(test_objs) != 0):
        # We want to tell the user since this not what they wanted.
        # We can be reasonably certain this file has already been uploaded.
        raise FileAlreadyUploadedError("File already uploaded")

    # ====================================================
    # Insert Racers
    # ====================================================
    # We want to add a new racer if one does not already exist.
    for racer in single_race.raceHeaderData:
        racer_obj, _ = Racer.objects.get_or_create(racerpreferredname=racer['Driver'])
        racer['racer_obj'] = racer_obj

    # ====================================================
    # Insert Race Details
    # ====================================================
    log.debug('metric=UploadSingleRaceDetails trackName=%s racedata=%s racenumber=%s', 
        track_obj.trackname, single_race.raceClass, single_race.raceNumber)
    details_obj = SingleRaceDetails(trackkey=track_obj,
                                    racedata=single_race.raceClass,
                                    roundnumber=single_race.roundNumber,
                                    racenumber=single_race.raceNumber,
                                    racedate=formatedtime,
                                    uploaddate=currenttime,
                                    racelength=racelength,
                                    winninglapcount=maxlaps,
                                    mainevent=single_race.mainEvent,
                                    maineventroundnum=single_race.mainEventRoundNum,
                                    maineventparsed=single_race.mainEventParsed)
    details_obj.save()

    # ====================================================
    # Insert Race Laps
    # ====================================================
    bulk_laptimes = []
    # For each racer in the raceHeaderData
    for racer in single_race.raceHeaderData:
        # Upload each lap for this racer, their care number - 1 indicates
        # the index of their laps in the lapRowsTime list.
        index = racer['Car#'] - 1

        # This would be a good place to check and see if there are enough laps, it
        # has been observed that the parser can fail to get everyone's lap data (another
        # pending bug).
        if index >= len(single_race.lapRowsTime):
            # I am going to try and move on, it is not totally un-expected that the race director
            # might mangle this part. SIMPLE - Racer in header, but no laps recorded.
            continue
            # raise FileUnableToParseError("This racer %s is missing his laps: %s" % (index, single_race.raceHeaderData))
        for row in range(0, len(single_race.lapRowsTime[index])):
            # print("Debug: ", racer['racer_obj'], row, single_race.lapRowsPosition[index][row])

            if (single_race.lapRowsPosition[index][row] == ''):
                single_race.lapRowsPosition[index][row] = None
                single_race.lapRowsTime[index][row] = None

            lap_obj = LapTimes(raceid=details_obj,
                               racer=racer['racer_obj'],
                               racelap=row,
                               raceposition=single_race.lapRowsPosition[index][row],
                               racelaptime=single_race.lapRowsTime[index][row])
            bulk_laptimes.append(lap_obj)

    log.debug('metric=UploadSingleRaceLaps trackName=%s racedata=%s racenumber=%s totalLapCount=%d', 
        track_obj.trackname, single_race.raceClass, single_race.raceNumber, len(bulk_laptimes))
    LapTimes.objects.bulk_create(bulk_laptimes)

    # ====================================================
    # Insert Race Results
    # ====================================================
    '''
        Example of the data structure we will work with here:
                          [{"Driver":"TOM WAGGONER",
                          "Car#":"9",
                          "Laps":"26",
                          "RaceTime":"8:07.943",
                          "Fast Lap":"17.063",
                          "Behind":"6.008",
                          "Final Position":9} , ...]
    '''
    bulk_raceheader = []
    for racer in single_race.raceHeaderData:
        if (racer['RaceTime'] == ''):
            racer['RaceTime'] = None
        else:
            # Convert the racetime to a datetime.time object,
            # this is required to ensure the microseconds are not
            # chopped off.
            racer['RaceTime'] = datetime.datetime.strptime(racer['RaceTime'], "%M:%S.%f")

        if (racer['Fast Lap'] == ''):
            racer['Fast Lap'] = None
        if (racer['Behind'] == ''):
            racer['Behind'] = None

        individual_result = SingleRaceResults(raceid=details_obj,
                                              racer=racer['racer_obj'],
                                              carnum=racer['Car#'],
                                              lapcount=racer['Laps'],
                                              racetime=racer['RaceTime'],
                                              fastlap=racer['Fast Lap'],
                                              behind=racer['Behind'],
                                              finalpos=racer['Final Position'])

        bulk_raceheader.append(individual_result)

    SingleRaceResults.objects.bulk_create(bulk_raceheader)
    # TODO - I can see the following code being good stuff to log.

    # ===============================================================
    # Collapse alias racer names.
    # ===============================================================
    collapse_racer_names()

    # ===============================================================
    # Collapse class names.
    # ===============================================================
    # Note - this likely changed the race's name.
    collapse_alias_classnames(SingleRaceDetails.objects.filter(id__exact=details_obj.id))

    return SingleRaceDetails.objects.get(pk=details_obj.id)


def _calculate_race_length(raceHeaderData):
    '''
    Look at all the racetimes and take largest number of minutes (note: we only
    look at the number of minutes in the race, not the number of seconds).

    Some people may be recorded as not going the entire race time, or have no
    race time at all.
    '''
    maxNumMinutes = 0

    for racer in raceHeaderData:
        if (racer["RaceTime"] == ''):
            continue
        else:
            numMin = int(racer["RaceTime"].split(':')[0])
            if numMin > maxNumMinutes:
                maxNumMinutes = numMin

    return maxNumMinutes


class FileUnableToParseError(Exception):
    """Exception raised when we fail some basic parsing/processing of the race. Possible structural error in the results."""
    pass


class FileAlreadyUploadedError(Exception):
    """Exception raised when a race has already been placed in the system."""
    pass
