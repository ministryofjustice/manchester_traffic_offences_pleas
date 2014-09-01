from django.core.management.base import BaseCommand, CommandError

from plea.models import CourtEmailPlea


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Deletes emails with a court date in the past'

    def handle(self, *args, **options):
        count = CourtEmailPlea.objects.delete_old_emails()

        if count > 0:
            self.stdout.write("{0} court email audit records cleaned".format(count))
        else:
            self.stdout.write("No records to delete")