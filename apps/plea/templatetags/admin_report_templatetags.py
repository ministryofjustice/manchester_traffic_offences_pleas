from django import template
import calendar

register = template.Library()

@register.filter()
def month_name(month_num):
    return calendar.month_name[month_num]

@register.assignment_tag(takes_context=True)
def percentage(context, num, total_num):
    """
    Works out the percentage of num over total_num and then appends the percentage sign
    """

    p = float(num)/float(total_num) * 100
    percent = str(p) + "%"
    return percent