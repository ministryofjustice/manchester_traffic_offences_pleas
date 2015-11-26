from django.contrib import admin

from apps.plea.models import UsageStats, Court, Case, CaseAction, CourtEmailCount, Offence, DataValidation


class UsageStatsAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'online_submissions', 'postal_requisitions', 'postal_responses')
    list_editable = ('postal_requisitions', 'postal_responses')


class CourtAdmin(admin.ModelAdmin):
    list_display = ('court_name', 'region_code', 'court_address', 'court_email', 'plp_email',
                    'enabled', 'test_mode', 'notice_types')


class InlineCaseAction(admin.TabularInline):
    model = CaseAction
    extra = 0
    readonly_fields = ('date',)


class InlineOffence(admin.StackedInline):
    model = Offence
    extra = 0


class CaseAdmin(admin.ModelAdmin):
    list_display = ("urn", "sent", "processed", "charge_count", "initiation_type")
    inlines = [InlineCaseAction, InlineOffence]
    search_fields = ["urn", "name"]

    def charge_count(self, obj):
        return obj.offences.count()


class CourtEmailCountAdmin(admin.ModelAdmin):
    list_display = ("court", "date_sent", "initiation_type", "total_pleas", "total_guilty", "total_not_guilty", "hearing_date", "sent", "processed")
    model = CourtEmailCount


class DataValidationAdmin(admin.ModelAdmin):
    list_display = ("date_entered", "urn_entered", "case_match", "case_match_count")


admin.site.register(UsageStats, UsageStatsAdmin)
admin.site.register(Court, CourtAdmin)
admin.site.register(CourtEmailCount, CourtEmailCountAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(DataValidation, DataValidationAdmin)
