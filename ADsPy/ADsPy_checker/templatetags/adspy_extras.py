from django import template
from django.utils.safestring import mark_safe
import time

register = template.Library()


@register .simple_tag
def call_method(obj, method_name, *args):
    print(obj, "obj", method_name, "method_name")
    method = getattr(obj, method_name)
    return mark_safe(method(*args))


@register .filter
def remove_brackets(value):
    return str(value).replace("['", "").replace("']", "")
