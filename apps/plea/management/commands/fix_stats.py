import json

from django.core.management.base import BaseCommand, CommandError

from apps.plea.models import CourtEmailPlea, CourtEmailCount


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Rebuild CourtEmailCount from CourtEmailPlea'

    def handle(self, *args, **options):

        CourtEmailCount.objects.all().delete()

        for plea in CourtEmailPlea.objects.all():
            data = json.loads(plea.dict_sent)

            email_count = CourtEmailCount()
            email_count.get_from_context(data)
            email_count.save()

            # fix the date
            email_count.date_sent = plea.date_sent
            email_count.save()

