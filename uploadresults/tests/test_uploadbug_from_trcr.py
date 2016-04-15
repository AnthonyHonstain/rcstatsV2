'''
Created on April 2016

@author: Anthony Honstain
'''
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

import datetime
import os
import pytz

from uploadresults.tests.test_general_race_uploader_api_base import GeneralRaceUploaderAPIBase
from uploadresults.tests.test_general_race_uploader_api_base import RaceUploadRecord
import uploadresults.models as models
import core.models as core_models

from core.models import (
    LapTimes,
    SingleRaceDetails,
    SingleRaceResults,
    SupportedTrackName,
    TrackName,
    RacerId)


class RaceUploadRecord():
    def __init__(self, filename, filecontent):
        self.filename = filename
        self.filecontent = filecontent
        self.single_race_details_pk = None


class TestBugFromTRCRUploader(GeneralRaceUploaderAPIBase):

    singlerace_testfile1 = '''
Scoring Software by www.RCScoringPro.com                4:44:47 PM  04/09/2016

                               TACOMA RC RACEWAY

4WD SHORT COURSE A3 Main                                      Round# 4, Race# 33

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
                 JASON MCCARTY    #1       1        3.514                     
                BRIAN UMPSTEAD    #2       1        4.139                0.625
                    GREG JONES    #3       1        4.736                1.222
                    BRYAN BIRD    #4       1       12.119                8.605
                    JOHN STONE    #5       1       12.607                9.093

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 1/3.514 2/4.139 3/4.736 4/12.11 5/12.60                                        
     N/A     N/A     N/A     N/A     N/A                                        
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
      1/      1/      1/      1/      1/                                        
     3.5     4.1     4.7    12.1    12.6                                                       
    '''

    def get_race_records_to_upload(self):
        return [
            RaceUploadRecord('upload1', self.singlerace_testfile1)
            ]


    def test_multipleraces_upload_records(self):
        # ====================================================
        # Validate Upload Records
        # ====================================================
        # because each file got uploaded separately, each will have its own primary record.
        #for race_to_upload in self.racelist_to_upload:

        single_race_details_file1 = core_models.SingleRaceDetails.objects.get(
            pk=self.racelist_to_upload[0].single_race_details_pk)

        self.assertEquals(single_race_details_file1.racedata, '4WD SHORT COURSE')
        self.assertEquals(single_race_details_file1.racenumber, 33)