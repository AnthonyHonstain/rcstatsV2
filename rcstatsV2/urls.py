from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = [
    url(r'^$', include('core.urls')),
    url(r'^results/', include('core.urls')),

    url(r'^upload/', include('uploadresults.urls')),
    url(r'^api/', include('raceAPI.urls')),

    url(r'^racer/', include('racer.urls')),

    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
