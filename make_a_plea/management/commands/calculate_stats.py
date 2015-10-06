from django.core.management.base import BaseCommand


from apps.plea.models import UsageStats


class Command(BaseCommand):
    help = "Build weekly aggregate stats"

    def handle(self, *args, **options):

        UsageStats.objects.calculate_weekly_stats()
