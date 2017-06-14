from datetime import datetime, date
from dateutil import parser
from django import template


register = template.Library()


@register.filter(name='parse_date')
def parse_date(value):
    try:
        return parser.parse(value)
    except ValueError:
        return "Unknown"
    except TypeError:
        return value
