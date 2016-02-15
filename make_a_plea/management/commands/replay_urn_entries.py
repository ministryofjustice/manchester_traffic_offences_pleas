from django.core.management.base import BaseCommand

from apps.plea.models import DataValidation, Case


class Command(BaseCommand):
    help = "Re-runs the urn data validation entries to find matches in the current data set"

    def handle(self, *args, **options):
        for dv in DataValidation.objects.all():
            cases = Case.objects.filter(urn=dv.urn_standardised)
            dv.case_match_count = len(cases)
            if len(cases) > 0:
                dv.case_match = cases[0]

            dv.save()
