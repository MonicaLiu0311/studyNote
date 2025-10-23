from django import template

register = template.Library()

@register.filter
def second(value):
    try:
        return value[1]
    except (IndexError, TypeError):
        return None