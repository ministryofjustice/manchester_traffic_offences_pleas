import datetime as dt

from django.db import models
from django.utils import translation

from .forms import SATISFACTION_CHOICES, RATING_QUESTIONS


class UserRatingManager(models.Manager):

    def record(self, service_rating, call_centre_rating, comments=None):
        """
        Record a user service and call centre satisfaction rating and update
        aggregates accordingly.
        """

        try:
            cc_rating = int(call_centre_rating)
        except (ValueError, TypeError):
            cc_rating = None

        obj = self.create(service_rating=int(service_rating), call_centre_rating=cc_rating, comments=comments)

        UserRatingAggregate.objects.update_weekly_aggregate(obj)

        if call_centre_rating:
            UserRatingAggregate.objects.update_weekly_aggregate(obj, question_tag="call-centre")


class UserRating(models.Model):

    timestamp = models.DateTimeField(auto_now_add=True)

    service_rating = models.PositiveIntegerField(choices=SATISFACTION_CHOICES)

    call_centre_rating = models.PositiveIntegerField(choices=SATISFACTION_CHOICES, null=True)

    comments = models.CharField(default=None, blank=True, null=True, max_length=4000)

    objects = UserRatingManager()


class UserRatingAggregateManager(models.Manager):

    @translation.override("en")
    def update_weekly_aggregate(self, rating_obj, question_tag="overall"):
        """
        Amend a rating to the aggregate count.
        """

        # calculate start of week, e.g. the last Monday 00:00
        start_date = dt.datetime.combine(
            rating_obj.timestamp - dt.timedelta(rating_obj.timestamp.weekday()),
            dt.time.min)

        # Get the rating we're processing here, overall or call centre
        if question_tag == "call-centre":
            rating = rating_obj.call_centre_rating
        else:
            rating = rating_obj.service_rating

        try:
            aggregate_obj = self.get(start_date=start_date, question_tag=question_tag)
        except UserRatingAggregate.DoesNotExist:
            aggregate_obj = UserRatingAggregate(
                start_date=start_date,
                question_tag=question_tag,
                question_text=RATING_QUESTIONS[question_tag],
                rating_1=0,
                rating_2=0,
                rating_3=0,
                rating_4=0,
                rating_5=0,
                total=0)

        rating_key = "rating_" + str(rating)

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

    question_tag = models.CharField(max_length=24, default="overall")

    question_text = models.CharField(max_length=255)

    rating_1 = models.PositiveIntegerField(default=0)
    rating_2 = models.PositiveIntegerField(default=0)
    rating_3 = models.PositiveIntegerField(default=0)
    rating_4 = models.PositiveIntegerField(default=0)
    rating_5 = models.PositiveIntegerField(default=0)

    total = models.PositiveIntegerField(default=0)

    objects = UserRatingAggregateManager()

    class Meta:
        ordering = ("start_date",)

