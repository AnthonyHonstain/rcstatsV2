'''
Major rework/addition Feb 2015

Switching over to storing the raw race files in database record instead of
trying to keep track of races in a file (requiring me to juggle them into
a cloud like S3).

Add api for uploading files, since we are automating away the manual process
I wanted a fairly reasonable API to support the upload process, this code
as a whole needs MUCH better logging and a solid refactor, but at least
I was able to greatly improve the unit testing.

----------------------------------------------
Created on April 2013

The revised uploader, I further stream lined the user scenario so that
you need to click less buttons to get the nights race results uploaded.

    This handles the bulk of the heavy lifting in the upload process, organizing them
    for storage, validating and guiding the user, and pushing into the database.

    There is lots of special logic to collect and process metadata like ranking or
    fixing of the class names or racer names.

    ----------------------------------------------
    SIMPLE OVERIVEW of UI upload.
    ----------------------------------------------
        STEP 1) easyupload_track
            -
        STEP 2) easyupload_fileselect
            -
        STEP 3) easyupload_results
            - Take the stuff from part 2 and start uploading.

@author: Anthony Honstain
'''

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone

from uploadresults.models import EasyUploaderPrimaryRecord, EasyUploadRecord, EasyUploadedRaces, SingleRaceData
from uploadresults.process_singlerace import create_single_race_details, FileAlreadyUploadedError

from core.models import SupportedTrackName, TrackName

from uploadresults.rcscoringprotxtparser import RCScoringProTXTParser

import hashlib
import io
import re
import sys
import traceback

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from uploadresults.serializers import EasyUploaderPrimaryRecordSerializer, EasyUploadRecordSerializer, SingleRaceUploadSerializer, TrackNameSerializer

from core.celery import mail_single_race

import logging
log = logging.getLogger('defaultlogger')


class EasyUploaderPrimaryRecordViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint that allows EasyUploaderPrimaryRecord to be viewed.
    '''
    queryset = EasyUploaderPrimaryRecord.objects.all()
    serializer_class = EasyUploaderPrimaryRecordSerializer


class EasyUploadRecordViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint that allows EasyUploadRecord to be viewed.
    '''
    queryset = EasyUploadRecord.objects.all()
    serializer_class = EasyUploadRecordSerializer


class TrackNameList(viewsets.ReadOnlyModelViewSet):
    queryset = TrackName.objects.all()
    serializer_class = TrackNameSerializer


# It would appear I don't need this.
# from rest_framework.authentication import SessionAuthentication
# http://stackoverflow.com/questions/16501770/csrf-exempt-failure-apiview-csrf-django-rest-framework
# class UnsafeSessionAuthentication(SessionAuthentication):
#
#     def authenticate(self, request):
#         http_request = request._request
#         user = getattr(http_request, 'user', None)
#
#         if not user or not user.is_active:
#             return None
#
#         return (user, None)


