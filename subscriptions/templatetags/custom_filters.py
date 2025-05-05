from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def abs_value(value):
    """Return the absolute value of a number."""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """Multiply the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
