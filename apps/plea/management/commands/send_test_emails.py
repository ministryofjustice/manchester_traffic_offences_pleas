from django.core.management.base import BaseCommand
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from apps.plea.tests.test_data import TEST_DEFENDANTS
from apps.plea.email import send_plea_email


class Command(BaseCommand):
    help = "Sends test emails to the given email address."

    def handle(self, *args, **options):
        try:
            validate_email(args[0])
            email = args[0]
        except:
            raise ValidationError(
                'First argument must be a valid email address')

        msg = "This will send %s emails to %s, is this ok?" % (
            len(TEST_DEFENDANTS),
            email)
        send = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False
        if send:
            for defendant in TEST_DEFENDANTS:
                send_plea_email({'about': defendant})
