from django import template
from django.utils.text import mark_safe


register = template.Library()

@register.filter
def hdir(obj):
    """
    HTML version of dir.
    """
    dir_text = dir(obj)
    return mark_safe("<pre>{0}</pre>".format(dir_text))

@register.filter
def pdir(obj):
    """
    Puts dir of an object on stdout
    """
    print(dir(obj))
    return obj


@register.filter
def pdb(obj):
    """
    Opens ipdb in the console.
    """
    import ipdb; ipdb.set_trace()
    return obj


@register.filter
def echo(obj):
    """
    Prints the value to the console.
    """
    print(obj)
    return obj