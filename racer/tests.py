from django.test import TestCase

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import core.models as core_models
import racer.models as racer_models


class TestFollow(TestCase):
    '''
    Verify the basic logic for the follow functionality.
    '''
    def setUp(self):
        self.track = core_models.TrackName.objects.create(id=1, trackname='Test_Track_0')
        self.racerId_0 = core_models.RacerId.objects.create(racerpreferredname='test_racer_0')

        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

    def test_follow_page(self):
        '''
        Validate we can GET on a follow page without an existing record.
        '''
        test_url = '/racer/follow/track/{}/racerid/{}/'.format(self.track.id, self.racerId_0.id)
        response = self.client.get(test_url)

        self.assertEqual(response.status_code, 200, 'Check the page response code')
  
    def test_follow_initial_submit(self):
        '''
        Validate we can GET and POST to create a new follow record.
        '''
        test_url = '/racer/follow/track/{}/racerid/{}/'.format(self.track.id, self.racerId_0.id)
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200, 'Check the page response code')

        form = {'active':False}
        response = self.client.post(test_url, form)
        self.assertRedirects(response, '/')

        new_follow = racer_models.Follow.objects.get(
        	user__exact=self.user, 
        	racerId__exact=self.racerId_0)
        self.assertEquals(new_follow.active, False, 'Verify the follow activity was persisted')

    def test_follow_initial_update(self):
        '''
        Validate we can POST an update to an existing follow record.
        '''
        racer_models.Follow.objects.create(user=self.user, racerId=self.racerId_0, active=False)
        test_url = '/racer/follow/track/{}/racerid/{}/'.format(self.track.id, self.racerId_0.id)
        form = {'active':True}
        response = self.client.post(test_url, form)
        self.assertRedirects(response, '/')

        new_follow = racer_models.Follow.objects.get(
        	user__exact=self.user, 
        	racerId__exact=self.racerId_0)
        self.assertEquals(new_follow.active, True, 'Verify the follow activity was persisted')
