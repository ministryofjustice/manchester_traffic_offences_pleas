# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.urls import reverse, reverse_lazy
from ..plea.models import UsageStats, CaseTracker
from .charts import RequiredStagesChart, FinancialSituationChart, HardshipChart, AllStagesDropoutsChart, IncomeSourcesDropoutsChart
from django.db.models import Value, Sum
import datetime

# Create your views here.

@login_required(login_url=settings.ADMIN_LOGIN_URL)
def index(request):
    return render(request, 'report_links.html', {'disable_language_switch': True})


class ReportEntryView(LoginRequiredMixin, View):
    login_url = settings.ADMIN_LOGIN_URL
    report_name = None
    report_url = None
    report_description = None
    template = "reports.html"
    report_links = None

    def get(self, request, *args, **kwargs):
        self.initialize_get(request)
        return render(request, self.template, self.get_context_data(request))

    def get_context_data(self, request):
        return {"report_name": self.report_name,
                "report_description": self.report_description,
                "report_url": self.report_url,
                'disable_language_switch': True}


class PleaMixin(object):

    def initialize_get(self, request):
        self.report_name = "Plea report"
        self.report_url = reverse("reports:plea_report")
        self.report_description = "A breakdown of the different types of plea over an entered date range"


class StageMixin(object):

    def initialize_get(self, request):
        self.report_name = "Stage completion report"
        self.report_url = reverse("reports:stage_report")
        self.report_description = "A statistical analysis of stage progression"


class PleaReportEntry(PleaMixin, ReportEntryView):
    pass


class StageReportEntry(StageMixin, ReportEntryView):
    pass


class BaseReportView(ReportEntryView):
    report_partial = None
    template = "report_base.html"

    def get_context_data(self, request):
        current_context_data = super(BaseReportView, self).get_context_data(request)
        current_context_data["report_partial"] = self.report_partial
        current_context_data.update(self.prepare_report_context(request))
        return current_context_data

    def prepare_report_context(self, request):
        pass


class PleaReportView(PleaMixin, BaseReportView):

    report_partial = "partials/plea_report_contents.html"

    def prepare_report_context(self, request):
        # Ensure correct start and end dates for report
        if 'start_date' in request.GET:
            try:
                start_date = datetime.datetime.strptime(request.GET['start_date'], '%d/%m/%Y').date()
            except ValueError:
                start_date = None

        if 'end_date' in request.GET:
            try:
                end_date = datetime.datetime.strptime(request.GET['end_date'], '%d/%m/%Y').date()
            except ValueError:
                end_date = None
        change_date = datetime.date(day=21,month=5,year=2018)
        qs = UsageStats.objects.all()
        late_end_date = True  # Set to true if end date is after 21st May
        early_start_date = True
        if start_date:
            qs = qs.filter(start_date__gte=start_date)
            start_date = start_date.date()
            if start_date > change_date:
                early_start_date = False
        if end_date:
            qs = qs.filter(start_date__lt=end_date)
            end_date = end_date.date()
            if end_date < change_date:
                late_end_date = False
        pre_qs = qs.filter(start_date__lt=change_date)
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
            'start_date': start_date,
            'end_date': end_date,
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
        }


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
    start_date = None
    end_date = None
    chart_name = "the required stages"

    def call_correct_chart(self):
        return RequiredStagesChart(self.start_date, self.end_date)

    def prepare_report_context(self, request):
        # Ensure correct start and end dates for report
        if 'start_date' in request.GET:
            try:
                start_date = datetime.datetime.strptime(request.GET['start_date'], '%d/%m/%Y').date()
            except ValueError:
                start_date = None

        if 'end_date' in request.GET:
            try:
                end_date = datetime.datetime.strptime(request.GET['end_date'], '%d/%m/%Y').date()
            except ValueError:
                end_date = None

        bar_chart = self.call_correct_chart()
        return {
            'start_date': start_date,
            'end_date': end_date,
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

    def call_correct_chart(self):
        return AllStagesDropoutsChart(self.start_date, self.end_date)


class IncomeSourcesDropoutsView(StageReportView):
    chart_name = "Dropout rates of the income stages"

    def call_correct_chart(self):
        return IncomeSourcesDropoutsChart(self.start_date, self.end_date)