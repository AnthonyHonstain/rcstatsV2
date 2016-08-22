'''
Create 2016-08-21 to validate the racer list pages.

@author: Anthony Honstain
'''

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import core.models as models


class RacerListTests(TestCase):
    '''
    Validate the pages that list all of a tracks racers and pages that drill in on a specific racer.
    '''
    def setUp(self):
        models.TrackName.objects.create(id=1, trackname='Test_Track_0')

        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

    def tearDown(self):
        pass

    def test_racer_list_login_redirect(self):
        '''
        Verify that the accessing the page without auth redirects us.
        '''
        pass # TODO - havent decided if I want this stuff behind the reg wall yet.
        #client = Client()
        #response = client.get('/results/racer-list/1/')
        #self.assertRedirects(response, '/accounts/signin/?next=/results/racer-list/1/')

    def test_basic_racer_list_page(self):
        '''
        Sanity check the page loads
        '''
        response = self.client.get('/results/racer-list/1/')

        self.assertEqual(response.status_code, 200, 'Check the page response code')
