from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def add_test_tag(text):
    """
    Add text to a template only if tests are being run.

    This is determined by settings.TESTING=True.

    Usage:
        {% if somecondition %}
            {% add_test_text "CONDITION1" %}
        {% else %}
            {% add_test_text "CONDITION2" %}
        {% endif %}

    Unit tests can then check for the presence of the condition text, rather
    than trying to match on the text content, to confirm that a specific
    branch/condition has been executed in a template, for a given input.

    """

    if getattr(settings, 'TESTING', False):
        return text
    else:
        return ''