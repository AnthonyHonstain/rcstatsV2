from core.models import SingleRaceDetails, Racer, Track, SupportedTrack, OfficialClassNames, AliasClassNames, ClassEmailSubscription
from core.models import LapTimes

from core.database_cleanup import collapse_alias_classnames

from django.contrib import admin


def delete_selected_fast(modeladmin, request, queryset):
    queryset.delete()


class SingleRaceDetailsAdmin(admin.ModelAdmin):
    # fields = ['racedata', 'racedate']
    list_display = ('racedata', 'track', 'racedate', 'roundnumber', 'racenumber')
    list_filter = ['racedate', 'track']
    actions = (
        #collapse_alias_classnames, # TODO - need to
        delete_selected_fast,
        )


class LapTimesAdmin(admin.ModelAdmin):
    list_display = ('raceid', 'racer')
    fields = ['raceid', 'racer', 'racelap', 'raceposition', 'racelaptime']


class RacerAdmin(admin.ModelAdmin):
    fields = ['racerpreferredname']
    # Showing the pref name gives the admin useful info.
    list_display = ('racerpreferredname',)
    search_fields = ('racerpreferredname',)


class TrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


class SupportedTrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'track',)


class OfficialClassNamesAdmin(admin.ModelAdmin):
    list_display = ('raceclass', 'active')


class AliasClassNamesAdmin(admin.ModelAdmin):
    list_display = ('raceclass', 'officialclass')


class ClassEmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('raceclass', 'user', 'active', 'modified_date')


admin.site.register(SingleRaceDetails, SingleRaceDetailsAdmin)
admin.site.register(LapTimes, LapTimesAdmin)
admin.site.register(Racer, RacerAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(SupportedTrack, SupportedTrackAdmin)
admin.site.register(OfficialClassNames, OfficialClassNamesAdmin)
admin.site.register(AliasClassNames, AliasClassNamesAdmin)
admin.site.register(ClassEmailSubscription, ClassEmailSubscriptionAdmin)