import csv
from django.core.management.base import BaseCommand


from apps.plea.models import DataValidation, Case
from apps.plea.standardisers import standardise_urn, format_for_region


class Command(BaseCommand):
    help = "Build weekly aggregate stats"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+')

    def handle(self, *args, **options):
        with open(options['csv_file'][0]) as csvfile:
            total_matched, total_missed, matched, missed = 0, 0, 0, 0

            for row in csvfile.readlines():
                if not row.strip():
                    continue
                elif row.startswith("#"):
                    if matched > 0 or missed > 0:
                        print "----------------\nMatched {}\nMissed {}\n\n".format(matched, missed)
                        total_matched += matched
                        total_missed += missed
                        matched = 0
                        missed = 0
                    print row
                else:
                    urn = standardise_urn(row)
                    if Case.objects.filter(urn__iexact=urn).exists():
                        matched += 1
                    else:
                        missed += 1
                        print "{} - failed".format(urn)

        print "----------------\nTotal:\nMatched {}\nMissed {}".format(total_matched, total_missed)