from django.shortcuts import render

from userena import views as userena_views

import logging
logger = logging.getLogger('defaultlogger')


def rcstats_signin(request):
    # do stuff before userena signin view is called

    # call the original view
    response = userena_views.signin(request)

    # This is just meant to be an initial attempt at tracking how often people
    # are signing in using the logs, alternatively I could probably get this same
    # information via google analytics or forking userena.
    if request.method == 'POST':
        logger.debug('metric=singin_attempt identification=%s', request.POST['identification'])

    # do stuff after userena signin view is done

    # return the response
    return response
