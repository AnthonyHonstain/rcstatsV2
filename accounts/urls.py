from django.conf.urls import patterns, include, url

from accounts import views

urlpatterns = patterns(
    '',
    (r'^', include('userena.urls')),
)
