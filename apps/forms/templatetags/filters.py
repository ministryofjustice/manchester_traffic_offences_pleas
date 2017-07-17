from django import template

register = template.Library()


@register.filter(name="format")
def fmt(value, arg):
    return value.format(arg)


@register.filter(name="index")
def index(value, idx):
    if value and idx > 0:
        try:
            return value[idx - 1]
        except IndexError:
            return {}


@register.filter(name="equal_coerced")
def equal_coerced(a, b):
    """Equality test for templating, coercing to the type of a"""
    atype, btype = type(a), type(b)

    if atype is not btype:
        if atype == bool:
            b = True if b == "True" else False if b == "False" else b

    return a == b
