import os
import calendar
import dateutil.parser
import itertools
from functools import wraps

from django.http import Http404

from .exceptions import BadRequestException


def parse_date_or_400(datestring):
    try:
        dateobj = dateutil.parser.parse(datestring)
    except (TypeError, ValueError):
        raise BadRequestException("Bad date format")
    return dateobj


def staff_or_404(view_func):
    """
    Decorator for views. Checks user is logged in and is staff, else raises 404.
    """
    def _checklogin(request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            raise Http404

    return wraps(view_func)(_checklogin)


def filter_cases_by_month(cases):
    return {
        k: len(list(v))
        for k, v in itertools.groupby(
            cases,
            key=lambda case: "{0} {1}".format(
                calendar.month_name[case.completed_on.month],
                case.completed_on.year,
            ),
        )
    }


def get_supported_language_from_request(request):

    try:
        language = request.GET["language"]
    except KeyError:
        raise BadRequestException("No language given")

    supported_languages = os.listdir(
        os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)),
            "conf",
            "locale"))

    if language not in supported_languages:
        raise BadRequestException(
            "{0} is not a supported language".format(language))

    return language
