from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register .simple_tag
def call_method(obj, method_name, *args):
    print(obj, "obj", method_name, "method_name")
    method = getattr(obj, method_name)
    return mark_safe(method(*args))
