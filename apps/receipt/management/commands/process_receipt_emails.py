from django.core.management.base import BaseCommand, CommandError

from apps.receipt.process import process_receipts


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Process receipt emails'

    def handle(self, *args, **options):

        log = process_receipts()

        self.stdout.write("Completed. See ReceiptLog(<{}>) for more details.".format(log.id))