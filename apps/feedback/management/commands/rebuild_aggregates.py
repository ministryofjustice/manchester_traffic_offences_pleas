from django.core.management.base import BaseCommand
from ...models import UserRatingAggregate, UserRating



class Command(BaseCommand):
    help = "Rebuild all User Satisfaction weekly aggregates"

    def handle(self, *args, **options):

        # Empty existing aggregates
        self.stdout.write("Deleting existing weekly aggregates... ", ending="")

        count = str(len(UserRatingAggregate.objects.all()))
        UserRatingAggregate.objects.all().delete()
        self.stdout.write(count + " weekly aggregate(s) deleted.")

        # Rebuild aggregates
        self.stdout.write("Rebuilding weekly aggregates... ", ending="")

        ratings = UserRating.objects.all()

        for rating in ratings:
            UserRatingAggregate.objects.update_weekly_aggregate(rating)

        count = str(len(UserRatingAggregate.objects.all()))
        self.stdout.write(count + " weekly aggregates created.")

        self.stdout.write("Done!")
