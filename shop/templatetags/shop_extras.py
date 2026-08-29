from django import template

register = template.Library()


@register.filter
def uah(value):
    try:
        n = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    return f"{n:,}".replace(",", " ") + " ₴"
