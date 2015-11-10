import datetime as dt

from rest_framework.decorators import list_route
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


from .serializers import CaseSerializer, UsageStatsSerializer

from apps.plea.models import Case, CourtEmailCount, UsageStats


class CaseViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create new cases
    """

    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class PublicStatsViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        start_date = request.GET.get("start", None)
        end_date = request.GET.get("end", None)

        stats = CourtEmailCount.objects.get_stats(start=start_date, end=end_date)

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

        stats = CourtEmailCount.objects.get_stats_by_court()

        return Response(stats)
