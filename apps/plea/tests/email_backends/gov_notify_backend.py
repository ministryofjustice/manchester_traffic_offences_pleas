from django.core.mail.backends.locmem import EmailBackend


class GovNotifyBackendTest(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_messages(self, email_messages):
        if email_messages:
            for email in email_messages:
                email.client.send_email_notification(
                    email_address=email.email_address,
                    personalisation=email.personalisation,
                    template_id=email.template_id
                )