from dateutil import parser

from django import template

register = template.Library()


@register.filter(name='string_date')
def string_date(value):
    if isinstance(value, basestring):
        dt = parser.parse(value)
    else:
        dt = value
    return "{:%d %B %Y}".format(dt)


@register.filter(name='string_time')
def string_time(value):
    if isinstance(value, basestring):
        dt = parser.parse(value)
    else:
        dt = value
    return "{:%H:%M}".format(dt)