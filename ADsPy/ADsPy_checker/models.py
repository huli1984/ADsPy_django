from django.db import models
from django.urls import reverse
from adspy import ADsPyManager
from selenium.webdriver.common.keys import Keys
from django.utils.safestring import mark_safe
from django.apps import apps
import pandas as pd
import bs4 as BS
import time
import datetime
import os

from redis import Redis
from rq import Queue

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
csv_address = BASE_DIR + "/ADsPy_checker/static/ADsPy/df/"


# Create your models here.
class MySearch(models.Model):
    """A typical class defining a model, derived from the Model class."""

    csv_address = BASE_DIR + "/ADsPy_checker/static/ADsPy/df/"


    # Fields
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
    job_timeout = models.CharField(max_length=6)

    # Metadata
    class Meta:
        ordering = ['-my_search_query']

    # Methods
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return str(self.my_search_query).upper()

    def get_url(self):
        return reverse("queries", kwargs={"id": self.id, "slug": self.slug})

    def display_df(self):
        try:
            csv_data = pd.read_csv(os.path.join(self.csv_address, "result_{}_{}.csv".format(self.my_search_query, self.id)), index_col=0)
        except FileNotFoundError:
            df = pd.DataFrame()
            df["alpha"] = 0
            df["n. in session"] = ""
            df["datetime"] = datetime.datetime.now()
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

        pd.set_option("display.max_colwidth", -1)
        csv_data = csv_data.drop(columns="index")
        csv_data = csv_data.drop(columns="alpha")
        my_table = csv_data.to_html(classes="result_table")
        return "{}".format(my_table)

    # def find_ads_background(self):
    #     print(self.csv_address, "csv address")
    #     manager = ADsPyManager(self.prof, self.prof_one, self.prof_two, self.prof_three, self.csv_address, self.my_search_query, self.initialize, self.wanna_check_distance, self.latandlong)
    #     q = Queue(connection=Redis())
    #     q.enqueue(manager.find_ads, self.csv_address, job_timeout=self.job_timeout)

    def find_post_id(self):
        return self.id



