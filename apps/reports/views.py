# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.urls import reverse, reverse_lazy
from django.core.urlresolvers import resolve
from ..plea.models import UsageStats, Court
from urllib.parse import quote, urlencode
from ..feedback.models import UserRating
from .charts import RequiredStagesChart, FinancialSituationChart,\
    HardshipChart, AllStagesDropoutsChart, IncomeSourcesDropoutsChart
from django.db.models import Sum
import datetime
from .charts import safe_percentage


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url


@login_required(login_url=settings.ADMIN_LOGIN_URL)
def index(request):
    return render(request, 'report_links.html', {'disable_language_switch': True})


class ReportEntryView(LoginRequiredMixin, View):
    login_url = settings.ADMIN_LOGIN_URL
    report_type = None
    report_url = None
    report_entry_url = None
    report_description = None
    template = "reports.html"
    report_links = None
    display_axes = True

    def get(self, request, *args, **kwargs):
        self.initialize_get(request)
        return render(request, self.template, self.get_context_data(request))

    def get_context_data(self, request):
        return {"report_type": self.report_type,
                "report_description": self.report_description,
                "report_url": self.report_url,
                "report_entry_url": self.report_entry_url,
                'display_axes': self.display_axes,
                'disable_language_switch': True}


class PleaMixin(object):

    def initialize_get(self, request):
        self.report_type = "Plea"
        self.report_url = reverse("reports:plea_report")
        self.report_entry_url = reverse("reports:plea_report_entry")
        self.report_description = "A breakdown of the different types of plea over an entered date range"


class StageMixin(object):

    def initialize_get(self, request):
        self.report_type = "Stage Completion"
        self.report_url = reverse("reports:stage_report")
        self.report_entry_url = reverse("reports:stage_report_entry")
        self.report_description = "A statistical analysis of stage progression"


class UserRatingMixin(object):

    def initialize_get(self, request):
        self.report_type = "User Rating"
        self.report_url = reverse("reports:rating_report")
        self.report_entry_url = reverse("reports:rating_report_entry")
        self.report_description = "An analysis of service user ratings"


class PleaReportEntry(PleaMixin, ReportEntryView):
    pass


class StageReportEntry(StageMixin, ReportEntryView):
    pass


class RatingReportEntry(UserRatingMixin, ReportEntryView):
    pass


class BaseReportView(ReportEntryView):
    report_partial = None
    template = "report_base.html"
    start_date = None
    end_date = None

    @staticmethod
    def set_dates():
        day_start = quote(datetime.date.today().strftime('%d/%m/%Y'))
        week_start = datetime.date.today() - datetime.timedelta(days=7)
        week_start = quote(week_start.strftime('%d/%m/%Y'))
        month_start = quote(subtract_one_month(datetime.date.today()).strftime('%d/%m/%Y'))
        today = quote(datetime.date.today().strftime('%d/%m/%Y'))
        return day_start, week_start, month_start, today

    def update_context_with_period(self, request, context):
        day_start, week_start, month_start, today = self.set_dates()
        context["day_url"] = build_url("reports:" + resolve(request.path).url_name,
                                       get={'start_date': day_start, 'end_date': today})
        context["week_url"] = build_url("reports:" + resolve(request.path).url_name,
                                        get={'start_date': week_start, 'end_date': today})
        context["month_url"] = build_url("reports:" + resolve(request.path).url_name,
                                         get={'start_date': month_start, 'end_date': today})
        return context

    def get_context_data(self, request):
        current_context_data = super(BaseReportView, self).get_context_data(request)
        current_context_data["report_partial"] = self.report_partial
        current_context_data.update(self.prepare_report_context(request))
        current_context_data = self.update_context_with_period(request, current_context_data)
        return current_context_data

    def prepare_report_context(self, request):
        pass

    def set_start_end_dates(self, request):
        if 'start_date' in request.GET:
            try:
                self.start_date = datetime.datetime.strptime(request.GET['start_date'], '%d/%m/%Y').date()
            except ValueError:
                self.start_date = None

        if 'end_date' in request.GET:
            try:
                self.end_date = datetime.datetime.strptime(request.GET['end_date'], '%d/%m/%Y').date()
            except ValueError:
                self.end_date = None


