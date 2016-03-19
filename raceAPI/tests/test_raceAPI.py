'''
Created on June 6, 2015

@author: Anthony Honstain
'''
import datetime
import pytz

from core.models import SingleRaceDetails, RacerId

from uploadresults.tests.test_general_race_uploader_api import GeneralRaceUploaderAPI
from uploadresults.tests.test_general_race_uploader_api import RaceUploadRecord


class MainEventByRacedayLookup(GeneralRaceUploaderAPI):

    singlerace_testfile1 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/1/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 1, Race# 1

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Anthony Honstain            #2         28         8:00.588         17.042
lowercase jim            #4         27         8:08.928         17.116
Charlie, Jon            #5         26         8:00.995         17.274
Delta, Jon            #3         25         8:02.680         17.714
Echo, Jon            #1          1           35.952         35.952

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 5/35.95 1/26.24 4/30.95 2/27.01 3/29.63
         1/17.47 4/18.67 2/19.47 3/17.76
         1/17.33 4/17.71 2/17.83 3/17.55
         1/17.27 4/19.73 2/17.85 3/17.92
         1/17.08 4/19.64 2/18.29 3/17.88
         1/17.07 4/18.33 2/17.92 3/17.82
         1/17.66 4/17.83 2/17.66 3/17.89
         1/17.39 4/17.82 2/17.37 3/17.67
         1/17.54 4/18.88 2/17.79 3/17.75
         1/17.04 4/18.62 2/17.41 3/17.67
         1/17.30 4/17.72 2/17.52 3/18.81
         1/19.07 4/20.62 2/17.82 3/18.23
         1/17.30 4/20.27 2/17.46 3/17.35
         1/17.05 4/18.85 2/17.63 3/18.45
         1/17.10 4/19.43 2/17.59 3/17.61
         1/17.46 4/18.10 2/17.96 3/18.86
         1/17.17 4/17.82 2/17.68 3/17.67
         1/17.28 4/17.86 2/17.96 3/17.27
         1/17.05 4/17.89 2/17.43 3/17.47
         1/17.16 4/18.43 2/17.34 3/17.60
         1/17.39 4/23.66 2/18.26 3/17.73
         1/17.44 4/18.52 2/17.51 3/18.30
         1/17.28 4/19.18 2/18.22 3/21.11
         1/17.39 4/18.03 2/17.65 3/17.46
         1/17.48 4/18.05 2/17.83 3/17.74
         1/17.14         2/17.25 3/19.69
         1/17.61         2/17.11
         1/20.71
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
      1/     28/     25/     27/     26/
    35.9  8:18.5  8:02.6  8:08.9  8:00.9
    '''

    def get_race_records_to_upload(self):
        return [
            RaceUploadRecord('upload1', self.singlerace_testfile1)]

    def test_multipleraces_upload_records(self):
        self.assertEqual(len(self.racelist_to_upload), 1)
        single_race_detals_pk = self.racelist_to_upload[0].single_race_details_pk

        laptime_url = '/api/TrackName/{0}/SingleRaceDetails/{1}/LapTimes/'.format(
            self.supported_trackname_obj.pk, single_race_detals_pk)

        response = self.client.get(laptime_url)
        self.assertEqual(response.status_code, 200, laptime_url)

        #for row in response.data:
        #    print(row)
        # Verify that all the laps are in here, each should get 28 laps 28*5=140
        self.assertEqual(len(response.data), 140)
