from core.models import SingleRaceDetails, RacerId, TrackName, SupportedTrackName, OfficialClassNames, AliasClassNames, ClassEmailSubscription
from core.models import LapTimes

from django.contrib import admin


def delete_selected_fast(modeladmin, request, queryset):
    queryset.delete()


class SingleRaceDetailsAdmin(admin.ModelAdmin):
    # fields = ['racedata', 'racedate']
    list_display = ('racedata', 'trackkey', 'racedate', 'roundnumber', 'racenumber')
    list_filter = ['racedate', 'trackkey']
    # actions = [collapse_alias_classnames] # TODO - excluding from initial port
    actions = (delete_selected_fast,)


class LapTimesAdmin(admin.ModelAdmin):
    list_display = ('raceid', 'racerid')
    fields = ['raceid', 'racerid', 'racelap', 'raceposition', 'racelaptime']


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


class ClassEmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('raceclass', 'user', 'active', 'modified_date')


admin.site.register(SingleRaceDetails, SingleRaceDetailsAdmin)
admin.site.register(LapTimes, LapTimesAdmin)
admin.site.register(RacerId, RacerIdAdmin)
admin.site.register(TrackName, TrackNameAdmin)
admin.site.register(SupportedTrackName, SupportedTrackNameAdmin)
admin.site.register(OfficialClassNames, OfficialClassNamesAdmin)
admin.site.register(AliasClassNames, AliasClassNamesAdmin)
admin.site.register(ClassEmailSubscription, ClassEmailSubscriptionAdmin)