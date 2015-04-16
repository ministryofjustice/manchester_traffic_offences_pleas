import datetime as dt
import json
import sys
import time
import traceback

from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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

    def _get_stack_trace(self):
        ex_type, ex, tb = sys.exc_info()
        return "An exception has occured: {}\n\n{}"\
               .format(ex, traceback.format_tb(tb))

    def post(self, request, *args, **kwargs):

        # temporarily logging to try to figure out structure of webhook
        ReceiptLog.objects.create(status_detail=str(request.POST))

        return HttpResponse("OK")

        time1 = time.time()
        start_date = dt.datetime.now()

        success_count, failure_count, error_count = 0, 0, 0

        try:
            data = request.POST["mandrill_events"]
        except KeyError:
            return HttpResponse("Bad request", status_code=400)

        items = json.loads(data)

        status_text = []

        for item in items:

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
            status_detail=status_text)

        return HttpResponse("OK")
