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
                rating_1=0,
                rating_2=0,
                rating_3=0,
                rating_4=0,
                rating_5=0,
                total=0)

        rating_key = "rating_" + str(rating_obj.rating)

        current_rating = getattr(aggregate_obj, rating_key, 0)
        current_rating += 1

        setattr(aggregate_obj, rating_key, current_rating)
        aggregate_obj.total += 1

        aggregate_obj.save()


class UserRatingAggregate(models.Model):
    """
    The aggregate model - currently just storing weekly
    aggregates on a Monday-Sunday period.
    """

    start_date = models.DateTimeField()

    rating_1 = models.PositiveIntegerField(default=0)
    rating_2 = models.PositiveIntegerField(default=0)
    rating_3 = models.PositiveIntegerField(default=0)
    rating_4 = models.PositiveIntegerField(default=0)
    rating_5 = models.PositiveIntegerField(default=0)

    total = models.PositiveIntegerField(default=0)

    objects = UserRatingAggregateManager()

    class Meta:
        ordering = ("start_date",)

