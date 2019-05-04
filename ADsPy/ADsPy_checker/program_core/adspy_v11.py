import datetime
import os
import sys
import re
import time
from threading import Thread
import bs4 as BS
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import wait as Wait
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.common.exceptions import ElementNotInteractableException as ENIE
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import numpy
import pandas as pd

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

'''Class Space'''


class style():
    BLACK = lambda x: '\033[30m' + str(x)
    RED = lambda x: '\033[31m' + str(x)
    GREEN = lambda x: '\033[32m' + str(x)
    YELLOW = lambda x: '\033[33m' + str(x)
    BLUE = lambda x: '\033[34m' + str(x)
    MAGENTA = lambda x: '\033[35m' + str(x)
    CYAN = lambda x: '\033[36m' + str(x)
    WHITE = lambda x: '\033[37m' + str(x)
    UNDERLINE = lambda x: '\033[4m' + str(x)
    RESET = lambda x: '\033[0m' + str(x)
    BOLD = lambda x: '\033[1m' + str(x)


class LoadBar(Thread):

    def __init__(self, thread_name, duration):
        Thread.__init__(self)
        self.duration = duration
        self.name = thread_name

    def run(self):
        duration = self.duration
        start_duration = self.duration
        divider = self.duration / 60
        print(duration, divider)
        while duration >= 0:
            sys.stdout.write('\r\r' + "[" + "#" * (int(self.duration / divider) - int(duration / divider)) + " " * int(
                duration / divider) + "]")
            duration -= 1
            time.sleep(1)


class PrepareLocation:

    def __init__(self, latitude, longitude, url_link, h3_data, page_sourced_saved, df, datetime, is_tads=False,
                 is_tadsb=False):
        self.latitude = latitude
        self.longitude = longitude
        self.url_link = url_link

        h3_list = []
        for item in h3_data:
            item = re.sub(re.compile("<h3 class=\"[A-Za-z0-9]+\"[>]*"), "", str(item).replace("</h3>", ""))
            h3_list.append(item)

        # self.h3 = h3_data
        self.h3 = h3_list
        self.page_source = page_sourced_saved
        self.is_tads = is_tads
        self.is_tadsb = is_tadsb
        self.sub_df = df
        self.datetime = datetime

        # process self.h3
        # print(self.h3, "self h3", type(self.h3))
        self.h3 = Utilis.polish_list(self.h3, terminal=False)
        # print(self.h3, "self h3", type(self.h3))

    def print_to_pandas_looper(self, my_source, datetime, km, main):
        df = self.sub_df
        if main:
            for element in my_source:
                element = element.strip("\n")
                element = element.strip(" ")
                # print(element, "element in for", self.h3, "for comparison")

                if element in self.h3:
                    element = element.strip("\u200e")
                    element = element + "\u200e"
                    # datetime = str(datetime).strip("\u200e")

                    for match in self.h3:
                        match = match.strip("\u200e")
                        match = match + "\u200e"
                        if element == match or element in match:
                            df.loc[(df["website title"] == element) & (df["datetime"] == datetime), km] = ["True"]
                        else:
                            df.loc[(df["website title"] == match) & (df["datetime"] == datetime), km] = ["False"]
                else:
                    pass
        else:
            # print("tads - else")
            for element in self.h3:
                element = element.strip("\u200e")
                element = element + "\u200e"
                # print("element in else for tads: ", element)
                # gestisce errore nel caso in cui compaia un elemento NON registrato in precedenza (per cui il controllo a 5 o più km è infattibile)
                df.loc[(df["website title"] == element) & (df["datetime"] == datetime), km] = "No ADS"

    def get_in_range(self, driver_ctrl, soup, csv_address, my_search_query):
        # get next measure for 2, 5 and 20 km
        df = self.sub_df
        self.csv_address = csv_address
        latitude = self.latitude
        latitude_1 = float(latitude) + 0.046  # latitude + 5 km
        latitude_2 = float(latitude_1) + 0.046  # latitude + 10 km
        latitude_3 = float(latitude_2) + 0.046 * 2  # latitude + 20 km
        lat_list = [latitude_1, latitude_2, latitude_3]
        datetime = self.datetime

        check_driver = None
        for k, item in enumerate(lat_list):
            km = 0
            if k == 0:
                km = "presence at 5 km"
                check_driver = driver_ctrl.browser_1
            elif k == 1:
                check_driver = driver_ctrl.browser_2
                km = "presence at 10 km"
            else:
                km = "presence at 20 km"
                check_driver = driver_ctrl.browser_3

            # go to previous page to check if tads and tasb are mantained at 5, 10 and 20 km
            check_driver.get(self.url_link)
            Utilis.waiter(driver_ctrl.browser)
            Utilis.change_geolocation_check(check_driver, k, km)
            Utilis.waiter(driver_ctrl.browser)

            # check for tads and tadsb
            # first check for the tads boxes, then for contents, for previusly included h3 tags
            # then export the check to be added into DataFrame columns: 5 km, 10 km and 20 km.
            # This keep tracks of campaign set in a close range to the company
            my_page = check_driver.page_source
            my_soup = BS.BeautifulSoup(my_page, "html.parser")

            if self.is_tads:
                # print("inside is tads")
                if my_soup.find(id="tads"):
                    # print("inside tads - 2")
                    # here sub-check for h3 - process list
                    new_h3 = soup.find(id="tads")("h3")
                    new_h3 = Utilis.polish_list(new_h3, terminal=False)
                    self.print_to_pandas_looper(new_h3, datetime, km, True)
                else:
                    self.print_to_pandas_looper(None, datetime, km, False)

            elif self.is_tadsb:
                # print("inside tadsb")
                if my_soup.find(id="tadsb"):
                    # print("inside tadsb - 2")
                    new_h3_b = soup.find(id="tadsb")("h3")
                    new_h3_b = Utilis.polish_list(new_h3_b, terminal=False)
                    self.print_to_pandas_looper(new_h3_b, datetime, km, True)
                else:
                    self.print_to_pandas_looper(None, datetime, km, False)

            else:
                print("this else is an error - line ~197")

            # here append to Pandas sub_df, instead of returning answers.
            df.to_csv("{}result_{}.csv".format(self.csv_address, my_search_query))

        return self.sub_df, self.page_source

    def get_geo_names(self):
        # here google APIs to get name for latitude and longitude
        pass


