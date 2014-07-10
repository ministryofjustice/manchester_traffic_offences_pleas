from django import template

register = template.Library()


@register.filter(name='ipdb')
def ipdb(value):
    # return value
    import ipdb
    ipdb.set_trace()