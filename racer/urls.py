from django.conf.urls import patterns, url

from racer import views

urlpatterns = [
    url(r'follow/track/(?P<track_id>\d+)/racerid/(?P<racerid_id>\d+)/$', views.follow, name='follow'),
    url(r'claim/track/(?P<track_id>\d+)/racerid/(?P<racerid_id>\d+)/$', views.claim, name='claim'),
]