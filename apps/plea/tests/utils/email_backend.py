from django.core.mail.backends.base import BaseEmailBackend


class TestEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        """
        We don't want to send any messages just view them in the outbox for testing
        """
        return len(email_messages)