class PleaReportView(PleaMixin, BaseReportView):

    selected_court = "All courts"
    report_partial = "partials/plea_report_contents.html"

    def prepare_report_context(self, request):

        qs = UsageStats.objects.all()

        # Ensure correct start and end dates for report
        self.set_start_end_dates(request)
        change_date = datetime.date(day=21, month=5, year=2018)
        court_change_date = datetime.date(day=10, month=6, year=2019)
        late_end_date = True  # Set to true if end date is after 21st May
        court_specific_late_end_date = True  # Set to true if end date is after 16th September
        early_start_date = True
        if self.start_date:
            qs = qs.filter(start_date__gte=self.start_date)
            start_date = self.start_date
            if start_date > change_date:
                early_start_date = False
        if self.end_date:
            qs = qs.filter(start_date__lte=self.end_date)
            end_date = self.end_date
            if end_date < change_date:
                late_end_date = False
            if end_date < court_change_date:
                court_specific_late_end_date = False

        if 'selected_court' in request.GET:
                self.selected_court = request.GET['selected_court']

        if self.selected_court != "All courts":
            qs = qs.filter(court__court_name=self.selected_court)

        pre_qs = qs.filter(start_date__lte=change_date)
        post_qs = qs.filter(start_date__gte=change_date)
        pre_totals = pre_qs.aggregate(Sum('online_submissions'),
                                      Sum('online_guilty_pleas'),
                                      Sum('online_not_guilty_pleas'))
        post_totals = post_qs.aggregate(Sum('online_submissions'),
                                        Sum('online_guilty_pleas'),
                                        Sum('online_not_guilty_pleas'),
                                        Sum('online_guilty_attend_court_pleas'),
                                        Sum('online_guilty_no_court_pleas'))
        totals = qs.aggregate(Sum('online_submissions'),
                              Sum('online_guilty_pleas'),
                              Sum('online_not_guilty_pleas'))
        all_online_submissions = totals["online_submissions__sum"] or 0
        all_online_guilty_pleas = totals["online_guilty_pleas__sum"] or 0
        all_online_not_guilty_pleas = totals["online_not_guilty_pleas__sum"] or 0
        all_online_pleas = all_online_guilty_pleas + all_online_not_guilty_pleas
        pre_online_submissions = pre_totals["online_submissions__sum"] or 0
        pre_online_guilty_pleas = pre_totals["online_guilty_pleas__sum"] or 0
        pre_online_not_guilty_pleas = pre_totals["online_not_guilty_pleas__sum"] or 0
        pre_online_pleas = pre_online_guilty_pleas + pre_online_not_guilty_pleas
        post_online_submissions = post_totals["online_submissions__sum"] or 0
        post_online_guilty_pleas = post_totals["online_guilty_pleas__sum"] or 0
        post_online_not_guilty_pleas = post_totals["online_not_guilty_pleas__sum"] or 0
        post_online_guilty_attend_court_pleas = post_totals["online_guilty_attend_court_pleas__sum"] or 0
        post_online_guilty_no_court_pleas = post_totals["online_guilty_no_court_pleas__sum"] or 0
        post_online_pleas = post_online_not_guilty_pleas + post_online_guilty_pleas

        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'late_end_date': late_end_date,
            'early_start_date': early_start_date,
            'all_online_submissions' : all_online_submissions,
            'all_online_guilty_pleas' : all_online_guilty_pleas,
            'all_online_not_guilty_pleas': all_online_not_guilty_pleas,
            'all_online_pleas': all_online_pleas,
            'pre_online_submissions': pre_online_submissions,
            'pre_online_guilty_pleas': pre_online_guilty_pleas,
            'pre_online_not_guilty_pleas': pre_online_not_guilty_pleas,
            'pre_online_pleas': pre_online_pleas,
            'post_online_submissions': post_online_submissions,
            'post_online_guilty_pleas': post_online_guilty_pleas,
            'post_online_not_guilty_pleas': post_online_not_guilty_pleas,
            'post_online_guilty_attend_court_pleas': post_online_guilty_attend_court_pleas,
            'post_online_guilty_no_court_pleas': post_online_guilty_no_court_pleas,
            'post_online_pleas': post_online_pleas,
            'list_of_courts': Court.objects.all().order_by('court_name'),
            'selected_court': self.selected_court,
            'court_specific_late_end_date': court_specific_late_end_date,
        }

    def update_context_with_period(self, request, context):
        if self.selected_court:
            day_start, week_start, month_start, today = self.set_dates()
            context["day_url"] = build_url("reports:" + resolve(request.path).url_name,
                                           get={'start_date': day_start, 'end_date': today,
                                                'selected_court': self.selected_court})
            context["week_url"] = build_url("reports:" + resolve(request.path).url_name,
                                            get={'start_date': week_start, 'end_date': today,
                                                 'selected_court': self.selected_court})
            context["month_url"] = build_url("reports:" + resolve(request.path).url_name,
                                             get={'start_date': month_start, 'end_date': today,
                                                  'selected_court': self.selected_court})
        else:
            context = super(PleaReportView, self).update_context_with_period(request, context)
        return context


