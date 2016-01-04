import datetime as dt

from django.core.exceptions import ValidationError

from rest_framework.decorators import list_route
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


from .serializers import CaseSerializer, UsageStatsSerializer, ResultSerializer

from apps.plea.models import Case, CourtEmailCount, UsageStats, Result


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

        serializer = UsageStatsSerializer(stats, many=True)

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
