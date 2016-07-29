from django.conf.urls import patterns, include, url

from accounts import views

urlpatterns = [
    url(r'signin/$', views.rcstats_signin, name='userena_signin'),
    url(r'^', include('userena.urls')),
]
