from django import template
from django.utils.text import mark_safe


register = template.Library()

@register.filter
def hdir(obj):
    dir_text = dir(obj)
    return mark_safe("<pre>{0}</pre>".format(dir_text))

@register.filter
def pdir(obj):
    print dir(obj)
    return obj


@register.filter
def pdb(obj):
    import ipdb; ipdb.set_trace()
    return obj