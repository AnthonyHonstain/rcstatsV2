'''
Created on May 11, 2013

@author: Anthony Honstain
'''
import datetime
import pytz

from core.models import SingleRaceDetails, Racer

import uploadresults.tests.test_general_race_uploader_easyupload as uploadresultstests
import core.result_history_queries as result_history


class MainEventByRacedayLookup(uploadresultstests.GeneralRaceUploader):

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

    singlerace_testfile2 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/2/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 2, Race# 2

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Anthony Honstain            #2         28         8:02.588         17.042
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

    singlerace_testfile3 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/3/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 3, Race# 3

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Anthony Honstain            #2         28         8:03.588         17.042
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

    # WARNING - this race was intentionally mangled to verify the robustness of the code
    # to group recent fast times.
    singlerace_testfile4 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/4/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 4, Race# 4

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Anthony Honstain            #2         28         8:40.588         17.042
lowercase jim            #4         27         8:08.928         17.116
Charlie, Jon            #5         26         8:00.995         17.274
Delta, Jon            #3         25         8:02.680         17.714
Echo, Jon            #1          1           35.952         35.952

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 5/35.95 1/26.24 4/30.95 2/27.01 3/29.63
                 4/18.67 2/19.47 3/17.76
         1/17.33 4/17.71 2/17.83 3/17.55
                 4/19.73 2/17.85 3/17.92
         1/17.08 4/19.64 2/18.29 3/17.88
                 4/18.33 2/17.92 3/17.82
         1/17.66 4/17.83 2/17.66 3/17.89
                 4/17.82 2/17.37 3/17.67
         1/17.54 4/18.88 2/17.79 3/17.75
                 4/18.62 2/17.41 3/17.67
         1/17.30 4/17.72 2/17.52 3/18.81
                 4/20.62 2/17.82 3/18.23
         1/17.30 4/20.27 2/17.46 3/17.35
                 4/18.85 2/17.63 3/18.45
         1/17.10 4/19.43 2/17.59 3/17.61
                 4/18.10 2/17.96 3/18.86
         1/17.17 4/17.82 2/17.68 3/17.67
                 4/17.86 2/17.96 3/17.27
         1/17.05 4/17.89 2/17.43 3/17.47
                 4/18.43 2/17.34 3/17.60
         1/17.39 4/23.66 2/18.26 3/17.73
                 4/18.52 2/17.51 3/18.30
         1/17.28 4/19.18 2/18.22 3/21.11
                 4/18.03 2/17.65 3/17.46
                 4/18.05 2/17.83 3/17.74
                         2/17.25 3/19.69
         1/17.61         2/17.11
         1/20.71
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
      1/     28/     25/     27/     26/
    35.9  8:18.5  8:02.6  8:08.9  8:00.9
    '''

    singlerace_testfile5 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/5/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 5, Race# 5

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Anthony Honstain            #2         28         8:05.588         17.042
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

    racelist_to_upload = [{'filename': 'upload1', 'filecontent': singlerace_testfile1},
                          {'filename': 'upload2', 'filecontent': singlerace_testfile2},
                          {'filename': 'upload3', 'filecontent': singlerace_testfile3},
                          {'filename': 'upload4', 'filecontent': singlerace_testfile4},
                          {'filename': 'upload5', 'filecontent': singlerace_testfile5}]

    def test_multipleraces_upload(self):

        # =====================================================
        # Validate Race Details
        # =====================================================
        # Validate the race details have been uploaded.

        #
        # WARNING - if these fail, it likely means the upload failed.
        #
        raceobj1 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="MODIFIED BUGGY",
                                                 racenumber=1,
                                                 roundnumber=1,
                                                 racelength=8,
                                                 winninglapcount=28,
                                                 mainevent=1)
        raceobj2 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="MODIFIED BUGGY",
                                                 racenumber=2,
                                                 roundnumber=2,
                                                 racelength=8,
                                                 winninglapcount=28,
                                                 mainevent=1)
        raceobj3 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="MODIFIED BUGGY",
                                                 racenumber=3,
                                                 roundnumber=3,
                                                 racelength=8,
                                                 winninglapcount=28,
                                                 mainevent=1)
        raceobj4 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="MODIFIED BUGGY",
                                                 racenumber=4,
                                                 roundnumber=4,
                                                 racelength=8,
                                                 winninglapcount=28,
                                                 mainevent=1)
        raceobj5 = SingleRaceDetails.objects.get(trackkey=self.trackname_obj,
                                                 racedata="MODIFIED BUGGY",
                                                 racenumber=5,
                                                 roundnumber=5,
                                                 racelength=8,
                                                 winninglapcount=28,
                                                 mainevent=1)
        # =====================================================
        # Validate Racers
        # =====================================================
        # The race should now be uploaded, we want to validate it is in the system.
        car1 = Racer.objects.get(racerpreferredname="Anthony Honstain")

        # We expect to find a race just for the given day, need to be careful that we
        # understand timezone of the user that is making the query.
        date = datetime.datetime(2012, 7, 3, 0, 0, 0, tzinfo=pytz.timezone('America/Los_Angeles'))
        results_template_format = result_history.main_event_by_raceday_lookup(self.supported_trackname_obj, date)

        self.assertEquals(len(results_template_format), 1)

        # EXAMPLE results_template_format
        #     [
        #        {
        #        'individual_results': '[[1, "racer name 1", 28, "00:08:10.761000", "16.528", "None"],
        #            [2, "racer name 2", 27, "00:08:01.661000", "16.725", "None"],
        #            [3, "racer name 3", 25, "00:08:16.037000", "17.053", "None"],
        #            [4, "racer name 4", 20, "00:08:05.180000", "20.883", "None"],
        #            [5, "racer name 5", 12, "00:03:57.669000", "17.760", "None"]]',
        #        'roundnumber': 5,
        #        'tagid': 2139,
        #        'racenumber': 1,
        #        'racedate': datetime.datetime(2012, 5, 12, 17, 26, 32),
        #        'racedata': u'Mod Short Course A Main'},
        self.assertEqual(results_template_format[0]['roundnumber'], 3)
