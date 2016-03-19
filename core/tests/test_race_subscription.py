'''
Create 2016-03-19 to validate the race email signup pages.

@author: Anthony Honstain
'''
import datetime
import pytz

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import core.models as models


class RaceEmailSubscription(TestCase):
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

    def test_subscription_login_redirect(self):
        '''
        We just want to verify that the accessing the page without auth redirects us.
        '''
        client = Client()
        response = client.get('/results/race-emails/')
        self.assertRedirects(response, '/accounts/signin/?next=/results/race-emails/')

    def test_basic_subscription_list(self):
        '''
        We are checking that the single official class we created and be seen in the
        subscription form.
        '''
        response = self.client.get('/results/race-emails/')

        self.assertEqual(response.status_code, 200, 'Check the page response code')
        
        form_fields_set = set([x.name for x in response.context['form']])
        self.assertEqual(len(form_fields_set), 3, 'Enexpected number of fields in form.')
        self.assertEqual(form_fields_set, set(['Mod_Buggy_Test', 'Stock_Truck_Test', 'Stock_Buggy_Test']))

    def test_subscription_with_subs_list(self):
        '''
        Verify we see current active subscriptions
        '''
        models.ClassEmailSubscription(raceclass=self.mod, user=self.user, active=True).save()
        models.ClassEmailSubscription(raceclass=self.truck, user=self.user, active=True).save()

        response = self.client.get('/results/race-emails/')
        self.assertEqual(response.status_code, 200)

        form_fields_dict = {x.name:x.value() for x in response.context['form']}
        self.assertEqual(form_fields_dict, {'Mod_Buggy_Test':True, 'Stock_Truck_Test':True, 'Stock_Buggy_Test':False})

    def test_subscription_update(self):
        '''
        Verify we can post the form and the ClassEmailSubscription gets persisted.
        '''
        subs = models.ClassEmailSubscription.objects.all()
        self.assertEqual(len(subs), 0, 'Verify no subscriptions to start with')
        
        form = {'Mod_Buggy_Test':True, 'Stock_Truck_Test':False, 'Stock_Buggy_Test': False}
        response = self.client.post('/results/race-emails/', form)
        self.assertRedirects(response, '/')

        updated_subs = models.ClassEmailSubscription.objects.all()
        self.assertEqual(len(updated_subs), 1)
        self.assertEqual(updated_subs[0].user, self.user)
        self.assertEqual(updated_subs[0].raceclass.raceclass, 'Mod_Buggy_Test') 
        self.assertEqual(updated_subs[0].active, True)

    def test_subscription_crud(self):
        '''
        Hammer through a few crud iterations to validate the DB data.
        '''
        form = {'Mod_Buggy_Test':True, 'Stock_Truck_Test':False, 'Stock_Buggy_Test': False}
        response = self.client.post('/results/race-emails/', form)
        self.assertRedirects(response, '/')

        mod_sub = models.ClassEmailSubscription.objects.filter(user=self.user, raceclass=self.mod)[0]
        self.assertEqual(mod_sub.active, True)

        form = {'Mod_Buggy_Test':False, 'Stock_Truck_Test':True, 'Stock_Buggy_Test': False}
        response = self.client.post('/results/race-emails/', form)
        self.assertRedirects(response, '/')

        mod_sub = models.ClassEmailSubscription.objects.filter(user=self.user, raceclass=self.mod)[0]
        self.assertEqual(mod_sub.active, False)

        truck_sub = models.ClassEmailSubscription.objects.filter(user=self.user, raceclass=self.truck)[0]
        self.assertEqual(truck_sub.active, True)

        form = {'Mod_Buggy_Test':True, 'Stock_Truck_Test':False, 'Stock_Buggy_Test': True}
        response = self.client.post('/results/race-emails/', form)
        self.assertRedirects(response, '/')

        mod_sub = models.ClassEmailSubscription.objects.filter(user=self.user, raceclass=self.mod)[0]
        self.assertEqual(mod_sub.active, True)

        truck_sub = models.ClassEmailSubscription.objects.filter(user=self.user, raceclass=self.truck)[0]
        self.assertEqual(truck_sub.active, False)

        stock_sub = models.ClassEmailSubscription.objects.filter(user=self.user, raceclass=self.stock)[0]
        self.assertEqual(stock_sub.active, True)