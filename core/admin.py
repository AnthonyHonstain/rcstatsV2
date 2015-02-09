from core.models import SingleRaceDetails, RacerId, TrackName, SupportedTrackName, OfficialClassNames, AliasClassNames

from django.contrib import admin


class SingleRaceDetailsAdmin(admin.ModelAdmin):
    # fields = ['racedata', 'racedate']
    list_display = ('racedata', 'trackkey', 'racedate', 'roundnumber', 'racenumber')
    list_filter = ['racedate', 'trackkey']
    # actions = [collapse_alias_classnames] # TODO - excluding from initial port


'''
LapTimesAdmin is disabled for now, I think there is to much data here to
expose it in a useful way in the admin (500k rows..)
'''
# class LapTimesAdmin(admin.ModelAdmin):
#    fields = ['raceId', 'racerId', 'raceLap', 'raceLapTime']


class RacerIdAdmin(admin.ModelAdmin):
    fields = ['racerpreferredname']
    # Showing the pref name gives the admin useful info.
    list_display = ('racerpreferredname',)
    search_fields = ('racerpreferredname',)


class TrackNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'trackname',)


class SupportedTrackNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'trackkey',)


class OfficialClassNamesAdmin(admin.ModelAdmin):
    list_display = ('raceclass',)


class AliasClassNamesAdmin(admin.ModelAdmin):
    list_display = ('raceclass', 'officialclass')


admin.site.register(SingleRaceDetails, SingleRaceDetailsAdmin)
# admin.site.register(LapTimes, LapTimesAdmin)
admin.site.register(RacerId, RacerIdAdmin)
admin.site.register(TrackName, TrackNameAdmin)
admin.site.register(SupportedTrackName, SupportedTrackNameAdmin)
admin.site.register(OfficialClassNames, OfficialClassNamesAdmin)
admin.site.register(AliasClassNames, AliasClassNamesAdmin)