class Utilis:
    def __init__(self):
        pass

    def f5(seq, idfun=None):
        # order preserving
        if idfun is None:
            def idfun(x): return x
        seen = {}
        result = []
        for item in seq:
            marker = idfun(item)

            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        return result

    @staticmethod
    def no_ads_found(dataframe, my_time, the_query, pause_time, csv_address):
        no_ads_data = {"n. in session": numpy.nan, "datetime": str(my_time), "website title": "Not Available",
                       "kind": "NO ADS BOXES", "location (coordinates)": str(latandlong[0]) + "_" + str(latandlong[1]),
                       "location (name)": "to be implemented", "query": the_query}
        no_ads_data = pd.Series(no_ads_data)
        dataframe = dataframe.append(no_ads_data, ignore_index=True)
        dataframe.to_csv("{}result_{}.csv".format(csv_address, the_query))
        no_ads_data = None
        bar_thread = LoadBar("bar thread - found", resting_time - 1)
        bar_thread.start()
        time.sleep(pause_time)

        return dataframe

    @staticmethod
    def polish_list(my_list, terminal=True, string_mode=False, for_h3=False):

        if for_h3:
            my_list = [str(item).replace("</h3>", "") for item in my_list]
            my_list = [re.sub(re.compile("<h3 class=\"[A-Za-z0-9]+\"[>]*"), "", item) for item in my_list]
        else:
            if not string_mode:
                my_list = [re.sub(re.compile("<h3 class=\"[A-Za-z0-9]+\"[>]*"), "", str(item)) for item in my_list]
                my_list = [str(item).replace("</h3>", "").replace(str("\u200e"), "") for item in my_list]
            else:
                my_list = re.sub(re.compile("<h3 class=\"[A-Za-z0-9]+\"[>]*"), "", str(my_list).replace("</h3>", ""))

        # optional, for outputs in terminal
        if terminal:
            my_list = str(my_list).replace("['", "    ").replace("']", "").replace("', ", "\n    ")

        return my_list

    @staticmethod
    def waiter(driver_plain):
        not_load = True
        while not_load:
            try:
                Wait(driver_plain, 2).until(
                    lambda browsed: browsed.find_element_by_css_selector(
                        '#resultStats').is_displayed())
                if driver_plain.find_element_by_css_selector('#resultStats'):

                    # print("page loaded\n")

                    not_load = False
                else:
                    print("page not loaded\n")

                    not_load = True
            except:
                print("into except for loading page\n")

                not_load = True

    @staticmethod
    def waiter_loc(previous_loc, driver_plain):
        not_load = True
        counter = 0
        while not_load:
            try:
                Wait(driver_plain, 2).until(
                    lambda browsed: browsed.find_element_by_css_selector('#swml-loc').is_displayed())
                if driver_plain.find_element_by_css_selector('#swml-loc').text != previous_loc:
                    print(
                        "\npage loaded, previous:" + previous_loc + ", present: " + driver_plain.find_element_by_css_selector(
                            '#swml-loc').text + "\n")
                    not_load = False
                else:
                    counter += 1
                    not_load = True
            except TimeoutException as e:
                print("Timeout reached: trying different page setting\n", )
                try:
                    Wait(driver_plain, 2).until(
                        lambda browsed: browsed.find_element_by_css_selector('#Wprf1b').is_displayed())
                    if driver_plain.find_element_by_css_selector('#Wprf1b').text != previous_loc:
                        print(
                            "\npage loaded, previous:" + previous_loc + ", present: " + driver_plain.find_element_by_css_selector(
                                '#Wprf1b').text + "\n")
                        not_load = False
                    else:
                        counter += 1
                        not_load = True
                except TimeoutException as e:
                    print("into except for loading page - Abort\n", )
                    not_load = True
                    sys.exit()

    @staticmethod
    def waiter_loc_check(previous_loc, driver):
        not_load = True
        counter = 0
        try:
            Wait(driver, 2).until(lambda browsed: browsed.find_element_by_css_selector('#swml-loc').is_displayed())
            if driver.find_element_by_css_selector('#swml-loc').text != previous_loc:
                print("\npage loaded, previous:" + previous_loc + ", present: " + driver.find_element_by_css_selector(
                    '#swml-loc').text + "\n")
                not_load = False
            else:
                counter += 1
                not_load = True
        except TimeoutException:
            print("Timeout reached: trying different page setting for check\n", )
            try:
                Wait(driver, 2).until(lambda browsed: browsed.find_element_by_css_selector('#Wprf1b').is_displayed())
                if driver.find_element_by_css_selector('#Wprf1b').text != previous_loc:
                    print(
                        "\npage loaded, previous:" + previous_loc + ", present: " + driver.find_element_by_css_selector(
                            '#Wprf1b').text + "\n")
                    not_load = False
                else:
                    counter += 1
                    not_load = True
            except TimeoutException as e:
                print("into except for loading page - Abort\n", )
                not_load = True
                sys.exit()

    @staticmethod
    def change_geolocation(driver_plain, page_source=None):
        try:
            Wait(driver_plain, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="swml-upd"]')))
            get_precise = driver_plain.find_element_by_css_selector("#swml-upd")
            get_precise_text = driver_plain.find_element_by_id("swml-loc").text
        except TimeoutException as e:
            Wait(driver_plain, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="eqQYZc"]')))
            get_precise = driver_plain.find_element_by_css_selector("#eqQYZc")
            get_precise_text = driver_plain.find_element_by_id("Wprf1b").text

        try:
            print("trying to change loc and lat and long: " + str(latandlong))
            get_precise.click()
        except ENIE:
            print("click into exception")

        Utilis.waiter_loc(get_precise_text, driver_plain)
        driver_plain.refresh()
        Wait(driver_plain, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/div[3]/div[11]/div/div/div/div[1]')))

        return True

    @staticmethod
    def change_geolocation_check(driver, num, presence):
        try:
            Wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="swml-upd"]')))
            get_precise = driver.find_element_by_css_selector("#swml-upd")
            get_precise_text = driver.find_element_by_id("swml-loc").text
        except TimeoutException as e:
            Wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="eqQYZc"]')))
            get_precise = driver.find_element_by_css_selector("#eqQYZc")
            get_precise_text = driver.find_element_by_id("Wprf1b").text

        try:
            print("trying to change loc and lat and long: " + str(latandlong), "round: " + str(num), "for: " + presence)
            get_precise.click()
        except ENIE:
            print("click into exception")

        Utilis.waiter_loc_check(get_precise_text, driver)
        driver.refresh()
        Wait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/div[3]/div[11]/div/div/div/div[1]')))

        return True

    @staticmethod
    def reset_geo(pref, val):
        options = Options()
        options.add_argument('-headless')
        profile = webdriver.FirefoxProfile("/home/gabri/PycharmProjects/ADsPy/profile")
        # profile  = webdriver.FirefoxProfile("C:\\Users\Gabri\Documents\ADsPy\profile")
        profile.set_preference("geo.prompt.testing", True)
        profile.set_preference("geo.prompt.testing.allow", True)
        profile.set_preference("geo.enabled", True)
        profile.set_preference(pref, val)

        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        cap['loggingPrefs'] = {'browser': 'ALL'}

        # driver_plain.firefox_profile.set_preference(pref, val)
        current_url = driver_plain.current_url
        driver_plain.close()
        driver_plain.start_session(cap, profile)
        polish = True
        while polish:
            print("ridding of Google privacy policy: policy is gonna be accepted\n")
            polish = driver_ctrl.get_rid_of_contract()

        driver_plain.get(current_url)


