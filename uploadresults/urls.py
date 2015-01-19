from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^easyupload_track/$', 'uploadresults.views.easyupload_track', name="easyupload_track"),
    url(r'^easyupload_fileselect/(?P<track_id>\d+)/$', 'uploadresults.views.easyupload_fileselect', name="easyupload_fileselect"),
    url(r'^easyupload_results/(?P<upload_id>\d+)/$', 'uploadresults.views.easyupload_results', name="easyupload_results"),
)
