import json

from django.http import HttpResponse

from rest_framework.decorators import detail_route, list_route
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


from .serializers import CaseSerializer

from apps.plea.models import Case, CourtEmailCount


class CaseViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create new cases
    """

    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class PublicStatsViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        stats = CourtEmailCount.objects.get_stats()

        return Response(stats)

    @list_route
    def by_hearing(self, request):
        stats = CourtEmailCount.objects.get_stats_by_hearing_date()

        return Response(stats)


def api_500(request):
    """
    A 500 handler to suppress the default HTML 500 handler for API calls.
    """

    return HttpResponse(json.dumps({'detail': 'An error occured'}),
                        content_type="application/json", status=500)