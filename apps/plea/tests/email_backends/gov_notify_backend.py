from django.core.mail.backends.locmem import EmailBackend
from .notify_mail import outbox


class GovNotifyBackendTest(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_messages(self, email_messages):
        if email_messages:
            for email in email_messages:
                outbox.append(email)
