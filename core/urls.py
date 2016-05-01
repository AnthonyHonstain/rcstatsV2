from django.conf.urls import patterns, url

from core import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'singleracedetail/(?P<single_race_detail_id>\d+)/$', views.single_race_details, name='results-singleracedetail'),
    url(r'racer-list/(?P<track_id>\d+)/$', views.racer_list, name='racer-list-by-track'),
    url(r'racer-list/(?P<track_id>\d+)/racerid/(?P<racerid_id>\d+)/$', views.single_racer_race_list, name='single_racer_race_list'),
    url(r'race-emails/$', views.race_emails, name='race-emails'),
    url(r'king-of-the-hill/(?P<track_id>\d+)/$', views.king_of_the_hill_summary, name='koh-summary'),
)
