from django.contrib import admin

from apps.plea.models import UsageStats

class UsageStatsAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'online_submissions', 'postal_requisitions', 'postal_responses')
    list_editable = ('postal_requisitions', 'postal_responses')

admin.site.register(UsageStats, UsageStatsAdmin)