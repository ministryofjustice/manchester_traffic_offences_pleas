"""
views
=====

"""
import datetime as dt

from django.db.models import Sum

from django.core.exceptions import ValidationError

from rest_framework.decorators import detail_route, list_route
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import AuditEventSerializer, CaseSerializer, UsageStatsSerializer, ResultSerializer
from apps.plea.models import AuditEvent, Case, CourtEmailCount, UsageStats
from apps.result.models import Result


class AuditEventViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create new audit events
    """
    queryset = AuditEvent.objects.all()
    serializer_class = AuditEventSerializer
    http_method_names = ['post']


class CaseViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create new cases
    """
    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class ResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create new results
    """
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


class PublicStatsViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def render_api_error(self, message):
        error = {
            "error": message
        }

        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        start_date = request.GET.get("start", None)
        end_date = request.GET.get("end", None)

        try:
            stats = CourtEmailCount.objects.get_stats(start=start_date, end=end_date)
        except ValidationError as e:
            return self.render_api_error("; ".join(e.messages))

        return Response(stats)

    def aggregate_field(self, query_to_aggregate, field_name):

        total = query_to_aggregate.aggregate(Sum(field_name))

        return total

    @list_route()
    def days_from_hearing(self, request):
        stats = CourtEmailCount.objects.get_stats_days_from_hearing()

        return Response(stats)

    @list_route()
    def by_hearing(self, request):

        now = dt.date.today()

        start_date = now - dt.timedelta(now.weekday())

        stats = CourtEmailCount.objects.get_stats_by_hearing_date(5, start_date)

        return Response(stats)

    @list_route()
    def all_by_hearing(self, request):

        stats = CourtEmailCount.objects.get_stats_by_hearing_date()

        return Response(stats)

    @list_route()
    def by_week(self, request):

        stats = UsageStats.objects.last_six_months()

        start_dates = []

        for n in stats:
            start_dates.append(n.start_date)

        distinct_start_dates = set(start_dates)

        stats_without_court = []

        for date in distinct_start_dates:

            weekly_stats = stats.filter(start_date=date)
            week_dict = {'online_submissions': self.aggregate_field(weekly_stats, 'online_submissions')['online_submissions__sum'],
                         'online_guilty_pleas': self.aggregate_field(weekly_stats, 'online_guilty_pleas')['online_guilty_pleas__sum'],
                         'online_not_guilty_pleas': self.aggregate_field(weekly_stats, 'online_not_guilty_pleas')['online_not_guilty_pleas__sum'],
                         'online_guilty_attend_court_pleas': self.aggregate_field(weekly_stats, 'online_guilty_attend_court_pleas')['online_guilty_attend_court_pleas__sum'],
                         'online_guilty_no_court_pleas': self.aggregate_field(weekly_stats, 'online_guilty_no_court_pleas')['online_guilty_no_court_pleas__sum'],
                         'postal_requisitions': self.aggregate_field(weekly_stats, 'postal_requisitions')['postal_requisitions__sum'],
                         'postal_responses': self.aggregate_field(weekly_stats, 'postal_responses')['postal_responses__sum'],
                         'start_date': date,
                         'id': weekly_stats[:1].get().id}

            stats_without_court.append(week_dict)

        stats_without_court_ordered = sorted(stats_without_court, key=lambda k: k['start_date'])

        serializer = UsageStatsSerializer(stats_without_court_ordered, many=True)

        return Response(serializer.data)

    @list_route()
    def by_court(self, request):
        start_date = request.GET.get("start", None)
        end_date = request.GET.get("end", None)

        try:
            stats = CourtEmailCount.objects.get_stats_by_court(start=start_date, end=end_date)
        except ValidationError as e:
            return self.render_api_error("; ".join(e.messages))

        return Response(stats)