class StageReportView(StageMixin, BaseReportView):

    report_partial = "partials/stage_report_contents.html"
    report_links = ((reverse_lazy("reports:required_stages_report"), "Required stages",
                     "Number of people that have visited each required stage"),
                   (reverse_lazy("reports:financial_situation_report"), "Income options",
                    "Number of people that have visited the required stages for guilty pleas"),
                    (reverse_lazy("reports:hardship_report"), "Hardship",
                     "Number of people that have visited each hardship-related stage"),
                    (reverse_lazy("reports:dropouts_all_stages_report"), "All dropouts",
                     "The probability of dropping out at any given stage"),
                    (reverse_lazy("reports:income_sources_dropouts_report"), "Income sources dropouts",
                     "The probability of dropping out after"
                     " selecting (self)employed/receiving out-of-work benefits/other"))
    chart_name = "Required stages"

    def call_correct_chart(self):
        return RequiredStagesChart(self.start_date, self.end_date)

    def prepare_report_context(self, request):
        # Ensure correct start and end dates for report
        self.set_start_end_dates(request)
        bar_chart = self.call_correct_chart()
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'case_count': bar_chart.get_case_count(),
            'complete_count': bar_chart.get_complete_count(),
            'completion_percentage': bar_chart.get_completion_percentage(),
            'bar_chart': bar_chart.get_bar_chart(),
            'report_links': self.report_links,
            'chart_name': self.chart_name,
        }


class RequiredStagesNumbersView(StageReportView):

    pass


class FinancialSituationNumbersView(StageReportView):

    chart_name = "Financial stages"

    def call_correct_chart(self):
        return FinancialSituationChart(self.start_date, self.end_date)


class HardshipStagesNumbersView(StageReportView):
    chart_name = "Hardship stages"

    def call_correct_chart(self):
        return HardshipChart(self.start_date, self.end_date)


class AllStagesDropoutsView(StageReportView):
    chart_name = "Dropout rates at all stages"
    display_axes = False

    def call_correct_chart(self):
        return AllStagesDropoutsChart(self.start_date, self.end_date)


class IncomeSourcesDropoutsView(StageReportView):
    chart_name = "Dropout rates of the income stages"

    def call_correct_chart(self):
        return IncomeSourcesDropoutsChart(self.start_date, self.end_date)


class RatingReportView(UserRatingMixin, BaseReportView):
    report_partial = "partials/rating_report_contents.html"
    chart_name = "User ratings"

    def prepare_report_context(self, request):
        self.set_start_end_dates(request)
        qs = UserRating.objects.all()
        if self.start_date:
            qs = qs.filter(timestamp__gte=self.start_date)
        if self.end_date:
            qs = qs.filter(timestamp__lte=self.end_date)
        tot_count = qs.count()
        vdis_count = qs.filter(service_rating=1).count()
        dis_count = qs.filter(service_rating=2).count()
        neither_count = qs.filter(service_rating=3).count()
        sat_count = qs.filter(service_rating=4).count()
        vsat_count = qs.filter(service_rating=5).count()
        bar_chart = [["Very dissatisfied".encode('ascii','ignore'), vdis_count],
                    ["Dissatisfied".encode('ascii','ignore'), dis_count],
                    ["Neither satisfied nor dissatisfied".encode('ascii','ignore'), neither_count],
                    ["Satisfied".encode('ascii','ignore'), sat_count],
                    ["Very satisfied".encode('ascii','ignore'), vsat_count]]
        rating_number_array = [vdis_count, dis_count, neither_count, sat_count, vsat_count]
        rating_percentage_array = [safe_percentage(vdis_count, tot_count), safe_percentage(dis_count, tot_count),
                                   safe_percentage(neither_count, tot_count), safe_percentage(sat_count, tot_count),
                                   safe_percentage(vsat_count, tot_count)]
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'bar_chart': bar_chart,
            "no_of_responses": tot_count,
            'no_of_each_response': rating_number_array,
            'percentage_of_each_response': rating_percentage_array,
            'chart_name': self.chart_name,
        }


def subtract_one_month(dt0):
    current_date = dt0.day
    dt1 = dt0.replace(day=1)
    dt2 = dt1 - datetime.timedelta(days=1)
    dt3 = dt2.replace(day=min(current_date, 28))

    return dt3