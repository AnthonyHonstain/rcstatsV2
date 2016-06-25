
import logging
log = logging.getLogger('defaultlogger')

import sys  # TODO - Remove after testing
import random

from celery import shared_task

from core.celery_manager import mail_all_users
from core.celery_manager import pre_compute_king_of_the_hill

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
def pre_compute_koh(self, trackname_id):
    return pre_compute_king_of_the_hill(trackname_id)
