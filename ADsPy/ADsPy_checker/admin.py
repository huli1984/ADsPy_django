from django.contrib import admin
from django.utils.safestring import mark_safe
from django.apps import apps

# Register your models here.
from .models import MySearch
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css_path = BASE_DIR + "/ADsPy_checker/static/ADsPy/css/"
js_path = BASE_DIR + "/ADsPy_checker/static/ADsPy/js/"
csv_address = BASE_DIR + "/ADsPy_checker/static/ADsPy/df/"


def process_data_model():
    my_search = apps.get_model(app_label="ADsPy_checker", model_name="MySearch")
    return my_search.process_data()


class MySearchAdmin(admin.ModelAdmin):

    list_display = ["__str__", "timestamp_now", "geolocation", "job_timeout"]
    list_filter = ["my_query", "geolocation"]
    search_fields = ["my_query", "result_field", "geolocation"]
    prepopulated_fields = {"slug": ("my_query",)}

    class Meta:
        model = MySearch

    class Media:
        css = {"all": ("{}admin.css".format(css_path))}
        js = ("{}admin.js".format(js_path))


admin.site.register(MySearch, MySearchAdmin)
