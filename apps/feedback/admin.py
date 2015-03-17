import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import UserRating, UserRatingAggregate


def performance_platform_export(modeladmin, request, queryset):

    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = "attachment; filename=perf_platform_user_rating.csv"

    writer = csv.writer(response)

    for data in queryset.all().order_by("start_date"):

        start_date = unicode(data.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
        feedback_avg = unicode(data.feedback_avg)

        writer.writerow([start_date, u"week", feedback_avg])

    return response
performance_platform_export.short_description = "Export for performance platform"


class UserRatingAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "rating")


class UserRatingAggregateAdmin(admin.ModelAdmin):
    list_display = ("start_date", "feedback_count", "feedback_total", "feedback_avg")

    actions = [performance_platform_export]


admin.site.register(UserRating, UserRatingAdmin)
admin.site.register(UserRatingAggregate, UserRatingAggregateAdmin)
