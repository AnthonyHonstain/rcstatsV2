r'''
Requirements - Python3, Python for Windows extensions http://sourceforge.net/projects/pywin32/
Windows logging - http://stackoverflow.com/questions/1067531/are-there-any-log-file-about-windows-services-status

Usage : python aservice.py install (or / then start, stop, remove, update)

Tail the logs in powershell
    Get-Content -Path .\rcstats_upload.log -Wait
    Get-Content -Path "C:\Python34\Lib\site-packages\win32\rcstats_upload.log" -Wait

Records are stored in a sqlite database DB_CONN
    SUCCESS
        "3" "C:\Users\Anthony\Desktop\testfolder\race_1_16\Round1.txt" "1" "2" "1"
    FAIL ON FIRST TRY
        "5" "C:\Users\Anthony\Desktop\testfolder\race_2_15\Round3.txt" "0" "2" "1"
    FAIL ON SECOND TRY
        "5" "C:\Users\Anthony\Desktop\testfolder\race_2_15\Round3.txt" "0" "1" "2"
    FAIL ON FINAL TRY
        "5" "C:\Users\Anthony\Desktop\testfolder\race_2_15\Round3.txt" "0" "0" "3"
    SUCCESS ON FINAL TRY
        "7" "C:\Users\Anthony\Desktop\testfolder\race_2_15\Round4.txt" "1" "0" "3"


Helpful tools:
    * http://sqlitebrowser.org/ to check status of database.
'''

import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import os, sys, string, time

import pathlib
import sqlite3
from urllib import request
import json
from pprint import pprint
from collections import namedtuple
from datetime import datetime
import time
import traceback
import re
import logging

logging.basicConfig(level=logging.NOTSET)

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
handler = logging.FileHandler('rcstats_upload.log')
handler.setFormatter(formatter)
logger.addHandler(handler)

#UPLOAD_URL = 'http://192.168.110.129:8000/upload/single_race_upload/'
UPLOAD_URL = 'http://nameless-ridge-5720.herokuapp.com/upload/single_race_upload/'
REGEX_ROUND_FILE = re.compile('Round.\.txt$')
TEST_DIRECTORY = r'C:\Users\Anthony\Desktop\testfolder'
MAX_ALLOWED_RETRY = 3
RETRY_WAIT_TIME_SECONDS = 3600
DB_FILENAME = 'rcstats_upload.db'
DB_CONN = sqlite3.connect(DB_FILENAME)

Upload = namedtuple('Upload', ['filename', 'success', 'retry', 'attemptcount', 'created', 'lastattempt'])


def initialize():
    logger.info('Check database')

    db_cursor = DB_CONN.cursor()
    table_check_result = db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='upload'")
    table = table_check_result.fetchone()
    db_cursor.close()

    if (not table):
        # Create Table
        logger.info('Initialize upload table %s', DB_FILENAME)
        DB_CONN.execute('CREATE TABLE upload (filename text, success integer, retry integer, '
                        'attemptcount integer, created date, lastattempt date)')
        DB_CONN.commit()

    # Cleanup
    #DB_CONN.execute('DROP TABLE upload')
    #DB_CONN.commit()


