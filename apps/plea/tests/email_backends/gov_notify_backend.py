from django.core.mail.backends.locmem import EmailBackend
from . import notify_mail


class GovNotifyBackendTest(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_messages(self, email_messages):
        if email_messages:
            for email in email_messages:
                notify_mail.outbox.append(email)
