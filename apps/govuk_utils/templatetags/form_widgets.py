from django import template

register = template.Library()

@register.inclusion_tag('widgets/std_field.html', takes_context=True)
def std_field(context, field, **kwargs):
    field.__dict__.update(kwargs)
    return {"field": field}

@register.inclusion_tag('widgets/multi_field.html', takes_context=True)
def radio_field(context, field, **kwargs):
    field.__dict__.update(kwargs)
    return {"field": field}

@register.inclusion_tag('widgets/multi_field.html', takes_context=True)
def multi_field(context, field, **kwargs):
    field.__dict__.update(kwargs)
    return {"field": field}

@register.inclusion_tag('widgets/hidden_field.html', takes_context=True)
def hidden_field(context, field, **kwargs):
    field.__dict__.update(kwargs)
    return {"field": field}

@register.inclusion_tag("widgets/split_form.html", takes_context=True)
def split_form(context, split_form):
    return {"form": split_form}
