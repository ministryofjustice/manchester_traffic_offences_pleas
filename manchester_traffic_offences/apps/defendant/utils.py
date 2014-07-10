import re
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _


def is_valid_urn_format(urn):
    """
    URN is 13 characters long in the following format:

    00/AA/0000000/00
    """

    pattern = r"[0-9]{2}/[a-zA-Z]{2}/[0-9]{7}/[0-9]{2}"

    if not re.match(pattern, urn):
        raise exceptions.ValidationError(_('Not a valid URN'))

    return True
