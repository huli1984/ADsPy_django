from django.db import models
from django.urls import reverse
from adspy import PrepareLocation, SeleniumCtrl, LoadBar, Utilis, style
from selenium.webdriver.common.keys import Keys
import pandas as pd
import bs4 as BS
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


# Create your models here.
class MySearch(models.Model):
    """A typical class defining a model, derived from the Model class."""

    # Fields
    my_query = models.CharField(max_length=250)
    geolocation = models.CharField(max_length=250)
    timestamp_now = models.DateField(auto_now=False, auto_now_add=True)
    result_field = models.TextField()
    slug = models.SlugField()
    latandlong = "0.000, 0.0000"
    my_search_query = models.CharField(max_length=250)
    wanna_check_distance = models.BooleanField(default=True)
    initialize = models.CharField(default="N", max_length=1)

    # Metadata
    class Meta:
        ordering = ['-my_query']

    # Methods
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return str(self.my_query).upper()

    def get_url(self):
        return reverse("queries", kwargs={"id": self.id, "slug": self.slug})

    def find_ads(self):
        # starting Selenium
        driver_ctrl = SeleniumCtrl()
        driver_plain = SeleniumCtrl.browser
        comfirm = "default"

        # get rid of Google's privacy pop up
        polish = True
        while polish:
            print("ridding of Google privacy policy: policy is gonna be accepted\n")
            polish = driver_ctrl.get_rid_of_contract()
        time.sleep(2)

        # go to Google search page and wait for prompt
        google_bar = driver_ctrl.start_google()

        # start searching contents; send query to google search box
        google_bar.send_keys(str(self.my_search_query).replace("b'", "").replace("'", ""))
        google_bar.send_keys(Keys.ENTER)
        count = 0

        # read or initialize the csv file + create Pandas DataFrame
        if self.initialize.capitalize() == "Y":
            are_u_sure = "Y"
            if are_u_sure.capitalize() == "Y":
                df = pd.DataFrame()
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

                # create old file back-up into CSVs folder
                if os.path.isfile("result.csv"):
                    df_backup = pd.read_csv("result.csv")
                    cpt = sum([len(files) for r, d, files in os.walk("CSVs")])
                    df_backup.to_csv("CSVs/backup_" + str(cpt + 1) + ".csv")
                    # delete the database from memory
                    df_backup = None

                # initialize empty csv
                df.to_csv("result.csv")
            else:
                # print("\nReading from previous database\n")
                df = pd.read_csv("result.csv")
        else:
            # initialize DataFrame from CSV file
            df = pd.read_csv("result.csv")
        changed = False

        # vars
        not_checked_range_a_yet = True
        not_checked_range_b_yet = True
        extracted_ads_list = []
        extracted_ads_list_b = []

        # here goes the MAIN PROCESS
        while on_run:

            # wait for new page to be loaded
            not_loaded = True
            not_loaded_contract = True
            Utilis.waiter()

            if not default_loc:
                if not changed:
                    changed = Utilis.change_geolocation()
                    print("changed", changed)

            # as page is loaded, gather the source code of the page
            my_raw_source = driver_ctrl.get_source()
            # extract the ADS part only with BS
            soup = BS.BeautifulSoup(my_raw_source, "html.parser")

            if not soup.find_all(id="tads") and not soup.find_all(id="tadsb"):
                no_tads = True
                accepted = False

                while no_tads and not accepted:
                    # controllo "sei sicuro di monitorare questa ricerca [Y/N], oppure procedere a una nuova?"
                    if first_run:
                        print("no ads found, keep this search or try a new search\n")
                        print("do you wanna keep tracking of this search-key? [y/N]\n")
                        print("\n")
                        comfirm = input()
                        change_geo_loc = input("do you wanna change de geolocation? y/N\n-> ")
                        print(change_geo_loc)

                        while change_geo_loc.capitalize() != "Y" and change_geo_loc.capitalize() != "N":
                            print("please insert a valid answer\n->")
                            change_geo_loc = input()
                        if change_geo_loc.capitalize() == "Y":
                            changed = False
                            splittable = False

                            df_latandlong = pd.read_csv("location.csv")
                            print(df_latandlong, "\nChoose also a registered location by name:\n")
                            latandlong = input("here choose new geo-loc, insert latitude and longitude x.xxxx, y.yyyy format:\n->")

                            # repeat form for geolocation -> to be reduced to fun(!)
                            while not splittable:
                                latandlong = latandlong.split(", ")
                                try:
                                    if latandlong[0] and latandlong[1]:
                                        is_double = False
                                        # print(latandlong, "inside second try")
                                        while not is_double:
                                            if float(latandlong[0]) and float(latandlong[1]):
                                                splittable = True
                                                is_double = True
                                            else:
                                                print("please use only numbers: insert lat and long again")
                                                latandlong = input("try insert a valid lat and long again:\n-> ")

                                except:
                                    print("lat and long are wrong in format. Here is your input:", latandlong)
                                    print(
                                        "insert a valid format for latitude and longitude: 'x.xxx, y,yyyy' check the numbers and the separator ', ' between them")
                                    print("\nyou can try to insert a stored location again: \n\n")
                                    latandlong = input("try insert a valid lat and long again:\n-> ")

                                    # here try again to use stored info
                                    try:
                                        latandlong = str(df_latandlong.loc[latandlong, "latandlong"])
                                        print(latandlong)
                                    except KeyError:
                                        pass  # eventually insert debug here

                            lat = latandlong[0]
                            long = latandlong[1]

                            geo_preference = "geo.wifi.uri"
                            geo_preference_value = 'data:application/json,{"location": {"lat": ' + lat + ', "lng": ' + long + '}, "accuracy": 100.0}'

                            Utilis.reset_geo(geo_preference, geo_preference_value)
                            Utilis.waiter()
                            Utilis.change_geolocation()

                        elif change_geo_loc.capitalize() == "N":
                            print("continue with previous: " + str(latandlong))

                        while comfirm.capitalize() != "Y" and comfirm.capitalize() != "N":
                            print(
                                "insert a choose: Y for keep tracking this search, N to go back and choose new opt.\n")
                            print("do you wanna keep tracking of this search-key? [y/N]\n")
                            comfirm = input()

                        if comfirm.capitalize() == "N":
                            while comfirm.capitalize() == "N":
                                google_bar = driver_ctrl.start_google()
                                print("insert your keyword for the company you wanna track\n- ")

                                self.my_search_query = input()
                                self.my_search_query = str(self.my_search_query).replace("b'", "").replace("'", "")
                                google_bar.send_keys(self.my_search_query)
                                google_bar.send_keys(Keys.ENTER)

                                Utilis.waiter()

                                first_run = True
                                my_raw_source = driver_ctrl.get_source()
                                soup = BS.BeautifulSoup(my_raw_source, "html.parser")

                                if not soup.find_all(id="tads") and not soup.find_all(id="tadsb"):
                                    no_tads = True
                                    print(
                                        "no ads found, keep this search, try a new search or change the geolocation options\n")
                                    print("do you wanna keep tracking of this search-key? [y/N]\n")
                                    print("\n")
                                    comfirm = input()
                                else:
                                    comfirm = "Y"
                                    no_tads = False
                                    first_run = False

                        # gestisce assenza di annunci ADs al PRIMO avvio
                        else:
                            first_run = False
                            accepted = True
                            time_now = datetime.datetime.now()

                            if count != 0:
                                count += 1
                            comfirm = "Y"
                            print("controlling for ADS activation status\n" + str(count) + " count\n" + str(
                                time_now) + " for query: " + str(self.my_search_query).replace("b'", "").replace("'", "") + "\n")

                            df = Utilis.no_ads_found(df, time_now, self.my_search_query, resting_time)

                        print("\n")

                    # gestisce assenza di annunci ADs DOPO il primo avvio
                    else:
                        time_now = datetime.datetime.now()
                        if count != 0:
                            count += 1
                        comfirm = "Y"
                        print("controlling for ADS activation status\n" + str(count) + " count\n" + str(
                            time_now) + " for query: " + str(self.my_search_query).replace("b'", "").replace("'", "") + "\n")

                        df = Utilis.no_ads_found(df, time_now, self.my_search_query, resting_time)
                        no_tads = False
            else:
                no_tads = False

            # memorizza dentro il csv la query e l'assenza degli annunci
            if no_tads:
                count += 1
                print("\nstart entry\n")
                print("tags doesn't exists\n")
                print(
                    str(count) + " count\n" + str(time_now) + "ADS  for key searched: \"" + str(self.my_search_query).replace("b'",
                                                                                                                  "").replace(
                        "'", "") + "\" NOT ACTIVE\n")
                print("end entry\n\n")

                time.sleep(resting_time)
                time_now = datetime.datetime.now()
                driver_plain.refresh()

            # memorizza le tabelle: valori ritrovati
            else:
                count += 1
                tag_tads = soup.find(id="tads")
                tag_tadsb = soup.find(id="tadsb")

                if tag_tads or tag_tadsb:
                    first_run = False
                    print("\nstart entry\n")

                    # try to create <h3> tag reader for entried in tads
                    h3_data_alpha = None
                    h3_data_beta = None
                    try:
                        text_tag = tag_tads.text
                        h3_tag = tag_tads("h3")
                        h3_data_alpha = h3_tag
                        h3_tag = Utilis.polish_list(h3_tag, terminal=False, for_h3=True)

                        set_one = set(extracted_ads_list)
                        set_two = set(h3_tag)
                        extracted_ads_list.extend(h3_tag)
                        extracted_ads_list = Utilis.f5(extracted_ads_list)

                        tads_true = True
                    except AttributeError:
                        tads_true = False

                    # try to create <h3> tag reader for entries in tadsb
                    try:
                        text_tag_b_b = tag_tadsb.text
                        h3_tag_b = tag_tadsb("h3")
                        h3_data_beta = h3_tag_b
                        h3_tag_b = Utilis.polish_list(h3_tag_b, terminal=False, for_h3=True)

                        set_one_b = set(extracted_ads_list_b)
                        set_two_b = set(h3_tag_b)
                        extracted_ads_list_b.extend(h3_tag_b)
                        extracted_ads_list_b = Utilis.f5(extracted_ads_list_b)

                        tadsb_true = True
                    except AttributeError:
                        tadsb_true = False

                    time_now = datetime.datetime.now()

                    # end process the announces
                    if tads_true:
                        output = style.RESET("_____") + style.RESET("\nMain ADS -") + "\ncycle number: " + str(
                            count) + "\n" + Utilis.polish_list(h3_tag) + "\n" + style.BOLD(
                            str(time_now)) + "\n - " + style.BOLD("ads ALPHA ACTIVE\n_____\n")

                        # store datas in csv with Pandas
                        for i, item in enumerate(h3_data_alpha):
                            data_alpha = {"n. in session": str(i), "datetime": str(time_now),
                                          "website title": Utilis.polish_list(item, terminal=False, string_mode=True),
                                          "kind": "ADS A",
                                          "location (coordinates)": str(latandlong[0]) + "_" + str(latandlong[1]),
                                          "location (name)": "to be implemented", "query": self.my_search_query}
                            data_alpha = pd.Series(data_alpha)
                            df = df.append(data_alpha, ignore_index=True)
                            # print(df) # print dataframe: useful in debugging
                            df.to_csv("result.csv")

                        # here method if it's been chosen "yes", to check also at 5, 10 and 20 km
                        link = driver_plain.current_url
                        if self.wanna_check_distance:
                            if h3_data_alpha:
                                if len(set_one.intersection(set_two)) < len(set_two):
                                    not_checked_range_a_yet = True
                                else:
                                    not_checked_range_a_yet = True

                                if not_checked_range_a_yet:  # implement check range control for extracte h3 titles and not for tads boxes
                                    check_range = PrepareLocation(lat, long, link, h3_data_alpha, my_raw_source, df,
                                                                  str(time_now), is_tads=True).get_in_range()
                                    not_checked_range_a_yet = True
                            else:
                                print(h3_data_alpha, "h3 data alpha should be null?")
                                pass

                    else:
                        output = "\nno Main ADS to report\n" + str(time_now) + "\n"

                    if tag_tadsb:
                        outputb = style.RESET("_____\n") + style.BOLD("Bottom ADS -") + style.RESET(
                            "\ncycle number: ") + str(count) + "\n" + Utilis.polish_list(h3_tag_b) + "\n" + style.BOLD(
                            str(time_now)) + style.RESET("\n - ") + style.BOLD("ads BETA ACTIVE") + style.RESET(
                            "\n_____\n")

                        # store datas in csv with Pandas
                        for i, item in enumerate(h3_data_beta):
                            data_alpha = {"n. in session": str(i), "datetime": str(time_now),
                                          "website title": Utilis.polish_list(item, terminal=False, string_mode=True),
                                          "kind": "ADS B",
                                          "location (coordinates)": str(latandlong[0]) + "_" + str(latandlong[1]),
                                          "location (name)": "to be implemented", "query": self.my_search_query}
                            data_alpha = pd.Series(data_alpha)
                            df = df.append(data_alpha, ignore_index=True)
                            # print(df)
                            df.to_csv("result.csv")

                        # here method if it's been chosen "yes", to check also at 5, 10 and 20 km - method runs ONLY one time for h3 entry
                        link = driver_plain.current_url
                        if self.wanna_check_distance:
                            if h3_data_beta:
                                if len(set_one_b.intersection(set_two_b)) < len(set_two_b):
                                    not_checked_range_b_yet = True
                                else:
                                    not_checked_range_b_yet = True

                                if not_checked_range_b_yet:
                                    check_range = PrepareLocation(lat, long, link, h3_data_beta, my_raw_source, df,
                                                                  str(time_now), is_tadsb=True).get_in_range()
                                    not_checked_range_b_yet = True
                            else:
                                print(h3_data_beta, "h3 data beta should be null?")
                                pass

                    else:
                        outputb = "\nno Bottom ADS to report\n" + str(time_now) + "\n"

                    print(str(output))
                    print(str(outputb))
                    print("end entry\n")

                    # activate thread for loading bar - it must be add a rectangle box
                    bar_thread = LoadBar("bar thread - found", resting_time)
                    bar_thread.start()

                    count += 1
                    time.sleep(resting_time + 2)
                    driver_plain.refresh()
                else:
                    count += 1
                    first_run = False
                    print("\nstart entry\n")
                    print("tags doesn't exists\n")

                    time_now = datetime.datetime.now()
                    output = str(count) + " " + str(time_now) + " " + "ADS NOT ACTIVE"
                    print(str(output))
                    print("end entry")

                    bar_thread = LoadBar("bar thread - not found", resting_time)
                    bar_thread.start()

                    time.sleep(resting_time + 2)
                    driver_plain.refresh()

        driver_plain.close()


