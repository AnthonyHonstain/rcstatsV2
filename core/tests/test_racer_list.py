'''
Create 2016-08-21 to validate the racer list pages.

@author: Anthony Honstain
'''
import datetime
import pytz

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import core.models as models


class RacerListTests(TestCase):
    '''
    Validate the pages that list all of a tracks racers and pages that drill in on a specific racer.
    '''
    def setUp(self):
        self.track = models.TrackName.objects.create(id=1, trackname='Test_Track_0')

        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

        self.racer = models.RacerId.objects.create(id=1, racerpreferredname='TestRacer')
        
        # Adding a race so we trigger some of the logic to lookup race results and calculate stats.
        racedate = datetime.datetime(
            year=2012,
            month=1,
            day=14,
            hour=20,
            minute=9,
            second=3,
            tzinfo=pytz.UTC)
      
        self.singlerace = models.SingleRaceDetails.objects.create(
            id=1,
            trackkey=self.track,
            racedata='TestClassBuggy0 A main',
            racedate=racedate,
            uploaddate=racedate,
            racelength='8',
            roundnumber=3,
            racenumber=16,
            winninglapcount='2',
            mainevent=1)          

        self.result0 = models.SingleRaceResults.objects.create(
            id=1,
            raceid=self.singlerace,
            racerid=self.racer,
            carnum=2,
            lapcount=28,
            racetime=datetime.time(second=20),
            fastlap='16.939',
            finalpos=1)

    def tearDown(self):
        pass

    def test_basic_racer_list_page(self):
        '''
        Sanity check the page loads
        '''
        response = self.client.get('/results/racer-list/1/')

        self.assertEqual(response.status_code, 200, 'Check the page response code')

    def test_basic_single_racer_page(self):
        '''
        Sanity check the page loads
        '''
        response = self.client.get('/results/racer-list/1/racerid/1/')

        self.assertEqual(response.status_code, 200, 'Check the page response code')

    def test_history(self):
        '''
        Sanity check the page loads
        '''
        response = self.client.get('/results/racer-list/1/racerid/1/history/')

        self.assertEqual(response.status_code, 200, 'Check the page response code')

    def test_racer_list_login_redirect(self):
        '''
        Verify that the accessing the page without auth redirects us.
        '''
        client = Client()
        response = client.get('/results/racer-list/1/racerid/1/history/')
        self.assertRedirects(
            response, 
            '/accounts/signin/?next=/results/racer-list/1/racerid/1/history/')
