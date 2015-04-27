from django import template

register = template.Library()

@register.inclusion_tag('widgets/std_field.html', takes_context=True)
def std_field(context, field, **kwargs):
    field.__dict__.update(kwargs)
    return {"field": field}