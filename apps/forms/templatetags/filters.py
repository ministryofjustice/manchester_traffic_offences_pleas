from django import template

register = template.Library()


@register.filter(name="format")
def fmt(value, arg):
    return value.format(arg)


@register.filter(name="index")
def index(value, idx):
    if value and idx > 0:
        try:
            return value[idx-1]
        except IndexError:
            return {}
