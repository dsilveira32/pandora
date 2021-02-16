from django import template

register = template.Library()

# Use this to call methods in templates that are
# otherwise not callable
@register.simple_tag
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)