from django.conf.urls import patterns, url, include
from rest_framework import routers
from raceAPI import views


router = routers.DefaultRouter()
router.register(r'Track', views.TrackList)
router.register(r'Track/(?P<track>.+)/SingleRaceDetails',
                views.SingleRaceDetailsByTrackList,
                base_name='singleracedetailsbytrack')
router.register(r'Track/(?P<track>.+)/SingleRaceDetailsSlim',
                views.SingleRaceDetailsSlimList,
                base_name='singleracedetailslim')

# Starting to clean up an provide generic endpoints for the API
router.register(r'Racer',
                views.RacerList,
                base_name='racer')
router.register(r'SingleRaceDetails',
                views.SingleRaceDetailsList,
                base_name='singleracedetails')
# TODO - starting with the laptimes, if this url structure is cleaner/more-organize
# than I should fix the race SingleRaceDetails and the SingleRaceDetailsSlim so
# that everything is more consistent.
router.register(r'Track/(?P<track>.+)/SingleRaceDetails/(?P<singleracedetails>.+)/LapTimes',
                views.LapTimesList,
                base_name='laptimes')


urlpatterns = [
    url(r'^', include(router.urls)),
]
