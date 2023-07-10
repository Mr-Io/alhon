from django import template
import datetime

register = template.Library()

@register.filter
def normalday(value):
    delta_days = (datetime.date.today() - value.date()).days
    if (delta_days == 0):
        res = "hoy"
    elif (delta_days == 1):
        res = "ayer"
    else:
        res = f"Hace {delta_days} días"
    return res
