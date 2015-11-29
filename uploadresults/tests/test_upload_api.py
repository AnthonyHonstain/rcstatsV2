'''
Created on Feb 2015

@author: Anthony Honstain
'''
from django.contrib.auth.models import User
from django.test import TestCase

import mock

import uploadresults.models as models
import core.models as core_models


class RaceUploadRecord():
    def __init__(self, filename, filecontent):
        self.filename = filename
        self.filecontent = filecontent
        self.easy_uploader_primary_record_pk = None


class UploadApi(TestCase):
    '''
    A set of basic tests to verify the basic functionality of the endpoint to upload races.

    Some basic tests of the API uploader and testing API behavior.
    '''

    singlerace_testfile1 = '''Scoring Software by www.RCScoringPro.com                9:26:42 PM  7/17/2012

                   TACOMA R/C RACEWAY

MODIFIED BUGGY A Main                                         Round# 3, Race# 2

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Alpha, Jon            #2         28         8:18.588         17.042
Beta, Jon            #4         27         8:08.928         17.116
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
        return [RaceUploadRecord('upload1', UploadApi.singlerace_testfile1)]

    def setUp(self):
        self.racelist_to_upload = self.get_race_records_to_upload()

        User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

        # Need a supported track in the system.
        trackname_obj = core_models.TrackName(trackname="TACOMA R/C RACEWAY")
        trackname_obj.save()
        self.trackname_obj = trackname_obj

        sup_trackname_obj = core_models.SupportedTrackName(trackkey=trackname_obj)
        sup_trackname_obj.save()
        self.supported_trackname_obj = sup_trackname_obj

    def test_basic_upload_endpoint_invalid_data(self):
        '''
        Verify that we can't upload without providing the required fields.
        '''
        # Check None, note - these get turned to strings 'None'
        upload_data = {
            "trackname": self.trackname_obj.id,
            "filename": None,
            "data": None}
        response = self.client.post('/upload/single_race_upload/', upload_data)
        self.assertEqual(response.status_code, 400)

        # Check min length and for empty fields.
        for race_to_upload in self.racelist_to_upload:
            upload_data = {
                "trackname": self.trackname_obj.id,
                "filename": "",
                "data": "fail"}
            response = self.client.post('/upload/single_race_upload/', upload_data)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['filename'], ['This field may not be blank.'])
            self.assertEqual(response.data['data'], ['Ensure this field has at least 10 characters.'])

        # Check min length and for empty fields.
        for race_to_upload in self.racelist_to_upload:
            upload_data = {
                "trackname": None,
                "filename": race_to_upload.filename,
                "data": race_to_upload.filecontent}
            response = self.client.post('/upload/single_race_upload/', upload_data)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['trackname'], ['Incorrect type. Expected pk value, received str.'])

    def test_endpoint_to_get_tracknames(self):
        response = self.client.get("/upload/TrackNameList/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1, 'Should only be one track in the system')
        self.assertEqual(response.data[0]['trackname'], "TACOMA R/C RACEWAY")


    def test_outgoing_email_triggered_by_upload(self):
        '''
        Verify that we call mail_single_race.delay with the single_race_details.id when uploading a race.
        '''
        with mock.patch('uploadresults.views.mail_single_race.delay') as mock_mail_single_race_delay:

            # Process each race/file from the list to upload separately.
            for race_to_upload in self.racelist_to_upload:
                upload_data = {
                    "trackname": self.trackname_obj.id,
                    "filename": race_to_upload.filename,
                    "data": race_to_upload.filecontent}
                response = self.client.post('/upload/single_race_upload/', upload_data)
                # response.data {
                #     'uploadrecord': 2, 'id': 2, 'data': '.........raw-data....'
                #     'owner': 'temporary', 'ip': '127.0.0.1', 'primaryrecord': 2,
                #     'trackname': 1, 'filename': 'upload2'}

                single_race_data_pk = response.data['id']
                uploadrecord_pk = response.data['uploadrecord']
                self.assertEqual(response.status_code, 201)

                # Now that we have the new SingleRaceData record created we can sanity check the get endpoint
                response = self.client.get("/upload/single_race_upload_detail/" + str(single_race_data_pk) + "/")
                self.assertEqual(response.status_code, 200)

                # We are going to retrieve the single_race_details records for this upload.
                # There is no use case beyond testing for the upload API to expose this, so we will
                # get it from the model.
                easy_uploaded_races = models.EasyUploadedRaces.objects.filter(upload__exact=uploadrecord_pk)

                # TODO - WARNING - if we start including multiple races in a single upload (more realistic)
                # we will need to address this.
                self.assertEquals(len(easy_uploaded_races), 1, 'Test infastructure only supports single race event per upload')

                # We are going to pull the single race details out of this and store it in our
                # RaceUploadRecord so the different tests can use it.
                race_to_upload.single_race_details_pk = easy_uploaded_races[0].racedetails.id

            single_race_details_file1 = core_models.SingleRaceDetails.objects.get(
                pk=self.racelist_to_upload[0].single_race_details_pk)

            mock_mail_single_race_delay.assert_called_with(single_race_details_file1.id)
