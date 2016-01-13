from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.plea.models import (UsageStats, Court,
                              Case, CaseAction,
                              CaseOffenceFilter,
                              CourtEmailCount,
                              Offence,
                              Result,
                              ResultOffence,
                              ResultOffenceData,
                              DataValidation)


class RegionalFilter(admin.SimpleListFilter):
    title = _('Region')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'region'

    def lookups(self, request, model_admin):
        codes = [(c.region_code, "{} - {}".format(c.region_code, c.court_name)) for c in Court.objects.all()]
        return codes

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(urn_entered__startswith=self.value())
        else:
            return queryset


class MatchFilter(admin.SimpleListFilter):
    title = _('Match')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'match'

    def lookups(self, request, model_admin):
        codes = [(True, "Yes"), (False, "No")]
        return codes

    def queryset(self, request, queryset):

        if self.value() is not None:
            v = True if self.value() == u"True" else False
            if v is True:
                return queryset.filter(case_match__isnull=False)
            elif v is False:
                return queryset.filter(case_match__isnull=True)
            else:
                return queryset
        else:
            return queryset


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


class InlineResultOffenceData(admin.StackedInline):
    model = ResultOffenceData
    extra = 0


class InlineResultOffence(admin.StackedInline):
    model = ResultOffence
    extra = 0
    inlines = [ResultOffenceData]


class CaseAdmin(admin.ModelAdmin):
    list_display = ("urn", "sent", "processed", "charge_count", "initiation_type")
    list_filter = ("sent", "processed", "initiation_type", "ou_code")
    inlines = [InlineCaseAction, InlineOffence]
    search_fields = ["urn", "case_number"]

    def charge_count(self, obj):
        return obj.offences.count()


class OffenceFilterAdmin(admin.ModelAdmin):
    list_display = ("filter_match", "description")
    search_fields = ("filter_match", "description")


class CourtEmailCountAdmin(admin.ModelAdmin):
    list_display = ("court", "date_sent", "initiation_type", "total_pleas", "total_guilty", "total_not_guilty", "hearing_date", "sent", "processed")
    model = CourtEmailCount


class ResultAdmin(admin.ModelAdmin):
    list_display = ("urn", "case_number", "ou_code", "sent", "sent_on")
    list_filter = ("ou_code", "sent", )
    inlines = [InlineResultOffence, ]
    search_fields = ["urn", "case_number"]


class DataValidationAdmin(admin.ModelAdmin):
    list_display = ("date_entered", "urn_entered", "case_match", "case_match_count")
    list_filter = (MatchFilter, RegionalFilter)


admin.site.register(UsageStats, UsageStatsAdmin)
admin.site.register(Court, CourtAdmin)
admin.site.register(CourtEmailCount, CourtEmailCountAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(CaseOffenceFilter, OffenceFilterAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(DataValidation, DataValidationAdmin)
