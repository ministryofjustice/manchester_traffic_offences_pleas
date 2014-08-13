from dateutil import parser

from django import template

register = template.Library()


@register.filter(name='string_date')
def string_date(value):
    dt = parser.parse(value)
    return "{:%d %B %Y at %H:%I%p}".format(dt)