from django.contrib import admin

from apps.plea.models import UsageStats, Court, Case, CaseAction, CourtEmailCount, Offence


class UsageStatsAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'online_submissions', 'postal_requisitions', 'postal_responses')
    list_editable = ('postal_requisitions', 'postal_responses')


class CourtAdmin(admin.ModelAdmin):
    list_display = ('court_code', 'region_code', 'court_name', 'court_address',
                    'court_telephone', 'court_email', 'submission_email',
                    'enabled', 'test_mode')


class InlineCaseAction(admin.StackedInline):
    model = CaseAction
    extra = 0
    readonly_fields = ('date',)


class InlineOffence(admin.StackedInline):
    model = Offence
    extra = 0


class CaseAdmin(admin.ModelAdmin):
    list_display = ("urn", "name", "sent", "processed", "charge_count")
    inlines = [InlineCaseAction, InlineOffence]
    search_fields = ["urn"]

    def charge_count(self, obj):
        return obj.offences.count()


class CourtEmailCountAdmin(admin.ModelAdmin):
    list_display = ("court", "total_pleas", "total_guilty", "total_not_guilty", "hearing_date", "sent", "processed")
    model = CourtEmailCount


admin.site.register(UsageStats, UsageStatsAdmin)
admin.site.register(Court, CourtAdmin)
admin.site.register(CourtEmailCount, CourtEmailCountAdmin)
admin.site.register(Case, CaseAdmin)
