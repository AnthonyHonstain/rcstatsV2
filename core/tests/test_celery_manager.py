'''
Created on March 25, 2016

@author: Anthony Honstain
'''
import datetime
import pytz
import mock

from core import models

from core.sharedmodels.king_of_the_hill_summary import KoHSummary

from django.contrib.auth.models import User

from uploadresults.tests.test_general_race_uploader_api_base import GeneralRaceUploaderAPIBase
from uploadresults.tests.test_general_race_uploader_api_base import RaceUploadRecord

from core import celery_manager


class TestCeleryManager(GeneralRaceUploaderAPIBase):

    singlerace_testfile1 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/1/2012

                   TACOMA R/C RACEWAY

Mod Buggy A Main                                         Round# 1, Race# 1

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Mod One            #2         28         8:00.588         17.042
Mod Two            #4         27         8:08.928         17.116
Mod Three          #5         26         8:00.995         17.274
Mod Four           #3         25         8:02.680         17.714
Mod Five           #1          1           35.952         35.952

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

    singlerace_testfile2 = '''Scoring Software by www.RCScoringPro.com                9:36:42 PM  7/1/2012

                   TACOMA R/C RACEWAY

Stock Buggy A Main                                         Round# 1, Race# 2

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Stock One            #2         28         8:00.588         17.042
Stock Two            #4         27         8:08.928         17.116
Stock Three          #5         26         8:00.995         17.274
Stock Four           #3         25         8:02.680         17.714
Stock Five           #1          1           35.952         35.952

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
            RaceUploadRecord('upload1', self.singlerace_testfile1),
            RaceUploadRecord('upload2', self.singlerace_testfile2),
            ]


    def test_celery_manager_empty(self):
        race_pk = self.racelist_to_upload[0].single_race_details_pk
        single_race_detail = models.SingleRaceDetails.objects.get(pk=race_pk)

        with mock.patch('core.celery_manager._mail_single_race') as mail_single_race:

            celery_manager.mail_all_users(single_race_detail.id)
            
            mail_single_race.assert_not_called()


    def test_construct_mail_content(self):
        '''
        Basic sanity check that the email html/txt can be generated and some
        of the expected data is rendered.
        '''
        host = 'localhost'
        user_with_sub = User.objects.create_user('sub', 'sub@gmail.com', 'sub')
        username = user_with_sub

        race_pk = self.racelist_to_upload[0].single_race_details_pk
        single_race_detail = models.SingleRaceDetails.objects.select_related('track').get(pk=race_pk)

        text_content, html_content = celery_manager._construct_mail_content(host, username, single_race_detail)

        self.assertIn('http://localhost/results/singleracedetail/{}/'.format(single_race_detail.id), text_content)
        self.assertIn('Mod One', text_content)

        self.assertIn('http://localhost/results/singleracedetail/{}/'.format(single_race_detail.id), html_content)
        self.assertIn('Mod One', html_content)
        self.assertIn(self.track_obj.name, html_content)
        self.assertIn(
            'http://localhost/results/racer-list/{}/racer/'.format(self.track_obj.id),
            html_content)


    def test_single_subscriber(self):
        '''
        Pretty crud test right now, now sure if I want to make this much more extensible
        of if I have a solid amount of coverage right here.

        If I make this any more fancy, or I find strange behavior in production
        I should clean up (DRY) and break out a few more test cases.

        TODO - I haven't decided what the right way to organize this type of test
        should be from an archetectural perspective.
            Should some of this data setup be centralized so I don't end up repeateding
            it in a few places??
        '''
        user_no_sub = User.objects.create_user('nosub', 'nosub@gmail.com', 'nosub')
        user_with_sub = User.objects.create_user('sub', 'sub@gmail.com', 'sub')

        mod_class = models.OfficialClassNames(raceclass='Mod Buggy')
        mod_class.save()

        stock_class = models.OfficialClassNames(raceclass='Stock Buggy')
        stock_class.save()

        mod_sub = models.ClassEmailSubscription(raceclass=mod_class, user=user_with_sub, active=True)
        mod_sub.save()
        stock_sub = models.ClassEmailSubscription(raceclass=stock_class, user=user_with_sub, active=False)
        stock_sub.save()

        mod_race_pk = self.racelist_to_upload[0].single_race_details_pk
        mod_race_detail = models.SingleRaceDetails.objects.get(pk=mod_race_pk)

        stock_race_pk = self.racelist_to_upload[1].single_race_details_pk
        stock_race_detail = models.SingleRaceDetails.objects.get(pk=stock_race_pk)

        # Validate that the stock race doesn't trigger an email
        with mock.patch('core.celery_manager._mail_single_race') as mail_single_race:

            celery_manager.mail_all_users(stock_race_detail.id)

            mail_single_race.assert_not_called()

        # Validate the mod buggy race finds a single subscriber.
        with mock.patch('core.celery_manager._mail_single_race') as mail_single_race:

            celery_manager.mail_all_users(mod_race_detail.id)

            mail_single_race.assert_called_with(user_with_sub, mod_race_detail)


    def test_find_king_of_the_hill_classes(self):
        mod_class = models.OfficialClassNames(raceclass='Mod Buggy', active=True)
        mod_class.save()

        stock_class = models.OfficialClassNames(raceclass='Stock Buggy', active=True)
        stock_class.save()

        track_and_class_list = celery_manager.find_king_of_the_hill_classes()

        self.assertEqual(track_and_class_list, [
            (self.track_obj.id, mod_class.id),
            (self.track_obj.id, stock_class.id),
            ])


    def test_compute_koh_by_track_class(self):
        # TODO - need to add a task for the other main function in the celery_manager
        mod_class = models.OfficialClassNames(raceclass='Mod Buggy', active=True)
        mod_class.save()

        with mock.patch('core.celery_manager._compute_king_of_the_hill') as compute_patch:
            celery_manager.compute_koh_by_track_class(self.track_obj.id, mod_class.id)

            compute_patch.assert_called_once_with(self.track_obj, mod_class, mock.ANY)


    def test_pre_compute_KoH(self):
        mod_class = models.OfficialClassNames(raceclass='Mod Buggy', active=True)
        mod_class.save()

        stock_class = models.OfficialClassNames(raceclass='Stock Buggy', active=True)
        stock_class.save()

        # We assume there are only a few races in the system, so we grab one and pick
        # is the current time.
        single_race = models.SingleRaceDetails.objects.get(pk=self.racelist_to_upload[0].single_race_details_pk)
        now = single_race.racedate
        #utcnow = datetime.datetime.utcnow()
        #utcnow.replace(tzinfo=pytz.utc)
        koh_timeframe = now - datetime.timedelta(days=15)

        with mock.patch('core.celery_manager._cache_results') as cache_results:
            celery_manager._compute_king_of_the_hill(self.track_obj, mod_class, koh_timeframe)

            mod_one = models.Racer.objects.filter(racerpreferredname='Mod One').first()
            mod_two = models.Racer.objects.filter(racerpreferredname='Mod Two').first()
            mod_three = models.Racer.objects.filter(racerpreferredname='Mod Three').first()
            mod_four = models.Racer.objects.filter(racerpreferredname='Mod Four').first()
            mod_five = models.Racer.objects.filter(racerpreferredname='Mod Five').first()

            expected_data = []
            expected_data.append(KoHSummary(
                mod_class.id,
                mod_class.raceclass,
                mod_one.id,
                mod_one.racerpreferredname,
                20))

            expected_data.append(KoHSummary(
                mod_class.id,
                mod_class.raceclass,
                mod_two.id,
                mod_two.racerpreferredname,
                19))

            expected_data.append(KoHSummary(
                mod_class.id,
                mod_class.raceclass,
                mod_three.id,
                mod_three.racerpreferredname,
                18))

            expected_data.append(KoHSummary(
                mod_class.id,
                mod_class.raceclass,
                mod_four.id,
                mod_four.racerpreferredname,
                17))

            expected_data.append(KoHSummary(
                mod_class.id,
                mod_class.raceclass,
                mod_five.id,
                mod_five.racerpreferredname,
                16))

            cache_results.assert_called_with(self.track_obj, mod_class, expected_data)
