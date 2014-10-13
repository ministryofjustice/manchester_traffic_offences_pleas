from django.db import models


class ReceiptLog(models.Model):
    """
    A basic log to capture the status
    """

    STATUS_ERROR = 0
    STATUS_COMPLETE = 1

    STATUS_CHOICES = (
        (STATUS_ERROR, 'Error'),
        (STATUS_COMPLETE, 'Completed')
    )

    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=0)

    started = models.DateTimeField(
        auto_now=True,
        help_text="The time the script started processing")

    run_time = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Time the script took to complete in seconds")

    query_from = models.DateTimeField(blank=True, null=True)

    query_to = models.DateTimeField(blank=True, null=True)

    total_emails = models.PositiveIntegerField(
        default=0,
        help_text="Number of entries received from the API")

    total_errors = models.PositiveIntegerField(
        default=0,
        help_text="Number of entries that were not processable")

    total_failed = models.PositiveIntegerField(
        default=0,
        help_text="Number of entries recorded as failed by the PA")

    total_success = models.PositiveIntegerField(
        default=0,
        help_text="Number of entries that the PA indicated were successfully processed"
    )

    status_detail = models.TextField(null=True, blank=True)