class SingleRaceDataCreate(generics.CreateAPIView):
    '''
    API endpoint that supports uploading a single race at a time.
    '''
    #authentication_classes = (UnsafeSessionAuthentication,)
    queryset = SingleRaceData.objects.all()
    serializer_class = SingleRaceUploadSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):

        log.debug('metric=Starting_API_Upload')

        ip = '127.0.0.1'
        if 'HTTP_X_FORWARDED_FOR' in self.request.META:
            ip = self.request.META['HTTP_X_FORWARDED_FOR']

        trackname = TrackName.objects.get(pk=serializer.validated_data['trackname'].id)
        filename = serializer.validated_data['filename']

        # First create a record for this upload action
        primary_record = EasyUploaderPrimaryRecord(
            user=self.request.user,
            ip=ip,
            filecount=1,
            filecountsucceed=0,
            uploadstart=timezone.now(),
            trackname=trackname)
        primary_record.save()

        md5 = hashlib.md5()
        md5.update(serializer.validated_data['data'].encode('utf-8'))
        filemd5 = md5.hexdigest()

        upload_record = EasyUploadRecord(
            uploadrecord=primary_record,
            origfilename=filename,
            filename=filename,
            ip=ip,
            user=self.request.user,
            filesize=sys.getsizeof(serializer.validated_data['data']),
            filemd5=filemd5,
            uploadstart=timezone.now(),
            processed=False)
        upload_record.save()

        serializer.save(primaryrecord=primary_record,
                        uploadrecord=upload_record,
                        owner=self.request.user,
                        ip=ip)

        # ----------------------------------------------------------
        # WARNING - this is a shameless copy paste from easyupload_results
        # TODO - REFACTOR ALL THIS STUFF and break out some unit tests for
        # the new methods (good integration coverage already).
        # ----------------------------------------------------------

        upload_errors = [
            'Pass',
            'Invalid filename - it is possible the upload to the server drive failed',
            'Unable to parse the file - likely is has incompatible format',
            'No races found in the file',
            'There was no trackname/header set',
            'Not all races in the file had the same trackname/header',
            'This race has ALREADY been uploaded.',
            'Unknown error processing the file.']

        single_race_data_records = SingleRaceData.objects.filter(primaryrecord=primary_record).order_by('id')

        # TODO - log what records we are planning to start on.
        # print('single_race_data_records', single_race_data_records)

        resultpage_list = []

        # =======================================================================
        # Primary loop - process each file uploaded.
        #     Note we keep this as a separate lookup so that we get them all saved to disk before validation
        # =======================================================================
        for single_race_data in single_race_data_records:
            single_race_list = _initial_validation_of_uploaded_file(single_race_data)
            if single_race_list:
                resultpage_list.append(ResultPage(single_race_data, single_race_data.uploadrecord, single_race_list))

        for result_page in resultpage_list:
            result_page.upload_record.uploadstart = timezone.now()
            result_page.upload_record.save()

            # We are going to set every race to have the same track name
            first_trackname_on_page = result_page.single_race_list[0].trackName
            _modify_trackname(single_race_data, first_trackname_on_page, trackname.trackname)

            # Short term fix - set the trackname here in case in the future we want to break it out
            result_page.upload_record.trackname = trackname

            _final_validation_and_upload(result_page)

            # Set all the error messages to display
            if result_page.upload_record.errorenum:
                result_page.error_message = upload_errors[result_page.upload_record.errorenum]
            else:
                result_page.upload_time = str(result_page.upload_record.uploadfinish - result_page.upload_record.uploadstart)

        # TODO - maybe save another DB hit if we were a little smarter with our data structures
        # through this upload process.
        upload_records = EasyUploadRecord.objects.filter(uploadrecord=primary_record).order_by('id')
        error_list = [x.errorenum for x in upload_records if x.errorenum]  # Just want to know if any other errors occured.
        fail_count = len(error_list)

        # Need to record the finals stats on the upload.
        primary_record.uploadfinish = timezone.now()
        primary_record.filecountsucceed = primary_record.filecount - fail_count
        primary_record.save()

        log.debug('metric=Completed_API_Upload')


class SingleRaceDataDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = SingleRaceData.objects.all()
    serializer_class = SingleRaceUploadSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------

class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField()


@login_required(login_url='/login')
def easyupload_track(request):
    '''
    Initial page in the easy upload, provide a list of buttons (each track)
    that can be clicked to navigate to the next step.

    Step 1
    '''
    track_list = SupportedTrackName.objects.all().order_by('trackkey__trackname')
    return render_to_response('easyupload_track.html', {'track_list': track_list}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def easyupload_fileselect(request, track_id):
    '''
    The controller responsible for the file upload.

    Step 2

    I have modified the post to support multiple file at a single time. I have not attempted
    to user any fancy jquery, I am going to attempt the easy route.

    Example of request.FILES when I attempt multiple uploads.
        <MultiValueDict: {u'file':
            [<InMemoryUploadedFile: 912503d1335331695-race-results-round3.txt (text/plain)>,
            <InMemoryUploadedFile: 913274d1335482296-race-results-round1.txt (text/plain)>,
            <InMemoryUploadedFile: 913275d1335482311-race-results-round2.txt (text/plain)>]}>
    Example when I request only a single file:
        <MultiValueDict: {u'file':
        [<InMemoryUploadedFile: 912503d1335331695-race-results-round3.txt (text/plain)>]}>
    '''
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)
    track = supported_track.trackkey

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        # What causes the form to not be valid? You can check by putting
        # {{ form.errors }} {{ form.non_field_errors }} in the template.

        if (form.is_valid() and 'file' in request.FILES):
            # Need to make sure the key used for FILES[ ] matches up with the
            # form in the template.

            # Example: print request.FILES
            # <MultiValueDict: {u'file': [<InMemoryUploadedFile: 912503d1335331695-race-results-round3.txt (text/plain)>,
            #     <InMemoryUploadedFile: 913274d1335482296-race-results-round1.txt (text/plain)>,
            #     <InMemoryUploadedFile: 913275d1335482311-race-results-round2.txt (text/plain)>]}>

            # Bug - This is not the ideal solution but I need quick
            # way for this to work in production and in development.
            #     In the dev enviro, 'HTTP_X_FORWARD_FOR' is not a
            #     key in request.META
            ip = '127.0.0.1'
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR']

            file_list = request.FILES.getlist('file')

            # First create a record for this upload action
            primary_record = EasyUploaderPrimaryRecord(user=request.user,
                                                       ip=ip,
                                                       filecount=len(file_list),
                                                       filecountsucceed=0,
                                                       uploadstart=timezone.now(),
                                                       trackname=track)
            primary_record.save()

            # For reference http://stackoverflow.com/questions/851336/multiple-files-upload-using-same-input-name-in-django
            for inmem_file in file_list:
                _process_inmemmory_file(primary_record, ip, track, request.user, inmem_file)

            return redirect('easyupload_results', upload_id=primary_record.id)
        else:
            error = 'Failed to upload file.'
            return render_to_response('easyupload_fileselect.html',
                                      {'form': form, 'track': track, 'error_status': error},
                                      context_instance=RequestContext(request))

    else:
        form = UploadFileForm()
    return render_to_response('easyupload_fileselect.html',
                              {'form': form, 'supported_track': supported_track},
                              context_instance=RequestContext(request))


