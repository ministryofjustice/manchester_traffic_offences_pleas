import csv

from django.contrib import admin
from django.http import HttpResponse
from django.core.validators import EMPTY_VALUES
from .models import UserRating, UserRatingAggregate


def performance_platform_export(modeladmin, request, queryset):

    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = "attachment; filename=perf_platform_user_rating.csv"

    writer = csv.writer(response)

    writer.writerow(["_timestamp",
                     "period",
                     "question_tag",
                     "question_text",
                     "rating_1",
                     "rating_2",
                     "rating_3",
                     "rating_4",
                     "rating_5",
                     "total"])

    for data in queryset.all().order_by("start_date"):

        start_date = unicode(data.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
        question_tag = unicode(data.question_tag)
        question_text = unicode(data.question_text)
        rating_1 = unicode(data.rating_1)
        rating_2 = unicode(data.rating_2)
        rating_3 = unicode(data.rating_3)
        rating_4 = unicode(data.rating_4)
        rating_5 = unicode(data.rating_5)
        total = unicode(data.total)

        writer.writerow([start_date,
                         "week",
                         question_tag,
                         question_text,
                         rating_1,
                         rating_2,
                         rating_3,
                         rating_4,
                         rating_5,
                         total])

    return response
    
performance_platform_export.short_description = "Export for performance platform"


class CommentsFilter(admin.SimpleListFilter):
    """Allow filtering Cases by Comment including compound views"""

    title = u'comments'
    parameter_name = u'comments'

    def lookups(self, request, model_admin):
        return(
            ('0', 'Commented', ),
            ('1', 'Not commented',),
        )

    def queryset(self, request, queryset):
        if self.value() in EMPTY_VALUES:
            return queryset
        exclude = (self.value() == '0')
        kwargs = {'{0}__exact'.format(self.parameter_name): ''}
        method = queryset.exclude if exclude else queryset.filter
        return method(**kwargs)


class UserRatingAdmin(admin.ModelAdmin):

    list_display = ("timestamp", "service_rating", "call_centre_rating", "comments")
    list_filter = ("timestamp", "service_rating", "call_centre_rating", CommentsFilter)


class UserRatingAggregateAdmin(admin.ModelAdmin):
    list_display = ("start_date", "question_tag", "question_text", "rating_1", "rating_2", "rating_3", "rating_4",
                    "rating_5", "total")

    actions = [performance_platform_export]


admin.site.register(UserRating, UserRatingAdmin)
admin.site.register(UserRatingAggregate, UserRatingAggregateAdmin)
