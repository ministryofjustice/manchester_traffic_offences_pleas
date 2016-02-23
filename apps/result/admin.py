from django.contrib import admin

from apps.result.models import (Result,
                                ResultOffence,
                                ResultOffenceData)


class InlineResultOffenceData(admin.StackedInline):
    model = ResultOffenceData
    extra = 0


class InlineResultOffence(admin.StackedInline):
    model = ResultOffence
    extra = 0
    inlines = [ResultOffenceData]


class ResultAdmin(admin.ModelAdmin):
    list_display = ("urn", "case_number", "ou_code", "sent", "sent_on")
    list_filter = ("ou_code", "sent", )
    inlines = [InlineResultOffence, ]
    search_fields = ["urn", "case_number"]


class ResultOffenceAdmin(admin.ModelAdmin):
    list_display = ("result", "offence_code")
    search_fields = ("result__urn", "result__case_number",)
    inlines = [InlineResultOffenceData, ]


admin.site.register(Result, ResultAdmin)
admin.site.register(ResultOffence, ResultOffenceAdmin)