def _process_inmemmory_file(primary_record, ip, track, user, inmem_file):
    '''
    Helper function for Step 2
        Create EasyUploadRecord - track basic status on the upload.
        Create SingleRaceData - record responsible for holding the raw race file.

    The input file will be stored in DB and have a new record created for the file.

    primary_record: the EasyUploaderPrimaryRecord for the new upload record.
    ip: the ip recorded with the upload
    user: the django user recorded in the request
    file: the InMemoryUploadedFile
    '''
    upload_data = []

    md5 = hashlib.md5()

    # NOTE - inmem_file TYPE: <class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
    for chunk in inmem_file.chunks():
        # http://stackoverflow.com/questions/606191/convert-bytes-to-a-python-string
        upload_data.append(chunk.decode('utf8'))
        md5.update(chunk)

    # Note - we are using a hex digest here instead of plain 'digest'
    # so that we can store it as a string in the db without dealing with
    # encoding it.
    md5hexdigest = md5.hexdigest()

    # Record the information we need about the fileupload. Not everything
    # is immediately recorded (we record the status and finish time later).
    upload_record = EasyUploadRecord(
        uploadrecord=primary_record,
        origfilename=inmem_file.name,
        filename=inmem_file.name,
        ip=ip,
        user=user,
        filesize=inmem_file.size,
        filemd5=md5hexdigest,
        processed=False)
    upload_record.save()

    single_race_data = SingleRaceData(
        primaryrecord=primary_record,
        uploadrecord=upload_record,
        owner=user,
        ip=ip,
        trackname=track,
        filename=inmem_file.name,
        data=''.join(upload_data))
    single_race_data.save()


class ResultPage():
        '''
        Contains all the data associated with a single file of race results.
        Including results prior to database upload, and what to display to the users.

        Parameters
        ----------
        single_race_data : SingleRaceData
        upload_record : EasyUploadRecord
        single_race_list : List[SingleRace]
           List of SingleRace objects that contains the raw data parsed from the original race file
        '''
        def __init__(self, single_race_data, upload_record, single_race_list):
            self.single_race_data = single_race_data
            self.upload_record = upload_record
            # The SingleRace objects that have been parsed.
            self.single_race_list = single_race_list  # List of parsed races from a single file upload
            self.uploaded_race_list = []  # For display to the user.
            # TODO - ranking
            self.uploaded_raceid_list = []  # For ranking
            self.display_error = None
            self.upload_time = None


