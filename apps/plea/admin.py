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
    INITIATION_TYPE_CHOICES,
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


class CaseInitiationTypeFilter(admin.SimpleListFilter):
    """Allow filtering Cases by Initiation type including compound views"""

    title = _('Initiation type')
    parameter_name = 'initiation_type'

    def lookups(self, request, model_admin):
        """Build a list of all initiation types mentioned by cases"""

        cases = Case.objects.all()

        # Return the initiation_type to use as a filter parameter and the name
        return list(set([
            (
                case.initiation_type,
                model_admin.model._get_initiation_type_choice(case)[1],
            )
            for case in cases
            if hasattr(case, "initiation_type")
        ])) + [(
            # Special case; compound filter
            "J|Q|S",
            "SJPs, requisitions and summons",
        )]

    def queryset(self, request, queryset):
        if self.value():
            # Compound queries (could be done programatically if needed)
            if self.value() == "J|Q|S":
                return queryset.filter(initiation_type="J") | \
                    queryset.filter(initiation_type="Q") | \
                    queryset.filter(initiation_type="S")

            # Filter on  particular initiation_type
            else:
                return queryset.filter(initiation_type=self.value())
        else:
            return queryset


class CaseAdmin(admin.ModelAdmin):
    list_display = ("urn", "sent", "processed", "charge_count", "initiation_type")
    list_filter = ("sent", "processed", CaseInitiationTypeFilter, "ou_code", "imported")
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


def x_by_y_from_z(x, y, z):
    """Return list of keys or attrs x from the y attr of each item in z"""
    retval = []
    for i in z:
        value = None
        if hasattr(i, y):
            iy = getattr(i, y)
            if iy is not None:
                if hasattr(iy, x):
                    value = getattr(iy, x)
                elif x in iy:
                    value = iy[x]
                retval.append(value)
    return set(retval)


class UrnFilter(admin.SimpleListFilter):
    """Allow filtering by URN from case or event_data"""

    title = _('URN')
    parameter_name = 'urn'

    def lookups(self, request, model_admin):
        """Build a list of all urns mentioned by auditevents"""

        # TODO: consider factoring out this iteration
        audit_events = AuditEvent.objects.all()
        urns_by_event_data = x_by_y_from_z("urn", "event_data", audit_events)
        urns_by_case = x_by_y_from_z("urn", "case", audit_events)

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
        else:
            return queryset


class AuditEventInitiationTypeFilter(admin.SimpleListFilter):
    """Allow filtering Audit events by Initiation type including compound views"""

    title = _('Initiation type')
    parameter_name = 'initiation_type'

    def lookups(self, request, model_admin):
        """Build a list of all initiation_types mentioned by auditevents"""
        audit_events = AuditEvent.objects.all()
        initiation_types_by_event_data = x_by_y_from_z(
            "initiation_type", "event_data", audit_events)
        initiation_types_by_case = x_by_y_from_z(
            "initiation_type", "case", audit_events)

        # Unique initiation_types for auditevents, with case initiation_types being preferred
        initiation_types = initiation_types_by_event_data
        initiation_types.update(initiation_types_by_case)

        # Return the initiation_type to use as a filter parameter and the name
        return list(set([
            (
                ae.case.initiation_type,
                ae._get_initiation_type_choice()[1],
            )
            for ae in audit_events
            if ae.case is not None and hasattr(ae.case, "initiation_type")
        ])) + [(
            # Special case; compound filter
            "J|Q|S",
            "SJPs, requisitions and summons",
        )]

    def queryset(self, request, queryset):
        if self.value():
            # Compound queries (could be done programatically if needed)
            if self.value() == "J|Q|S":
                return queryset.filter(case__initiation_type="J") | \
                    queryset.filter(case__initiation_type="Q") | \
                    queryset.filter(case__initiation_type="S") | \
                    queryset.filter(event_data__contains={'initiation_type': "J"}) | \
                    queryset.filter(event_data__contains={'initiation_type': "Q"}) | \
                    queryset.filter(event_data__contains={'initiation_type': "S"})

            # Filter on  particular initiation_type
            else:
                return queryset.filter(
                    case__initiation_type=self.value()
                ) | queryset.filter(
                    event_data__contains={
                        'initiation_type': self.value()
                    }
                )
        else:
            return queryset


class AuditEventAdmin(admin.ModelAdmin):
    """Audit events in the admin page"""

    list_display = (
        'id',
        'event_datetime',
        'event_subtype',
        'initiation_type',
        'case_link',
    )
    list_filter = (
        "event_type",
        "event_subtype",
        AuditEventInitiationTypeFilter,
        UrnFilter,
    )
    search_fields = ("case__urn", "event_data__urn")

    def initiation_type(self, auditevent):
        """Required for the admin_order_field"""
        itype = auditevent._get_initiation_type_choice()
        if itype is not None:
            return itype[1]

    def case_link(self, auditevent):
        """Display cases as links where possible"""
        if hasattr(auditevent, "case") and auditevent.case is not None:
            link = urlresolvers.reverse(
                "admin:plea_case_change",
                args=[auditevent.case.id],
            )
            return u'<a href="%s">%s</a>' % (link, auditevent.case.urn)
        else:
            return "No case"
    case_link.allow_tags = True

    initiation_type.admin_order_field = 'case__initiation_type'
    case_link.admin_order_field = 'case__id'

    def has_add_permission(self, request):
        return False


admin.site.register(UsageStats, UsageStatsAdmin)
admin.site.register(Court, CourtAdmin)
admin.site.register(CourtEmailCount, CourtEmailCountAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(CaseOffenceFilter, OffenceFilterAdmin)
admin.site.register(DataValidation, DataValidationAdmin)
admin.site.register(AuditEvent, AuditEventAdmin)
