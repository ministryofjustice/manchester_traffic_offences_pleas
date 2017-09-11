from django.core.management.base import BaseCommand

from apps.plea.models import Case


class Command(BaseCommand):
    help = "Resets urns in list back to unsent so they can be reused"
    urn_list = ['97FF1234585', '98BB1234587', '98FF1234583', '98BB1234588']

    def handle(self, *args, **options):

        try:
            cases = Case.objects.filter(urn__in=self.urn_list, sent=True)
        except Case.DoesNotExist:
            return True
        cases.update(sent=False, processed=False, completed_on=None)
        print "Cases in urn list have been reset"


