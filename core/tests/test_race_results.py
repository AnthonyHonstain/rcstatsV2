'''
Create 2016-08-21 to validate the race results pages.

@author: Anthony Honstain
'''

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import core.models as models


class RaceResultsTests(TestCase):
    '''
    Validate the pages that display all the race events for a track.
    '''
    def setUp(self):
        models.Track.objects.create(id=1, name='Test_Track_0')

        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

    def tearDown(self):
        pass

    def test_race_results_login_redirect(self):
        '''
        Verify that the accessing the page without auth redirects us.
        '''
        client = Client()
        response = client.get('/results/race-results/1/')
        self.assertRedirects(response, '/accounts/signin/?next=/results/race-results/1/')

    def test_basic_results_page(self):
        '''
        Sanity check the page loads
        '''
        response = self.client.get('/results/race-results/1/')

        self.assertEqual(response.status_code, 200, 'Check the page response code')

    # TODO - not much to test here yet because the page is just light wrapper for 
    # a javascript table that can page through all the past races using the API.
