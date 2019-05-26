from django import template
from django.utils.safestring import mark_safe
import time

register = template.Library()


# @register .tag
# def display_with_param(obj, arg):
#     print("param in first call method: ", arg)
#     print(str(arg), "arg in string")
#     make_table = obj.display_df(param=arg)
#     return make_table

@register .simple_tag
def call_method(obj, method_name, *args):
    print(obj, "obj", method_name, "method_name")
    method = getattr(obj, method_name)
    return mark_safe(method(*args))
