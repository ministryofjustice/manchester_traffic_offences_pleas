from django.contrib import admin

from apps.plea.models import UsageStats, Court


class UsageStatsAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'online_submissions', 'postal_requisitions', 'postal_responses')
    list_editable = ('postal_requisitions', 'postal_responses')


class CourtAdmin(admin.ModelAdmin):
    list_display = ('court_code', 'region_code', 'court_name', 'court_address',
                    'court_telephone', 'court_email', 'submission_email',
                    'enabled', 'test_mode')


admin.site.register(UsageStats, UsageStatsAdmin)
admin.site.register(Court, CourtAdmin)