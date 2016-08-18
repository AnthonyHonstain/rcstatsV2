
import logging
log = logging.getLogger('defaultlogger')

import sys  # TODO - Remove after testing
import random

from celery import shared_task

from core.celery_manager import mail_all_users
from core.celery_manager import find_king_of_the_hill_classes
from core.celery_manager import compute_koh_by_track_class

'''
The general architecture here is that the tasks defined and managed here, but all the
heavy lifting is implemented and tested in another module.

So we can work and test the outgoing email logic without having to think very much 
about the celery job and the external dependencies that make the whole system dance.
'''

@shared_task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    sys.stdout.flush()  # TODO - Remove after testing
    return random.randint(0, 100)


@shared_task(bind=True)
def mail_single_race(self, single_race_details_id):
    mail_all_users(single_race_details_id)
    return


@shared_task(bind=True)
def pre_compute_koh(self):
	# We want a list of all tracks and classe (tuple) to consider
    track_and_class_list = find_king_of_the_hill_classes()

    # Spawn new tasks, alternatively we could organize this into
    # a celery Group http://docs.celeryproject.org/en/master/userguide/canvas.html#groups
    # but I am not convinced of the value (other than possibly doing
    # away with this gross list of tuples)
    for trackname_id, official_class_name_id in track_and_class_list:
        koh_track_class_task.delay(trackname_id, official_class_name_id)
        return


@shared_task(bind=True)
def koh_track_class_task(self, trackname_id, official_class_name_id):
    return compute_koh_by_track_class(trackname_id, official_class_name_id)
