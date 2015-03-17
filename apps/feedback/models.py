import datetime as dt

from django.db import models

from .forms import SATISFACTION_CHOICES


class UserRatingManager(models.Manager):

    def record(self, rating):
        """
        Record a user satisfaction rating and update
        aggregates accordingly.
        """

        obj = self.create(rating=int(rating))

        UserRatingAggregate.objects.update_weekly_aggregate(obj)


class UserRating(models.Model):

    timestamp = models.DateTimeField(auto_now_add=True)

    rating = models.PositiveIntegerField(choices=SATISFACTION_CHOICES)

    objects = UserRatingManager()


class UserRatingAggregateManager(models.Manager):

    def update_weekly_aggregate(self, rating_obj):
        """
        Amend a rating to the aggregate count.
        """

        # calculate start of week, e.g. the last Monday 00:00

        start_date = dt.datetime.combine(
            rating_obj.timestamp - dt.timedelta(rating_obj.timestamp.weekday()),
            dt.time.min)

        try:
            aggregate_obj = self.get(start_date=start_date)
        except UserRatingAggregate.DoesNotExist:
            aggregate_obj = UserRatingAggregate(
                start_date=start_date,
                feedback_count=0,
                feedback_total=0,
                feedback_avg=0)

        aggregate_obj.feedback_count += 1
        aggregate_obj.feedback_total += rating_obj.rating
        aggregate_obj.feedback_avg = \
            float(aggregate_obj.feedback_total) / aggregate_obj.feedback_count

        aggregate_obj.save()


class UserRatingAggregate(models.Model):
    """
    The aggregate model - currently just storing weekly
    aggregates on a Monday-Sunday period.
    """

    start_date = models.DateTimeField()

    feedback_count = models.PositiveIntegerField()
    feedback_total = models.PositiveIntegerField()
    feedback_avg = models.DecimalField(max_digits=5, decimal_places=2)

    objects = UserRatingAggregateManager()

    class Meta:
        ordering = ("start_date",)

