from django.contrib import admin

from apps.receipt.models import ReceiptLog


class ReceiptLogAdmin(admin.ModelAdmin):
    list_display = ("started", "total_emails", "total_errors", "total_failed", "total_success", "status", "status_detail")


admin.site.register(ReceiptLog, ReceiptLogAdmin)
