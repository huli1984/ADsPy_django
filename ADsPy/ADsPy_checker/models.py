from django.db import models
from django.urls import reverse
from django.utils import timezone
import pandas as pd
import re
from datetime import datetime
import time
import datetime
import os


delay = 2  # seconds
page_number = 1
previousPageNumber = 0
serie = 0

debug_mode = False
headless = True
condition = True
on_run = True
first_run = True
no_tads = False
latandlong = ""
lat = 0.0
long = 0.0
resting_time = 30
default_loc = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print([item for item in os.walk(BASE_DIR) if "template" in str(item)])
csv_address = BASE_DIR + "/ADsPy_checker/static/ADsPy/df/"


# Create your models here.
class MySearch(models.Model):
    """A typical class defining a model, derived from the Model class."""

    csv_address = BASE_DIR + "/ADsPy_checker/static/ADsPy/df/"
    print("BASE DIR: {}".format(BASE_DIR))

    # Fields
    job_starts = models.DateTimeField(verbose_name="Inserire tempo di avvio", default=timezone.now)
    #job_starts = models.CharField(max_length=5, default="now")
    timestamp_now = models.DateField(auto_now=False, auto_now_add=True)
    result_field = models.TextField(blank=True, null=True)
    slug = models.SlugField()
    latandlong = models.CharField(max_length=50, default="Seppia")
    my_search_query = models.CharField(max_length=250)
    wanna_check_distance = models.BooleanField(default=True)
    initialize = models.CharField(default="N", max_length=1)
    prof = BASE_DIR + "/ADsPy_checker/static/ADsPy/profile/"
    prof_one = BASE_DIR + "/ADsPy_checker/static/ADsPy/profile_one/"
    prof_two = BASE_DIR + "/ADsPy_checker/static/ADsPy/profile_two/"
    prof_three = BASE_DIR + "/ADsPy_checker/static/ADsPy/profile_three/"
    job_timeout = models.CharField(max_length=9, default=900)
    insert_job_timeout = models.CharField(max_length=5, name="job timeout", default="00:15")

    # Metadata
    class Meta:
        ordering = ['-my_search_query']
        permissions = (('can_publish', 'Can Publish Posts'),)

    # Methods
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return str(self.my_search_query).upper()

    def get_url(self):
        return reverse("queries", kwargs={"id": self.id, "slug": self.slug})

    def display_df(self, param=None):
        no_presence = False
        no_query = False
        start_datetime = 0
        end_datetime = 0

        try:
            csv_data = pd.read_csv(os.path.join(self.csv_address, "result_{}_{}.csv".format(self.my_search_query, self.id)), index_col=0)
        except FileNotFoundError:
            df = pd.DataFrame()
            df["alpha"] = 0
            df["n. in session"] = ""
            df["datetime"] = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            df["website title"] = ""
            df["kind"] = ""
            df["location (coordinates)"] = ""
            df["location (name)":] = ""
            df["query"] = ""
            df["presence at 5 km"] = ""
            df["presence at 10 km"] = ""
            df["presence at 20 km"] = ""
            df = df.reset_index()
            df.to_csv(os.path.join(self.csv_address, "result_{}_{}.csv".format(self.my_search_query, self.id)))
            csv_data = df

        if not param:
            pd.set_option("display.max_colwidth", -1)
            csv_data = csv_data.drop(columns="index")
            csv_data = csv_data.drop(columns="alpha")

            try:
                csv_data = csv_data.drop(columns="location (name)")
            except KeyError:
                pass

            my_table = csv_data.to_html(classes="result_table")

        else:
            print("param", param)
            print("")

            pd.set_option("display.max_colwidth", -1)
            csv_data = csv_data.drop(columns="index")
            csv_data = csv_data.drop(columns="alpha")
            # csv_data = csv_data.drop(columns="location (name)")

            if "'no_presence': ['1']" in param:
                csv_data = csv_data.drop(columns="presence at 5 km")
                csv_data = csv_data.drop(columns="presence at 10 km")
                csv_data = csv_data.drop(columns="presence at 20 km")
                no_presence = True
            elif ("'no_presence': ['0']" in param) and no_presence:
                no_presence = False

            if "'no_query': ['1']" in param:
                csv_data = csv_data.drop(columns="query")
                no_query = True
            elif ("'no_query': ['0']" in param) and no_query:
                no_query = False

            if "start': ['0']" in param:
                pass
            else:
                # find the date in string format:
                # it needs to be converted in date object
                if re.findall(re.compile(r"'start': \['\d\d\/\d\d\/\d\d\d\d'\]"), param):
                    start_string_raw = re.findall(re.compile(r"'start': \['\d\d\/\d\d\/\d\d\d\d'\]"), param)[0].replace("'start': ['", "").replace("']", "")
                    start_datetime = datetime.datetime.strptime(start_string_raw, "%d/%m/%Y")
                    print(start_datetime, "start datetime")

            if "end': ['0']" in param:
                pass
            else:
                # find the date in string format:
                # it needs to be converted in date object
                if re.findall(re.compile(r"'end': \['\d\d\/\d\d\/\d\d\d\d'\]"), param):
                    end_string_raw = re.findall(re.compile(r"'end': \['\d\d\/\d\d\/\d\d\d\d'\]"), param)[0].replace("'end': ['", "").replace("']", "")
                    end_datetime = datetime.datetime.strptime(end_string_raw, "%d/%m/%Y")
                    print(end_datetime, "end time")

            if start_datetime != 0 and end_datetime != 0:
                # retrieve dates from column in dataframe
                csv_data = csv_data.loc[pd.to_datetime(csv_data["datetime"], dayfirst=True).between(start_datetime, end_datetime, inclusive=True)]
                print(csv_data, "csv in function")
            else:
                print(csv_data, "csv in else")

            try:
                csv_data = csv_data.drop(columns="location (name)")
            except KeyError:
                pass

            my_table = csv_data.to_html(classes="result_table")

        return "{}".format(my_table).replace("&lt;", "<").replace("&gt;", ">")

    def find_post_id(self):
        return int(self.id)







