from django.core.management.base import BaseCommand

from apps.plea.models import Case
from apps.plea.standardisers import standardise_urn


class Command(BaseCommand):
    help = "Build weekly aggregate stats"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+')

    def handle(self, *args, **options):
        total_matched, total_missed, matched, missed = 0, 0, 0, 0

        with open(options['csv_file'][0]) as csvfile:
            for row in csvfile.readlines():
                if not row.strip():
                    print "----------------\nMatched {}\nMissed {}\n\n".format(matched, missed)
                    total_matched += matched
                    total_missed += missed

                elif row.startswith("#"):
                    if matched > 0 or missed > 0:
                        matched = 0
                        missed = 0
                    print row
                else:
                    urn = standardise_urn(row)
                    if Case.objects.filter(urn__iexact=urn).exists():
                        matched += 1
                    else:
                        missed += 1
                        print "{} - failed".format(row.strip())

        print "----------------\nTotal:\nMatched {}\nMissed {}".format(total_matched, total_missed)
