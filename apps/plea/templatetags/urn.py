from django import template
from django.utils.text import mark_safe

from ..standardisers import format_for_region


register = template.Library()


@register.filter
def format_urn(obj):
    """
    Re-format a standardised URN with any slashes or extra characters
    re-inserted.
    """
    formatted_urn = format_for_region(obj)
    return mark_safe(formatted_urn)
