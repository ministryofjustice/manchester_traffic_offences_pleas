from __future__ import division

from datetime import date, timedelta
from functools import update_wrapper

from django.core import urlresolvers
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.template import RequestContext
from django.db.models import Count, When, IntegerField, Q
from django.db.models import Case as case2
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
    CaseTracker,
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
    list_display = (
        'court_name', 'region_code', 'court_address', 'court_email',
        'plp_email', 'ou_codes', 'enabled', 'test_mode', 'notice_types',
        'validate_urn', 'display_case_data')

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

    title = 'Initiation type'
    parameter_name = 'initiation_type'

    def lookups(self, request, model_admin):

        return list(INITIATION_TYPE_CHOICES) + [(
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
    list_filter = ("sent", "processed", "ou_code", "imported", "language", "completed_on", CaseInitiationTypeFilter)
    inlines = [InlineCaseAction, InlineOffence]
    search_fields = ["urn", "case_number", "name", "extra_data"]
    readonly_fields = ('created',)
    initial_report_template = "admin/case_initial_report.html"
    ongoing_report_template = "admin/case_ongoing_report.html"
    change_list_template = "admin/case_change_list.html"

    def charge_count(self, obj):
        return obj.offences.count()

    def get_queryset(self, request):
        case_model = super(CaseAdmin, self).get_queryset(request)
        case_model = case_model.prefetch_related('offences')
        return case_model

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urls = [
            url(
                r'^initial_report/$',
                wrap(self.initial_report_view),
                name='%s_%s_initial_report' % info
            ),
            url(
                r'^ongoing_report/$',
                wrap(self.ongoing_report_view),
                name='%s_%s_ongoing_report' % info
            ),
        ]

        super_urls = super(CaseAdmin, self).get_urls()

        return urls + super_urls

    def initial_report_view(self, request):
        cutoff_date = date(2017,7,31)
        case_month_data = Case.objects.filter(completed_on__isnull=False).filter(completed_on__lte=cutoff_date)\
            .extra(select={'month': "EXTRACT(month FROM completed_on)",'year': "EXTRACT(year FROM completed_on)", })\
            .values('month', 'year')\
            .annotate(total_welsh_cases=Count(case2(When(language='cy', then=1,))), total_cases=Count('completed_on'),
                      total_welsh_with_english_postcodes=Count(case2(When(Q(language='cy')
                                                                           & Q(extra_data__has_key='PostCode')
                                                                           & ~Q(extra_data__PostCode__istartswith='cf')
                                                                           & ~Q(extra_data__PostCode__istartswith='ch')
                                                                           & ~Q(extra_data__PostCode__istartswith='hr')
                                                                           & ~Q(extra_data__PostCode__istartswith='np')
                                                                           & ~Q(extra_data__PostCode__istartswith='gl')
                                                                           & ~Q(extra_data__PostCode__istartswith='ld')
                                                                           & ~Q(extra_data__PostCode__istartswith='ll')
                                                                           & ~Q(extra_data__PostCode__istartswith='sa')
                                                                           & ~Q(extra_data__PostCode__istartswith='sy')
                                                                          , then=1))))
        return render(request, self.initial_report_template, {
            'title': 'Case Initial Report',
            'opts': self.model._meta,
            'case_month_data': case_month_data,
            'cutoff_date': cutoff_date,
        })

    def ongoing_report_view(self, request):
        cutoff_date = date(2017,7,31)
        case_month_data = Case.objects.filter(completed_on__isnull=False).filter(completed_on__gte=cutoff_date)\
            .extra(select={'month': "EXTRACT(month FROM completed_on)",'year': "EXTRACT(year FROM completed_on)",})\
            .values('month', 'year')\
            .annotate(total_welsh_cases=Count(case2(When(language='cy', then=1,))), total_cases=Count('completed_on'),
                      total_welsh_with_english_postcodes=Count(case2(When(Q(language='cy')
                                                                           & Q(extra_data__has_key='PostCode')
                                                                           & ~Q(extra_data__PostCode__istartswith='cf')
                                                                           & ~Q(extra_data__PostCode__istartswith='ch')
                                                                           & ~Q(extra_data__PostCode__istartswith='hr')
                                                                           & ~Q(extra_data__PostCode__istartswith='np')
                                                                           & ~Q(extra_data__PostCode__istartswith='gl')
                                                                           & ~Q(extra_data__PostCode__istartswith='ld')
                                                                           & ~Q(extra_data__PostCode__istartswith='ll')
                                                                           & ~Q(extra_data__PostCode__istartswith='sa')
                                                                           & ~Q(extra_data__PostCode__istartswith='sy')
                                                                          , then=1))))
        return render(request, self.ongoing_report_template, {
            'title': 'Case Ongoing Report',
            'opts': self.model._meta,
            'case_month_data': case_month_data,
            'cutoff_date': cutoff_date,
        })


class OffenceFilterAdmin(admin.ModelAdmin):
    list_display = ("filter_match", "description")
    search_fields = ("filter_match", "description")


class CourtEmailCountAdmin(admin.ModelAdmin):
    list_display = (
        "court", "date_sent", "initiation_type", "total_pleas", "total_guilty",
        "total_not_guilty", "hearing_date", "sent", "processed")
    model = CourtEmailCount


class DataValidationAdmin(admin.ModelAdmin):
    list_display = ("date_entered", "urn_entered", "case_match", "case_match_count")
    list_filter = (MatchFilter, RegionalFilter)

    statistics_template = "admin/statistics.html"
    change_list_template = "admin/datavalidation_change_list.html"

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urls = [
            url(
                r'^statistics/$',
                wrap(self.statistics_view),
                name='%s_%s_statistics' % info
            ),
        ]

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
            dv = DataValidation.objects.filter(
                urn_entered__startswith=court.region_code,
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

        return render(request, self.statistics_template, {
            'title': 'Data Validation Statistics',
            'opts': self.model._meta,
            'recent_days': recent_days,
            'regions': regions
        })


class UrnFilter(admin.SimpleListFilter):
    """Allow filtering by URN from case or event_data"""

    TOP_URN_LIMIT = 20  # Display this many URNs in the filter
    title = 'Top {0} URNs'.format(TOP_URN_LIMIT)
    parameter_name = 'urn'

    def lookups(self, request, model_admin):
        """Build a list of top urns referenced by auditevents"""

        audit_events = AuditEvent.objects \
            .filter(case__isnull=False) \
            .values('case__urn') \
            .annotate(count_by_case=Count('case')) \
            .order_by('-count_by_case')

        return [
            (
                ae["case__urn"],
                "{0} ({1})".format(
                    ae["case__urn"],
                    ae["count_by_case"])
            )
            for ae in audit_events[:self.TOP_URN_LIMIT]
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

    title = 'Initiation type'
    parameter_name = 'initiation_type'

    def lookups(self, request, model_admin):

        return list(INITIATION_TYPE_CHOICES) + [(
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
    search_fields = ("case__name", "case__urn", "case__extra_data__urn")
    raw_id_fields = ("case",)
    readonly_fields = ("case", "event_type", "event_subtype", "event_trace", "event_data", "event_datetime")

    def get_search_results(self, request, queryset, search_term):
        """
        Perform a less intensive search on some fields (e.g. hstore types). By default a
        filter with 'icontains' is added for each field.
        """

        # Separate fields into the good and the bad
        included_fields = []
        excluded_fields = []
        for field in self.search_fields:
            if field.startswith('case__extra_data__') or field.endswith('__urn'):
                excluded_fields.append(field)
            else:
                included_fields.append(field)

        # Most fields can benefit from the full, substring search
        self.search_fields = tuple(included_fields)
        queryset, use_distinct = super(
            AuditEventAdmin, self).get_search_results(
                request, queryset, search_term)

        # Simple equality test for some intensive fields
        self.search_fields = tuple(included_fields + excluded_fields)
        for field in excluded_fields:
            queryset |= self.model.objects.filter(**{field: search_term})

        return queryset, use_distinct

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

    def get_queryset(self, request):
        auditevent_model = super(AuditEventAdmin, self).get_queryset(request)
        auditevent_model = auditevent_model.prefetch_related('case')
        return auditevent_model

    def has_add_permission(self, request):
        return False


class CaseTrackerAdmin(admin.ModelAdmin):
    readonly_fields = (
        'case',
    )

admin.site.register(UsageStats, UsageStatsAdmin)
admin.site.register(Court, CourtAdmin)
admin.site.register(CourtEmailCount, CourtEmailCountAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(CaseOffenceFilter, OffenceFilterAdmin)
admin.site.register(DataValidation, DataValidationAdmin)
admin.site.register(AuditEvent, AuditEventAdmin)
admin.site.register(CaseTracker, CaseTrackerAdmin)
