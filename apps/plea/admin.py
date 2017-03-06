from __future__ import division

from datetime import date, timedelta
from functools import update_wrapper

from django.core import urlresolvers
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q

from apps.plea.models import (
    AuditEvent,
    Court,
    Case,
    CaseAction,
    CaseOffenceFilter,
    CourtEmailCount,
    DataValidation,
    Offence,
    OUCode,
    UsageStats,
)


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


class InlineOUCode(admin.StackedInline):
    model = OUCode
    extra = 1


class CourtAdmin(admin.ModelAdmin):
    list_display = ('court_name', 'region_code', 'court_address', 'court_email', 'plp_email', 'ou_codes',
                    'enabled', 'test_mode', 'notice_types', 'validate_urn', 'display_case_data')

    inlines = (InlineOUCode,)

    def ou_codes(self, obj):

        return ", ".join(x.ou_code for x in obj.oucode_set.all())


class InlineCaseAction(admin.TabularInline):
    model = CaseAction
    extra = 0
    readonly_fields = ('date',)


class InlineOffence(admin.StackedInline):
    model = Offence
    extra = 0


class CaseAdmin(admin.ModelAdmin):
    list_display = ("urn", "sent", "processed", "charge_count", "initiation_type")
    list_filter = ("sent", "processed", "initiation_type", "ou_code", "imported")
    inlines = [InlineCaseAction, InlineOffence]
    search_fields = ["urn", "case_number"]
    readonly_fields = ('created',)

    def charge_count(self, obj):
        return obj.offences.count()


class OffenceFilterAdmin(admin.ModelAdmin):
    list_display = ("filter_match", "description")
    search_fields = ("filter_match", "description")


class CourtEmailCountAdmin(admin.ModelAdmin):
    list_display = ("court", "date_sent", "initiation_type", "total_pleas", "total_guilty", "total_not_guilty", "hearing_date", "sent", "processed")
    model = CourtEmailCount


class DataValidationAdmin(admin.ModelAdmin):
    list_display = ("date_entered", "urn_entered", "case_match", "case_match_count")
    list_filter = (MatchFilter, RegionalFilter)

    statistics_template = "admin/statistics.html"
    change_list_template = "admin/datavalidation_change_list.html"

    def get_urls(self):
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urls = patterns(
            '',
            url(
                r'^statistics/$',
                wrap(self.statistics_view),
                name='%s_%s_statistics' % info
            ),
        )

        super_urls = super(DataValidationAdmin, self).get_urls()

        return urls + super_urls

    def statistics_view(self, request):
        default_recent = 30
        try:
            recent_days = int(request.GET.get("days", default_recent))
            if recent_days < 1:
                recent_days = default_recent
        except ValueError:
            recent_days = default_recent

        regions = []
        court_codes = []
        for court in Court.objects.all():
            court_codes.append(court.region_code)
            dv = DataValidation.objects.filter(urn_entered__startswith=court.region_code,
                                               date_entered__lte=date.today() - timedelta(days=recent_days))
            all_total = dv.count()
            all_matched = dv.filter(case_match_count__gt=0).count()

            if all_total > 0:
                all_percentage = round(all_matched / all_total * 100, 2)
            else:
                all_percentage = 0

            dv_recent = DataValidation.objects.filter(urn_entered__startswith=court.region_code,
                                                      date_entered__gt=date.today() - timedelta(days=recent_days))
            recent_total = dv_recent.count()
            recent_matched = dv_recent.filter(case_match_count__gt=0).count()
            if recent_total > 0:
                recent_percentage = round(recent_matched / recent_total * 100, 2)
            else:
                recent_percentage = 0

            change_percentage = recent_percentage - all_percentage
            if change_percentage > 0:
                change_percentage = "+ {}".format(change_percentage)
            else:
                change_percentage = "{}".format(change_percentage)

            if all_total > 0:
                reg = {"name": court.court_name,
                       "all_total": all_total,
                       "all_matched": all_matched,
                       "all_percentage": all_percentage,
                       "recent_total": recent_total,
                       "recent_matched": recent_matched,
                       "recent_percentage": recent_percentage,
                       "change_percentage": change_percentage}
                regions.append(reg)

        return render_to_response(self.statistics_template, {
            'title': 'Data Validation Statistics',
            'opts': self.model._meta,
            'recent_days': recent_days,
            'regions': regions
        }, context_instance=RequestContext(request))


class UrnFilter(admin.SimpleListFilter):
    """Allow filtering by URN from case or event_data"""

    title = _('URN')
    parameter_name = 'urn'

    def lookups(self, request, model_admin):
        """Build a list of all urns mentioned by auditevents"""

        # TODO: consider factoring out this iteration
        urns_by_case = {
            a.case.urn
            for a in AuditEvent.objects.all()
            if hasattr(a, "case") and hasattr(a.case, "urn")
        }
        urns_by_event_data = {
            a.event_data["urn"]
            for a in AuditEvent.objects.all()
            if hasattr(a, "event_data") and "urn" in a.event_data
        }

        # Unique urns for auditevents, with case urns being preferred
        urns = urns_by_event_data
        urns.update(urns_by_case)

        # Return the urn to use as a filter parameter and the name
        return [
            (u, u)
            for u in urns
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                case__urn=self.value()
            ) | queryset.filter(
                event_data__contains={
                    'urn': self.value()
                }
            )
            #event_data__urn=self.value())
        else:
            return queryset


class AuditEventAdmin(admin.ModelAdmin):
    """Audit events in the admin page"""

    list_display = (
        'urn',
        'event_datetime',
        'event_subtype',
        'case_link',
    )
    list_filter = (
        "event_type",
        "event_subtype",
        UrnFilter,

    )
    search_fields = ("case__urn", "event_data__urn")

    def case_link(self, obj):
        """Display cases as links"""
        if hasattr(obj, "case") and obj.case is not None:
            link = urlresolvers.reverse(
                "admin:plea_case_change",
                args=[obj.case.id],
            )
            return u'<a href="%s">%s</a>' % (link, obj.case.urn)
        else:
            return "No case"
    case_link.allow_tags = True

    def has_add_permission(self, request):
        return False

admin.site.register(UsageStats, UsageStatsAdmin)
admin.site.register(Court, CourtAdmin)
admin.site.register(CourtEmailCount, CourtEmailCountAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(CaseOffenceFilter, OffenceFilterAdmin)
admin.site.register(DataValidation, DataValidationAdmin)
admin.site.register(AuditEvent, AuditEventAdmin)
