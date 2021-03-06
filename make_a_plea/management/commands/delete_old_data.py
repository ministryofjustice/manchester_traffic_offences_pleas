import datetime as dt

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.plea.models import AuditEvent, Case, CaseTracker
from apps.result.models import Result


class Command(BaseCommand):
    help = "Delete auditevent, case and result data that is greater " \
        "than {} days old".format(settings.DATA_RETENTION_PERIOD)

    def handle(self, *args, **options):

        cut_off_date = dt.datetime.now() - dt.timedelta(settings.DATA_RETENTION_PERIOD)

        Case.objects.filter(
            created__lt=cut_off_date).delete()

        Result.objects.filter(
            created__lt=cut_off_date).delete()

        AuditEvent.objects.filter(
            event_datetime__lt=cut_off_date).delete()