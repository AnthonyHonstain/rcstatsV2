'''
Create 2016-04-30 to validate the king of the hill logic

@author: Anthony Honstain
'''

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import core.models as models


class KingOfTheHillTests(TestCase):
    '''
    Validate the pages that handle user signup for race race emails.
    '''
    def setUp(self):
        models.TrackName.objects.create(id=1, trackname='Test_Track_0')

        self.mod = models.OfficialClassNames(raceclass='Mod_Buggy_Test')
        self.mod.save()
        self.stock = models.OfficialClassNames(raceclass='Stock_Buggy_Test')
        self.stock.save()
        self.truck = models.OfficialClassNames(raceclass='Stock_Truck_Test')
        self.truck.save()

        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

    def tearDown(self):
        pass

    def test_koh_login_redirect(self):
        '''
        Verify that the accessing the page without auth redirects us.
        '''
        client = Client()
        response = client.get('/results/king-of-the-hill/1/')
        self.assertRedirects(response, '/accounts/signin/?next=/results/king-of-the-hill/1/')

    def test_basic_koh(self):
        '''
        Sanity check the page loads
        '''
        response = self.client.get('/results/king-of-the-hill/1/')

        self.assertEqual(response.status_code, 200, 'Check the page response code')
