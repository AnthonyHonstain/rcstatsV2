from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.models import TrackName, RacerId
from racer.models import Follow

from django import forms


import logging
logger = logging.getLogger('defaultlogger')


@login_required
def follow_claim_list(request):
    '''

    TODO - in the future you might need to add another page so that can interact
    with a single track at a time. Adding tracks seems pretty slow/unlikely at this 
    stage so I am going to optimize for dev velocity.
    '''

    racerid_and_counts = RacerId.objects.all()\
      .order_by('racerpreferredname')


#class FollowForm(forms.Form):
#	active = forms.BooleanField()
class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ['active']


@login_required()
def follow(request, track_id, racerid_id):
    '''
	All a user to modify the following behavior for a specific racer.
    '''
    logger.debug('metric=follow track=%s racer=%s user=%d method=%s', 
    	track_id, racerid_id, request.user.id, request.method);

    trackname = get_object_or_404(TrackName, pk=track_id)
    racerId = get_object_or_404(RacerId, pk=racerid_id)

    if request.method == 'POST':
        form = FollowForm(request.POST)

        if form.is_valid():
            form_dict = form.cleaned_data
            # We are just looking to have upsert behavior on the 'active' column
            follow_obj, created = Follow.objects.get_or_create(
                user=request.user,
                racerId=racerId)

            follow_obj.active = form_dict['active']
            follow_obj.save()

            logger.debug('metric=newFollow track=%d racer=%s user=%d username=%s', 
                trackname.id, racerid_id, request.user.id, request.user.username)

            return redirect('/')
    else:
        try:
            old_follow = Follow.objects.get(user__exact=request.user, racerId__exact=racerId)
        except Follow.DoesNotExist:
            old_follow = None
        form = FollowForm(instance=old_follow)

    return render(request, 'follow.html', {'form': form, 'trackname': trackname, 'racerId': racerId});


@login_required()
def claim(request, track_id, racerid_id):
	return render(request, 'claim.html', {'form': form});