class SeleniumCtrl:

    def __init__(self, prof, prof_one, prof_two, prof_three, csv_add, laandlo):

        global profile_zero
        global profile_one
        global profile_two
        global profile_three
        global csv_address

        print(prof, "prof", prof_one, "prof one", prof_two, "prof two", prof_three, "prof three", csv_add, "csv address", laandlo, "latandlong")

        headless = True

        profile_zero = prof
        profile_one = prof_one
        profile_two = prof_two
        profile_three = prof_three
        csv_address = csv_add
        latandlong = laandlo

        self.profile_zero = prof
        self.profile_one = prof_one
        self.profile_two = prof_two
        self.profile_three = prof_three
        self.csv_address = csv_add
        self.latandlong = latandlong
        # print("\n\nself.latandlong {} and latandlong {}\n\n".format(self.latandlong, latandlong))

        options = Options()
        options.add_argument('-headless')
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        cap['loggingPrefs'] = {'browser': 'ALL'}

        # profile  = webdriver.FirefoxProfile("C:\\Users\Gabri\Documents\ADsPy\profile")
        profile = webdriver.FirefoxProfile(profile_one)
        profile.set_preference("geo.prompt.testing", True)
        profile.set_preference("geo.prompt.testing.allow", True)
        profile.set_preference("geo.enabled", True)

        profile_1 = webdriver.FirefoxProfile(profile_directory=profile_one)
        profile_1.set_preference("geo.prompt.testing", True)
        profile_1.set_preference("geo.prompt.testing.allow", True)
        profile_1.set_preference("geo.enabled", True)

        profile_2 = webdriver.FirefoxProfile(profile_two)
        profile_2.set_preference("geo.prompt.testing", True)
        profile_2.set_preference("geo.prompt.testing.allow", True)
        profile_2.set_preference("geo.enabled", True)

        profile_3 = webdriver.FirefoxProfile(profile_three)
        profile_3.set_preference("geo.prompt.testing", True)
        profile_3.set_preference("geo.prompt.testing.allow", True)
        profile_3.set_preference("geo.enabled", True)

        splittable = False
        loc_address = os.path.join(csv_address, "location.csv")

        # read locations stored in the editable "location.csv" - it's easy to add a tag in the column "places" and a set of coordinates in the col "latandlong"
        df_latandlong = pd.read_csv(loc_address)
        # set places as index
        df_latandlong = df_latandlong.set_index("places", drop=False)
        print("\n", df_latandlong, "\n\nchoose a place stored in memory or insert a new coordinate\n")

        # latandlong = input("please insert latitude and longitude -> (x.xxxx, y.yyyy use comma and space as separator and dot as decimal indicator)\ninsert 'default' to use current real location\n -> ")

        # retrieve data from pd DataFrame, if input matches a stored location
        try:
            latandlong = str(df_latandlong.loc[latandlong, "latandlong"])
            print(latandlong)
        except KeyError:
            pass  # eventually insert debug here

        global default_loc
        if latandlong != "default":
            default_loc = False
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
                    print("\nyou can try to insert a stored location again: \n\n"
                          "")
                    latandlong = input("try insert a valid lat and long again:\n-> ")

                    # here try again to use stored info
                    try:
                        latandlong = str(df_latandlong.loc[latandlong, "latandlong"])
                        print(latandlong)
                    except KeyError:
                        pass  # eventually insert debug here
        else:
            default_loc = True

        print(latandlong)

        global lat, long
        lat = latandlong[0]
        long = latandlong[1]
        self.lat = lat
        self.long = long

        if not default_loc:
            profile.set_preference("geo.wifi.uri",
                                   'data:application/json,{"location": {"lat": ' + lat + ', "lng": ' + long + '}, "accuracy": 100.0}')

            # set distances for further checks
            profile_1.set_preference("geo.wifi.uri", 'data:application/json,{"location": {"lat": ' + str(
                float(lat) + 0.046) + ', "lng": ' + long + '}, "accuracy": 100.0}')
            profile_2.set_preference("geo.wifi.uri", 'data:application/json,{"location": {"lat": ' + str(
                float(lat) + 0.046 * 2) + ', "lng": ' + long + '}, "accuracy": 100.0}')
            profile_3.set_preference("geo.wifi.uri", 'data:application/json,{"location": {"lat": ' + str(
                float(lat) + 0.046 * 4) + ', "lng": ' + long + '}, "accuracy": 100.0}')

        else:
            profile.set_preference("geo.wifi.uri",
                                   'data:application/json,{"location": {"lat": <lat>, "lng": <long>}, "accuracy": 100.0}')
            print("using actual geolocation - error with other profiles")

        if headless:
            browser = webdriver.Firefox(profile, capabilities=cap, options=options)
            browser_1 = webdriver.Firefox(profile_1, capabilities=cap, options=options)
            browser_2 = webdriver.Firefox(profile_2, capabilities=cap, options=options)
            browser_3 = webdriver.Firefox(profile_3, capabilities=cap, options=options)

            self.browser = browser
            self.browser_1 = browser_1
            self.browser_2 = browser_2
            self.browser_3 = browser_3
            self.latandlong = latandlong

    def go_to_page(self, my_url):
        driver = self.browser
        driver.get(my_url)

    # it starts the program in Google page for search - it retrivies the bar waiting for prompt
    def start_google(self):
        driver = self.browser
        driver.get("https://www.google.com")
        google_bar = driver.find_element_by_css_selector(".gLFyf")
        return google_bar

    def get_series_data(self, script):
        # script = 'return JSON.stringify(res[0].PeformanceData)'
        my_log = self.browser.execute_script(script)
        return my_log

    def get_source(self):
        driver = self.browser
        my_raw_source = driver.page_source
        return my_raw_source

    # get rid of privacy contract with google (it would block navigation)
    def get_rid_of_contract(self):
        time.sleep(5)
        driver = self.browser
        driver_1 = self.browser_1
        driver_2 = self.browser_2
        driver_3 = self.browser_3
        driver_list = [driver, driver_1, driver_2, driver_3]
        for driver in driver_list:
            driver.get(
                "https://consent.google.com/ui/?continue=https://www.google.com/&origin=https://www.google.com&if=1&gl=IT&hl=it&pc=s")
            not_loaded = True
            # print("check before while")

            while not_loaded:
                try:
                    Wait(driver, 1).until(
                        lambda browsed: browsed.find_element_by_css_selector('#yDmH0d').is_displayed())
                    if driver.find_element_by_css_selector('#yDmH0d'):
                        # print("page loaded")
                        not_loaded = False
                    else:
                        print("page not loaded")
                        not_loaded = True
                except:
                    print("into except for loading page_5")
                    not_loaded = True

            my_magic_button = driver.find_element_by_css_selector("#agreeButton")
            my_page_body = driver.find_element_by_css_selector("body")
            my_page_body.send_keys(Keys.END)
            time.sleep(2)
            my_magic_button.click()
            time.sleep(2)

        return False


