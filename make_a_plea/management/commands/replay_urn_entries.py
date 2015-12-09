import csv
from django.core.management.base import BaseCommand


from apps.plea.models import DataValidation, Case
from apps.plea.standardisers import standardise_urn, format_for_region


class Command(BaseCommand):
    help = "Build weekly aggregate stats"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+')

    def handle(self, *args, **options):
        print options["csv_file"]
        with open(options['csv_file'][0]) as csvfile:
            reader = csv.reader(csvfile)
            for idx, row in enumerate(reader):
                urn = row[2]
                dv = DataValidation()
                dv.urn_entered = urn
                dv.urn_standardised = standardise_urn(urn)
                dv.urn_formatted = format_for_region(dv.urn_standardised)
                cases = Case.objects.filter(urn=dv.urn_standardised)
                dv.case_match_count = len(cases)
                if len(cases) > 0:
                    dv.case_match = cases[0]

                dv.save()