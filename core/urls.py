from django.conf.urls import patterns, url

from core import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'singleracedetail/(?P<single_race_detail_id>\d+)/$', views.single_race_details, name='results-singleracedetail'),
)