def get_all_uploads():
    db_cursor = DB_CONN.cursor()
    file_records = {}
    for row in db_cursor.execute('SELECT * FROM upload'):
        # Example time from the database (datetime is stored as string field)
        # '2015-03-14 20:10:18.180030'
        upload_row = Upload(row[0], row[1], row[2], row[3],
                            datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S.%f'),
                            datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S.%f'))
        file_records[upload_row.filename] = upload_row
    db_cursor.close()
    return file_records


def get_upload_record(file_name):
    db_cursor = DB_CONN.cursor()
    db_cursor.execute('SELECT * FROM upload WHERE filename=?', (file_name,))
    row = db_cursor.fetchone()
    db_cursor.close()
    return Upload(*row)


def new_upload_record(file_name):
    DB_CONN.execute('INSERT INTO upload VALUES (?,?,?,?,?,?)',
                    (file_name, 0, MAX_ALLOWED_RETRY, 0, datetime.utcnow(), datetime.utcnow()))
    DB_CONN.commit()
    return get_upload_record(file_name)


def update_success(upload_record):
    DB_CONN.execute('UPDATE upload SET success = 1, retry = ?, attemptcount = ?, lastattempt = ? WHERE filename=?',
                    (upload_record.retry - 1, upload_record.attemptcount + 1, datetime.utcnow(), upload_record.filename,))
    DB_CONN.commit()
    return get_upload_record(upload_record.filename)


def update_fail(upload_record):
    DB_CONN.execute('UPDATE upload SET success = 0, retry = 0, attemptcount = ? WHERE filename=?',
                    (upload_record.attemptcount + 1, upload_record.filename,))
    DB_CONN.commit()
    return get_upload_record(upload_record.filename)


def update_retry(upload_record):
    # We must prevent the system from retrying for ever.
    if current_upload_record.attemptcount >= MAX_ALLOWED_RETRY - 1:
        return update_fail(upload_record)

    DB_CONN.execute('UPDATE upload SET success = 0, retry = ?, attemptcount = ?, lastattempt = ? WHERE filename=?',
                    (upload_record.retry - 1, upload_record.attemptcount + 1, datetime.utcnow(), upload_record.filename,))
    DB_CONN.commit()
    return get_upload_record(upload_record.filename)

# -------------------------------------------------------------------------------


def get_all_files(starting_path):
    # Look to the file system
    possible_files = set()
    for path, subdirs, files in os.walk(starting_path):
        for name in files:
            if REGEX_ROUND_FILE.match(name):
                possible_files.add(str(pathlib.PurePath(path, name)))
                #print(name, pathlib.PurePath(path, name))
            else:
                #print('IGNORING', str(pathlib.PurePath(path, name)))
                pass
    #print()
    #print('SET')
    #pprint(possible_files)
    return possible_files


def load_file(file_name):
    race_text = ''
    with open(file_name, 'r') as f:
        race_text = f.read()
    return race_text


def upload_to_api(filename, race_txt):
    # Construct the json data to POST
    json_dict = {'trackname': 1, 'filename':filename, 'data':race_txt}
    json_data = json.dumps(json_dict)
    post_data = json_data.encode('utf-8')

    headers = {}
    headers['Content-Type'] = 'application/json;charset=UTF-8'

# TODO - come up with a better scheme for setting creds.
headers['Authorization'] = FIX ME

    # now do the request for a url
    req = request.Request(UPLOAD_URL, post_data, headers=headers)

    # send the request
    start = time.time()
    try:
        res = request.urlopen(req)
        response_code = res.getcode()
        res.close()
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(tb)
        response_code = 502

    logger.debug('HTTP Response code %d for duration %s - site: %s',
                 response_code, time.time() - start, UPLOAD_URL)

    return response_code


def upload_file(current_upload_record):
    race_txt = load_file(current_upload_record.filename)

    response_code = upload_to_api(current_upload_record.filename, race_txt)
    if 200 <= response_code < 300:
        new_record = update_success(current_upload_record)
    elif 500 <= response_code < 600:
        new_record = update_retry(current_upload_record)
    else:
        new_record = update_fail(current_upload_record)
    return new_record


def find_and_process_race_files():
    '''
    The main logic to find files we want to consider uploading, and then attempt
    the upload if appropriate.
    '''
    initialize()

    # Get an in-memory set of all the files from the db.
    file_records = get_all_uploads()
    # Dump out the database records.
    #pprint(list(file_records.keys()))
    #pprint(list(file_records.values()))

    possible_files = get_all_files(TEST_DIRECTORY)

    new_upload_count = 0
    retry_count = 0

    logger.info('Starting processing - considering %d files against %d known files', len(possible_files), len(file_records))
    # If the file is not in the db we want to attempt upload and persist it.
    files_to_upload = {}
    for file_name in possible_files:
        if file_name in file_records:
            if not file_records[file_name].success:
                logger.info('Retry: %s', file_name)
                current_upload_record =  file_records[file_name]

                # We only retry once an hour to try and give the server a chance to recover
                diff = datetime.utcnow() - current_upload_record.lastattempt

                if (current_upload_record.retry and diff.seconds >= RETRY_WAIT_TIME_SECONDS):
                    updated_upload_record = upload_file(current_upload_record)
                    logger.info('Retry: %r', str(updated_upload_record))
                    file_records[updated_upload_record.filename] = updated_upload_record
                    retry_count += 1
                else:
                    logger.info('Not attempting retry: %s', file_name)
            else:
                # File already finished.
                #logger.info('Skip: %s', file_name)
                pass
        else:
            logger.info('New: %s', file_name)
            # We are going to insert the race prior to attempting the upload
            # so we have an acurate record of attempts if it totally falls down.
            file_records[file_name] = new_upload_record(file_name)
            current_upload_record = file_records[file_name]

            updated_upload_record = upload_file(current_upload_record)
            logger.info('New record: %r', str(updated_upload_record))
            file_records[updated_upload_record.filename] = updated_upload_record
            new_upload_count += 1

    logger.info('Finished processing - new uploads:%d retry attempts:%d', new_upload_count, retry_count)

class aservice(win32serviceutil.ServiceFramework):
    '''
    Main python windows service class, responsible for start, stop, run functionality.
    '''

    _svc_name_ = 'RaceUploader'
    _svc_display_name_ = 'Race uploader by Anthony Honstain'
    _svc_description_ = 'Retrieve race data and upload it to web server.'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))

        self.timeout = 640000  # 640 seconds / 10 minutes (value is in milliseconds)
        #self.timeout = 120000  # 120 seconds / 2 minutes
        #self.timeout = 12000
        # This is how long the service will wait to run / refresh itself (see script below)
        logger.info('RaceUplaoder - STARTING')
        while 1:
            # Wait for service stop signal, if I timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal encountered
                logger.info('RaceUplaoder - STOPPED!')
                servicemanager.LogInfoMsg('RaceUploader - STOPPED!')  # For Event Log
                break
            else:
                try:
                    logger.info('RaceUploader - start work')
                    find_and_process_race_files()
                except Exception as e:
                    tb = traceback.format_exc()
                    logger.error(tb)
                    servicemanager.LogInfoMsg('RaceUploader - exception:', e)


def ctrlHandler(ctrlType):
    return True


if __name__ == '__main__':
    # You need these to start/stop/remove etc.
    win32api.SetConsoleCtrlHandler(ctrlHandler, True)
    win32serviceutil.HandleCommandLine(aservice)

    # Toggle for Local testing
    #find_and_process_race_files()
