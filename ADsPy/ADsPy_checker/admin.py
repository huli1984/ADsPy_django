from django.contrib import admin
from django.utils.safestring import mark_safe
from django.apps import apps

# Register your models here.
from .models import MySearch
import os
import pandas as pd
import bs4 as BS
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css_path = BASE_DIR + "/ADsPy_checker/static/ADsPy/css/"
js_path = BASE_DIR + "/ADsPy_checker/static/ADsPy/js/"
csv_address = BASE_DIR + "/ADsPy_checker/static/ADsPy/df/"


class MySearchAdmin(admin.ModelAdmin):

    list_display = ["__str__", "timestamp_now", "latandlong", "job_timeout"]
    list_filter = ["my_search_query", "latandlong"]
    search_fields = ["my_search_query", "result_field", "latandlong"]
    prepopulated_fields = {"slug": ("my_search_query",)}

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['location_list'] = self.process_data_model()
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.POST.get("change-list"):
            print("into modification")
        extras = extra_context or {}
        extras['location_list'] = self.process_data_model()
        return super().change_view(request, object_id, form_url, extra_context=extras)

    def process_data_model(self):
        location_list = pd.read_csv("{}location.csv".format(csv_address))
        result_list = location_list.drop(columns="Unnamed: 0")
        result_list = result_list.to_html()
        html_soup = BS.BeautifulSoup(result_list, "html.parser")
        tds = html_soup.findAll("td")
        for i in range(0, len(tds)):
            if i%2 == 0:
                tds[i].string.replace_with('<input id=\"button_' + str(i) + '\" onclick="fillTargetContainer(\'button_' + str(i) + '\')" style="width: 100%; height: 100%; /*background-color: #92a992;*/" class="location-input" type="button" value="' + tds[i].text +'">')
            else:
                tds[i].replace_with("<td style='border-bottom-color: #92a992'>" + tds[i].text)

        html_soup = re.sub(re.compile(r"<th>(?:\d+</th>)"), "<th class='to-hide'>", str(html_soup))
        return html_soup.replace('&lt;', '<').replace('&gt;', '/>') # .replace("<td>", "<td style='background-color: #92a992'>")

    class Meta:
        model = MySearch

    class Media:
        css = {"all": ("{}admin.css".format(css_path))}
        js = ("{}admin.js".format(js_path))


admin.site.register(MySearch, MySearchAdmin)
