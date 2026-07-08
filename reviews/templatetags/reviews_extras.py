from django import template

register = template.Library()


@register.filter(name='star_rating')
def star_rating(value, max_stars=10):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''

    filled = round(value / 2)
    filled = max(0, min(5, filled))
    empty = 5 - filled
    return '★' * filled + '☆' * empty


@register.simple_tag
def multiply(a, b):
    try:
        return round(float(a) * float(b), 2)
    except (TypeError, ValueError):
        return 0
