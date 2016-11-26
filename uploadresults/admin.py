from uploadresults.models import EasyUploaderPrimaryRecord, EasyUploadRecord, EasyUploadedRaces, SingleRaceData
from django.contrib import admin


class EasyUploadRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ip', 'track', 'filename', 'filesize', 'filemd5', 'uploadstart', 'errorenum')
    list_filter = ['user', 'ip', 'track']
    ordering = ('-uploadstart',)


class EasyUploadedRacesAdmin(admin.ModelAdmin):
    list_display = ('upload', 'get_track', 'get_racedata', 'get_racedate', 'racedetails')

    # http://stackoverflow.com/questions/163823/can-list-display-in-a-django-modeladmin-display-attributes-of-foreignkey-field
    def get_track(self, obj):
        return '%s' % (obj.racedetails.track)
    get_track.short_description = 'Track'

    def get_racedata(self, obj):
        return '%s' % (obj.racedetails.racedata)
    get_racedata.short_description = 'ClassName'

    def get_racedate(self, obj):
        return '%s' % (obj.racedetails.racedate)
    get_racedate.short_description = 'Date'


class SingleRaceDataInline(admin.StackedInline):
    # https://docs.djangoproject.com/en/1.7/ref/contrib/admin/#inlinemodeladmin-objects
    model = SingleRaceData
#     max_num = 1


class SingleRaceDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'ip', 'track', 'filename', 'created')


class EasyUploaderPrimaryRecordAdmin(admin.ModelAdmin):
    inlines = [SingleRaceDataInline]
    list_display = ('id', 'user', 'ip', 'track', 'filecount', 'filecountsucceed', 'uploadstart')
    list_filter = ['user', 'ip', 'track']
    ordering = ('-uploadstart',)


admin.site.register(EasyUploaderPrimaryRecord, EasyUploaderPrimaryRecordAdmin)
admin.site.register(EasyUploadRecord, EasyUploadRecordAdmin)
admin.site.register(EasyUploadedRaces, EasyUploadedRacesAdmin)

admin.site.register(SingleRaceData, SingleRaceDataAdmin)
