from django.contrib import admin

from apps.result.models import (Result,
                                ResultOffence,
                                ResultOffenceData)

import nested_admin


class InlineResultOffenceData(nested_admin.NestedStackedInline):
    model = ResultOffenceData
    extra = 0


class InlineResultOffence(nested_admin.NestedStackedInline):
    model = ResultOffence
    extra = 0
    inlines = [InlineResultOffenceData]


class ResultAdmin(nested_admin.NestedModelAdmin):
    list_display = ("urn", "case_number", "ou_code", "sent", "sent_on")
    list_filter = ("ou_code", "sent", )
    inlines = [InlineResultOffence, ]
    search_fields = ["urn", "case_number"]


admin.site.register(Result, ResultAdmin)
