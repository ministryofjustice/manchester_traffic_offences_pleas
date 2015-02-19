from django.contrib import admin

from apps.plea.models import UsageStats, Case, CaseAction


class UsageStatsAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'online_submissions', 'postal_requisitions', 'postal_responses')
    list_editable = ('postal_requisitions', 'postal_responses')


class InlineCaseAction(admin.StackedInline):
    model = CaseAction
    extra = 0
    readonly_fields = ('date',)


class CaseAdmin(admin.ModelAdmin):
    list_display = ("urn", "name", "sent", "processed")
    inlines = [InlineCaseAction,]
    search_fields = ["urn"]


admin.site.register(UsageStats, UsageStatsAdmin)
admin.site.register(Case, CaseAdmin)