@login_required(login_url='/login')
def easyupload_results(request, upload_id):
    '''
    Final view to trigger the final generation of race results.

    Step 3
    '''
    primary_upload_record = get_object_or_404(EasyUploaderPrimaryRecord, pk=upload_id)
    track = primary_upload_record.trackname

    # We have already recorded this file as processed, there is nothing more
    # this script can do at this point. It is likely a user error.
    if (primary_upload_record.filecount == primary_upload_record.filecountsucceed):
        general_error_message = 'All of these files have been processed. It is likely that the races are already in the system. An administrator can probably fix the problem quickly.'
        return render_to_response('easyupload_validate.html',
                                  {'general_error': True, 'general_error_message': general_error_message},
                                  context_instance=RequestContext(request))

    # TODO - move this to a better spot, so it is easy to understand when coming from the database
    upload_errors = ['Pass',
                     'Invalid filename - it is possible the upload to the server drive failed',
                     'Unable to parse the file - likely is has incompatible format',
                     'No races found in the file',
                     'There was no trackname/header set',
                     'Not all races in the file had the same trackname/header',
                     'This race has ALREADY been uploaded.',
                     'Unknown error processing the file.']

    single_race_data_records = SingleRaceData.objects.filter(primaryrecord=primary_upload_record).order_by('id')

    # TODO - log what records we are planning to start on.
    # print('single_race_data_records', single_race_data_records)

    resultpage_list = []

    # =======================================================================
    # Primary loop - process each file uploaded.
    #     Note we keep this as a separate lookup so that we get them all saved to disk before validation
    # =======================================================================
    for single_race_data in single_race_data_records:
        single_race_list = _initial_validation_of_uploaded_file(single_race_data)
        if single_race_list:
            resultpage_list.append(ResultPage(single_race_data, single_race_data.uploadrecord, single_race_list))

    for result_page in resultpage_list:
        result_page.upload_record.uploadstart = timezone.now()
        result_page.upload_record.save()

        # DATA RESTORATION - This is to hopefully simplify restoring data in the event of
        # an emergency (all that would be needed would be these text files).
        first_trackname_on_page = result_page.single_race_list[0].trackName
        _modify_trackname(single_race_data, first_trackname_on_page, track.trackname)

        # Short term fix - set the trackname here in case in the future we want to break it out
        result_page.upload_record.trackname = track

        _final_validation_and_upload(result_page)

        # Set all the error messages to display
        if result_page.upload_record.errorenum:
            result_page.error_message = upload_errors[result_page.upload_record.errorenum]
        else:
            result_page.upload_time = str(result_page.upload_record.uploadfinish - result_page.upload_record.uploadstart)

    # TODO - maybe save another DB hit if we were a little smarter with our data structures
    # through this upload process.
    upload_records = EasyUploadRecord.objects.filter(uploadrecord=primary_upload_record).order_by('id')
    error_list = [x.errorenum for x in upload_records if x.errorenum]  # Just want to know if any other errors occured.
    fail_count = len(error_list)

    # Need to record the finals stats on the upload.
    primary_upload_record.uploadfinish = timezone.now()
    primary_upload_record.filecountsucceed = primary_upload_record.filecount - fail_count
    primary_upload_record.save()

    # Get basic information about the upload to display to the user
    total_uploadtime = str(primary_upload_record.uploadfinish - primary_upload_record.uploadstart)

    context = {'resultpage_list': resultpage_list,
               'total_uploadtime': total_uploadtime,
               'success_count': primary_upload_record.filecountsucceed,
               'fail_count': fail_count,
               'general_error': fail_count > 0,
               'general_error_message': None}
    return render_to_response('easyupload_validate.html',
                              context,
                              context_instance=RequestContext(request))


def _initial_validation_of_uploaded_file(single_race_data):
    '''
    Helper function to provide initial validation of the uploaded race file.

    SANITY CHECK the metadata on the race.

    Parameters
    ----------
    single_race_data : SingleRaceData
       Record of an individual race file being upload (can contain multiple races from a single round).
    '''
    log.debug('metric=Validate_SingleRaceData single_race_data=%s', single_race_data.id)

    easy_upload_record = EasyUploadRecord.objects.get(pk=single_race_data.uploadrecord.id)

    # =======================================================================
    # Phase A) validate I can retrieve the file and parse it.
    #    I expect most problems to be in the category (did they upload shit).
    # =======================================================================
    try:
        single_race_list = _parse_raw_upload_string(single_race_data.filename, single_race_data.data)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log.error('metric=UploadError type=Exception_SingleRaceData single_race_data={0} exception={1} {2}'
                  .format(single_race_data.id, str(e), trace))
        easy_upload_record.errorenum = 2
        easy_upload_record.save()
        return

    # =======================================================================
    # Phase B) sanity check that there is a race, it has a trackname, and the same trackname.
    # =======================================================================
    # There must be at least 1 race.
    if (len(single_race_list) < 1):
        log.error('metric=UploadError type=No_Races_Found single_race_data=%s', single_race_data.id)
        easy_upload_record.errorenum = 3
        easy_upload_record.save()
        return

    # Check the first name of the list
    upload_trackname = single_race_list[0].trackName

    # We are going to force them to have a trackname already set.
    #     It makes this code so much simpler, if they need to change
    #     the trackname (then I can easily replace it and save the
    #     modified version).
    if (upload_trackname.strip() == ''):
        log.error('metric=UploadError type=TrackName_Missing single_race_data=%s', single_race_data.id)
        easy_upload_record.errorenum = 4
        easy_upload_record.save()
        return

    # Validate all the track names are the same.
    #     I don't think this would ever happen but I am going
    #     to check because I don't want people doing it.
    for race in single_race_list:
        if (race.trackName != upload_trackname):
            log.error('metric=UploadError type=TrackName_Missmatch single_race_data=%s', single_race_data.id)
            easy_upload_record.errorenum = 5
            easy_upload_record.save()
            return

    return single_race_list


