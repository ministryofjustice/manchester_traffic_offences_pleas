from django.core.mail.backends.locmem import EmailBackend
from . import notify_mail


class GovNotifyBackendTest(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_messages(self, email_messages):
        print("IN SEND MESSAGES TEST")
        if email_messages:
            for email in email_messages:
                print("APPENDING: ", email)
                notify_mail.outbox.append(email)