class ADsPyManager:

    def __init__(self, prof, prof_one, prof_two, prof_three, csv_address, my_search_query, initialize, wanna_check_distance, latandlong):

        self.my_search_query = my_search_query
        self.prof = prof
        self.prof_one = prof_one
        self.prof_two = prof_two
        self.prof_three = prof_three
        self.csv_address = csv_address
        self.initialize = initialize
        self.wanna_check_distance = wanna_check_distance
        self.latandlong = latandlong
        print("\n\nin ADSPYManager: self.latandlong {} and latandlong {}\n\n".format(self.latandlong, latandlong))

    @staticmethod
    def initialize_df(csv_address, my_query, initializing=False):
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

        '''# create old file back-up into CSVs folder
        if os.path.isfile("result.csv"):
            df_backup = pd.read_csv("result.csv")
            cpt = sum([len(files) for r, d, files in os.walk("CSVs")])
            df_backup.to_csv("CSVs/backup_" + str(cpt + 1) + ".csv")
            # delete the database from memory
            df_backup = None'''

        # initialize empty csv
        df.to_csv("{}result_{}.csv".format(csv_address, my_query))
        if initializing:
            return df


    def find_ads(self, prof=None, prof_one=None, prof_two=None, prof_three=None, csv_address=None, my_search_query=None, initialize=None, wanna_check_distance=None, latandlong=None):

        if prof:
            self.prof = prof
        if prof_one:
            self.prof_one = prof_one
        if prof_two:
            self.prof_two = prof_two
        if prof_three:
            self.prof_three = prof_three
        if csv_address:
            self.csv_address = csv_address
        if my_search_query:
            self.my_search_query = my_search_query
        if initialize:
            self.initialize = initialize
        if wanna_check_distance:
            self.wanna_check_distance = wanna_check_distance
        if latandlong:
            self.latandlong = latandlong
        else:
            self.latandlong = "Seppia"

        # starting Selenium
        driver_ctrl = SeleniumCtrl(self.prof, self.prof_one, self.prof_two, self.prof_three, self.csv_address, self.latandlong)
        driver_plain = driver_ctrl.browser
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
                self.initialize_df(self.csv_address, self.my_search_query)
            else:
                # print("\nReading from previous database\n")
                df = pd.read_csv("{}result_{}.csv".format(self.csv_address, self.my_search_query), index_col=0)
        else:
            # initialize DataFrame from CSV file
            exists = os.path.isfile("{}result_{}.csv".format(self.csv_address, self.my_search_query))
            if exists:
                # Store configuration file values
                df = pd.read_csv("{}result_{}.csv".format(self.csv_address, self.my_search_query), index_col=0)
            else:
                # Keep presets
                df = self.initialize_df(self.csv_address, self.my_search_query, initializing=True)

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
            Utilis.waiter(driver_plain)

            if not default_loc:
                if not changed:
                    changed = Utilis.change_geolocation(driver_plain, page_source=driver_plain.page_source)
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

                            df_latandlong = pd.read_csv(self.csv_address + "location.csv")
                            print(df_latandlong, "\nChoose also a registered location by name:\n")
                            # latandlong = input("here choose new geo-loc, insert latitude and longitude x.xxxx, y.yyyy format:\n->")
                            latandlong = driver_ctrl.latandlong

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
                            Utilis.waiter(driver_plain)
                            Utilis.change_geolocation(driver_plain)

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

                                Utilis.waiter(driver_plain)

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

                            df = Utilis.no_ads_found(df, time_now, self.my_search_query, resting_time, self.csv_address)

                        print("\n")

                    # gestisce assenza di annunci ADs DOPO il primo avvio
                    else:
                        time_now = datetime.datetime.now()
                        if count != 0:
                            count += 1
                        comfirm = "Y"
                        print("controlling for ADS activation status\n" + str(count) + " count\n" + str(
                            time_now) + " for query: " + str(self.my_search_query).replace("b'", "").replace("'", "") + "\n")

                        df = Utilis.no_ads_found(df, time_now, self.my_search_query, resting_time, self.csv_address)
                        no_tads = False
            else:
                no_tads = False

            # memorizza dentro il csv la query e l'assenza degli annunci
            if no_tads:
                count += 1
                print("\nstart entry\n")
                print("tags doesn't exists\n")
                print(
                    str(count) + " count\n" + str(time_now) + "ADS  for key searched: \"" + str(self.my_search_query).replace("b'", "").replace(
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
                            data_alpha = {"alpha": 0, "n. in session": str(i), "datetime": str(time_now),
                                          "website title": Utilis.polish_list(item, terminal=False, string_mode=True),
                                          "kind": "ADS A",
                                          "location (coordinates)": str(driver_ctrl.latandlong[0]) + "_" + str(driver_ctrl.latandlong[1]),
                                          "location (name)": "to be implemented", "query": self.my_search_query}
                            data_alpha = pd.Series(data_alpha)
                            df = df.append(data_alpha, ignore_index=True)
                            df.to_csv("{}result_{}.csv".format(self.csv_address, self.my_search_query))

                        # here method if it's been chosen "yes", to check also at 5, 10 and 20 km
                        link = driver_plain.current_url
                        if self.wanna_check_distance:
                            if h3_data_alpha:
                                if len(set_one.intersection(set_two)) < len(set_two):
                                    not_checked_range_a_yet = True
                                else:
                                    not_checked_range_a_yet = True

                                if not_checked_range_a_yet:  # implement check range control for extracte h3 titles and not for tads boxes
                                    check_range = PrepareLocation(driver_ctrl.lat, driver_ctrl.long, link, h3_data_alpha, my_raw_source, df, str(time_now), is_tads=True).get_in_range(driver_ctrl, soup, csv_address, self.my_search_query)
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
                            data_alpha = {"alpha": 0, "n. in session": str(i), "datetime": str(time_now),
                                          "website title": Utilis.polish_list(item, terminal=False, string_mode=True),
                                          "kind": "ADS B",
                                          "location (coordinates)": str(driver_ctrl.latandlong[0]) + "_" + str(driver_ctrl.latandlong[1]),
                                          "location (name)": "to be implemented", "query": self.my_search_query}
                            data_alpha = pd.Series(data_alpha)
                            df = df.append(data_alpha, ignore_index=True)
                            # print(df)
                            df.to_csv("{}result_{}.csv".format(self.csv_address, self.my_search_query))

                        # here method if it's been chosen "yes", to check also at 5, 10 and 20 km - method runs ONLY one time for h3 entry
                        link = driver_plain.current_url
                        if self.wanna_check_distance:
                            if h3_data_beta:
                                if len(set_one_b.intersection(set_two_b)) < len(set_two_b):
                                    not_checked_range_b_yet = True
                                else:
                                    not_checked_range_b_yet = True

                                if not_checked_range_b_yet:
                                    lat = driver_ctrl.latandlong[0]
                                    long = driver_ctrl.latandlong[1]
                                    check_range = PrepareLocation(lat, long, link, h3_data_beta, my_raw_source, df, str(time_now), is_tadsb=True).get_in_range(driver_ctrl, soup, self.csv_address, self.my_search_query)
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

if __name__ == "__main__":
    pass










