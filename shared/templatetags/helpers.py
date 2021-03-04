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