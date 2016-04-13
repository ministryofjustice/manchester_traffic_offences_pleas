from raven.contrib.django.raven_compat.models import client


def log_user_data(context_data, extra_data=None):
    """
    Push extra user data into sentry for debugging purposes
    """

    def _get_key(func, cdata):
        try:
            return func(cdata)
        except KeyError:
            return "undefined"

    extra_data = extra_data or {}

    # record pertinent debugging data whilst discarding anything
    # that is potentially sensitive
    data = {
        "urn": _get_key(lambda x: x["case"]["urn"], context_data),
        "notice_type": _get_key(lambda x: x["notice_type"]["sjp"], context_data),
        "doh": _get_key(lambda x: x["case"]["date_of_hearing"], context_data),
        "posting_date": _get_key(lambda x: x["case"]["posting_date"], context_data),
        "plea_made_by": _get_key(lambda x: x["case"]["plea_made_by"], context_data),
        "dx": _get_key(lambda x: x["dx"], context_data)
    }

    data.update(extra_data)

    client.extra_context(data)