def _final_validation_and_upload(result_page):
    '''
    Parameters
    ----------
    result_page : ResultPage
       Object that holds all the data for a single race being uploaded.
    '''
    # Process each race and load it into the DB.
    for single_race in result_page.single_race_list:
        # Set the new trackname on each of the race objects.
        single_race.trackName = result_page.upload_record.trackname.trackname

        try:
            single_race_details = create_single_race_details(single_race)

            # We are going to track who uploaded this race.
            EasyUploadedRaces.objects.create(upload=result_page.upload_record, racedetails=single_race_details)
            result_page.uploaded_race_list.append((single_race.raceClass, single_race_details.id))
            result_page.uploaded_raceid_list.append(single_race_details.id)

            # Celery task to queue up an outgoing email.
            mail_single_race.delay(single_race_details.id)

            # This is where we are going to queue up additional celery work, like if
            # we want to calculating ranking.

        except FileAlreadyUploadedError:
            log.error('metric=UploadError type=DuplicateUpload filename=%s', result_page.upload_record.filename)

            result_page.upload_record.errorenum = 6
            result_page.upload_record.save()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = traceback.format_exception(exc_type, exc_value, exc_traceback)

            log.error('metric=UploadError type=Exception_SingleRaceDetails file={0} exception={1} {2}'
                      .format(result_page.upload_record.filename, str(e), trace))

            result_page.upload_record.errorenum = 7
            result_page.upload_record.save()

    # TODO - push out and run in Celery so we wont wait forever here.

    # _update_ranking(track, uploaded_raceid_list)

    # Log this upload as processed (we do NOT want to support
    # multiple attempts at uploading the file).
    result_page.upload_record.processed = True
    result_page.upload_record.uploadfinish = timezone.now()
    result_page.upload_record.save()


def _parse_raw_upload_string(filename, raw_race_data_string):
    '''
    There a many possible scenarios that could cause this to fail,
    we want to record as much as possible so either the admin or
    the user can make a change and hopefully succeed.

    I expect that people will accidentally (hopefully) throw a number
    invalid files at this.

    Returns
    ----------
        List of SingleRace objects that have been parsed
    '''
    single_race_list = []
    currentRaceStartIndex = 0
    lastRace = ''

    # http://stackoverflow.com/questions/7472839/python-readline-from-a-string
    buf = io.StringIO(raw_race_data_string)
    content = buf.readlines()

    # Process the first race.
    for i in range(1, len(content)):

        # We have marked the start at 'currentRaceStartIndex' and we are looking for the
        # end of the race which we track with 'i'

        # We scan until we see something like this:
        #  Scoring Software by www.RCScoringPro.com                5:52:23 PM  04/27/2013
        #
        #                  TACOMA RC RACEWAY PRESENTS SHOWDOWN ROUND 7
        if (content[i].find('www.RCScoringPro.com') != -1):
            # This means we have found a new race in the file.

            # print '=' * 100
            # print content[currentRaceStartIndex:i]

            # This is a special check, if they have modified the race
            # manually, there will two results for the same race and
            # we want to take the second.
            if (lastRace == content[currentRaceStartIndex + 4]):
                currentRaceStartIndex = i
                continue

            single_race = RCScoringProTXTParser(filename, content[currentRaceStartIndex:i])
            single_race_list.append(single_race)

            lastRace = content[currentRaceStartIndex + 4]
            currentRaceStartIndex = i

    # This triggers when we have found the final race in the file.
    single_race = RCScoringProTXTParser(filename, content[currentRaceStartIndex:len(content)])
    single_race_list.append(single_race)

    return single_race_list


def _modify_trackname(single_race_data, origional_trackname, new_trackname):
    '''
    We want to store it based on the track name as it was uploaded, this
    is just for sanity down the road (if we need to upload from db records).

    We rely on the user to set the right trackname, since the one in the file
    is usually messed up.
    '''
    pattern = re.compile(re.escape(origional_trackname), re.IGNORECASE)
    modified_data_lines = []  # We are going to overwrite the existing trackname

    buf = io.StringIO(single_race_data.data)
    content = buf.readlines()

    for line in content:
        search_result = pattern.search(line)
        if (search_result):
            newline = ' ' * search_result.start(0)
            newline += new_trackname + '\n'
            modified_data_lines.append(newline)
        else:
            modified_data_lines.append(line)

    single_race_data.data = ''.join(modified_data_lines)
    single_race_data.save()
    return
