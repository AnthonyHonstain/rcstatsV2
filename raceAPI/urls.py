from django.conf.urls import patterns, url, include
from rest_framework import routers
from raceAPI import views


router = routers.DefaultRouter()
router.register(r'TrackName', views.TrackNameList)
router.register(r'TrackName/(?P<trackname>.+)/SingleRaceDetails',
                views.SingleRaceDetailsList,
                base_name='singleracedetail')

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
