import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

register = template.Library()

# Use this to call methods in templates that are
# otherwise not callable
@register.simple_tag
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj, sort_keys=True, indent=1, cls=DjangoJSONEncoder))

@register.simple_tag
def subtract_until_zero(value, arg):
    ret = value - arg
    if ret < 0:
        ret = 0
    return ret

@register.simple_tag
def days_left_until(date):
    from datetime import datetime
    today = datetime.now()
    diff = today - date
    daysleft = diff.days
    if daysleft < 0:
        daysleft = 0
    return daysleft

@register.simple_tag
def get_percent(current, max, reverse):
    ret = current*100/max
    if reverse:
        ret = 100 - ret
    if ret < 0:
        ret = 0
    return int(round(ret, 0))

@register.simple_tag
def list_has_open_contests(contests):
    for c in contests:
        try:
            if c.isOpen():
                return True
        except:
            pass
    return False

@register.simple_tag
def list_has_closed_contests(contests):
    for c in contests:
        try:
            if not c.isOpen():
                return True
        except:
            pass
    return False

