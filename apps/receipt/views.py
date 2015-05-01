import datetime as dt
import json
import sys
import time
import traceback

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.plea.models import Court
from .models import ReceiptLog
from .process import process_receipt, InvalidFormatError, ReceiptProcessingError


class ReceiptWebhook(View):
    """
    Process a mandrill inbound email webhook

    See http://help.mandrill.com/entries/22092308-What-is-the-format-of-inbound-email-webhooks-
    """
    def head(self, *args, **kwargs):
        """
        This needs to exist so that Mandrill can validate the URL.
        """
        return HttpResponse('')

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ReceiptWebhook, self).dispatch(*args, **kwargs)

    @staticmethod
    def _get_stack_trace():
        ex_type, ex, tb = sys.exc_info()
        return "An exception has occured: {} - {}"\
               .format(ex, traceback.format_tb(tb))

    @staticmethod
    def _validate_email(from_email, to_email, headers):
        """
        Validate the from/to email addresses and header

        Returns True if the email appears to be valid, False if not,
        and will create a ReceiptLog entry if the email is invalid.
        """
        if not Court.objects.validate_emails(from_email,
                                             to_email):

            return False, "to/from emails are not in the Court model {} {}".format(from_email, to_email)

        header_check = getattr(settings, "RECEIPT_HEADER_FRAGMENT_CHECK", None)

        if header_check:
            for header in headers:
                if header_check in header:
                    break
            else:
                return False, "header fragment not found"

        return True, ""

    def post(self, request, *args, **kwargs):

        time1 = time.time()
        start_date = dt.datetime.now()

        success_count, failure_count, error_count = 0, 0, 0

        try:
            data = request.POST["mandrill_events"]
        except KeyError:
            return HttpResponse("Bad request", status=400)

        items = json.loads(data)

        status_text = []

        for item in items:

            valid, reason = self._validate_email(item["msg"]["from_email"],
                                                 item["msg"]["email"],
                                                 item["msg"]["headers"]["Received"])

            if not valid:
                status_text.append("Email not processed because: " + reason)

                error_count += 1

                continue

            try:
                processed, status_text = process_receipt(item["msg"]["subject"],
                                                         item["msg"]["text"])

            except (ReceiptProcessingError, InvalidFormatError) as ex:
                status_text.append("Processing error {}".format(str(ex)))

                error_count += 1
            except Exception:
                status_text.append(self._get_stack_trace())
                error_count += 1
            else:
                if processed:
                    success_count += 1
                else:
                    failure_count += 1

        ReceiptLog.objects.create(
            status=ReceiptLog.STATUS_COMPLETE,
            started=True,
            query_from=start_date,
            run_time=time.time()-time1,
            total_emails=len(items),
            total_errors=error_count,
            total_failed=failure_count,
            total_success=success_count,
            status_detail="\n".join(status_text))

        return HttpResponse("OK")
