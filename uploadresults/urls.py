from django.conf.urls import patterns, url, include
from rest_framework import routers
from uploadresults import views


router = routers.DefaultRouter()
router.register(r'EasyUploaderPrimaryRecord', views.EasyUploaderPrimaryRecordViewSet)
router.register(r'EasyUploadRecord', views.EasyUploadRecordViewSet)
router.register(r'TrackNameList', views.TrackNameList)


urlpatterns = [
    url(r'^easyupload_track/$', views.easyupload_track, name="easyupload_track"),
    url(r'^easyupload_fileselect/(?P<track_id>\d+)/$', views.easyupload_fileselect, name="easyupload_fileselect"),
    url(r'^easyupload_results/(?P<upload_id>\d+)/$', views.easyupload_results, name="easyupload_results"),


    url(r'^single_race_upload/$', views.SingleRaceDataCreate.as_view()),
    url(r'^single_race_upload_detail/(?P<pk>[0-9]+)/$', views.SingleRaceDataDetail.as_view()),
    url(r'^', include(router.urls)),

    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
