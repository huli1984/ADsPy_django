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
        divider = self.duration/60
        print(duration, divider)
        while duration >= 0:
            sys.stdout.write('\r\r' + "[" + "#"*(int(self.duration/divider) - int(duration/divider)) + " "*int(duration/divider) + "]")
            duration -= 1
            time.sleep(1)


class PrepareLocation:

    def __init__(self, latitude, longitude, url_link, h3_data, page_sourced_saved, df, datetime, is_tads=False, is_tadsb=False):
        self.latitude = latitude
        self.longitude = longitude
        self.url_link = url_link

        h3_list = []
        for item in h3_data:
            item = re.sub(re.compile("<h3 class=\"[A-Za-z0-9]+\"[>]*"), "", str(item).replace("</h3>", ""))
            h3_list.append(item)

        #self.h3 = h3_data
        self.h3 = h3_list
        self.page_source = page_sourced_saved
        self.is_tads = is_tads
        self.is_tadsb = is_tadsb
        self.sub_df = df
        self.datetime = datetime

        #process self.h3
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


    def get_in_range(self, driver_ctrl, soup):
        # get next measure for 2, 5 and 20 km
        df = self.sub_df
        latitude = self.latitude
        latitude_1 = float(latitude) + 0.046  # latitude + 5 km
        latitude_2 = float(latitude_1) + 0.046  # latitude + 10 km
        latitude_3 = float(latitude_2) + 0.046*2  # latitude + 20 km
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
                    new_h3_b = polish_list(new_h3_b, terminal=False)
                    self.print_to_pandas_looper(new_h3_b, datetime, km, True)
                else:
                    self.print_to_pandas_looper(None, datetime, km, False)

            else:
                print("this else is an error - line ~197")

            # here append to Pandas sub_df, instead of returning answers.
            df.to_csv("result.csv")

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
    def no_ads_found(dataframe, my_time, the_query, pause_time):
        no_ads_data = {"n. in session": numpy.nan, "datetime": str(my_time), "website title": "Not Available",
                       "kind": "NO ADS BOXES", "location (coordinates)": str(latandlong[0]) + "_" + str(latandlong[1]),
                       "location (name)": "to be implemented", "query": the_query}
        no_ads_data = pd.Series(no_ads_data)
        dataframe = dataframe.append(no_ads_data, ignore_index=True)
        dataframe.to_csv("result.csv")
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

    def __init__(self, prof, prof_one, prof_two, prof_three, csv_add):

        global profile_zero
        global profile_one
        global profile_two
        global profile_three
        global csv_address

        headless = True

        profile_zero = prof
        profile_one = prof_one
        profile_two = prof_two
        profile_three = prof_three
        csv_address = csv_add

        self.profile_zero = prof
        self.profile_one = prof_one
        self.profile_two = prof_two
        self.profile_three = prof_three
        self.csv_address = csv_add

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

        global latandlong
        splittable = False
        loc_address = os.path.join(csv_address, "location.csv")

        # read locations stored in the editable "location.csv" - it's easy to add a tag in the column "places" and a set of coordinates in the col "latandlong"
        df_latandlong = pd.read_csv(loc_address)
        # set places as index
        df_latandlong = df_latandlong.set_index("places", drop=False)
        print("\n", df_latandlong, "\n\nchoose a place stored in memory or insert a new coordinate\n")

        latandlong = input("please insert latitude and longitude -> (x.xxxx, y.yyyy use comma and space as separator and dot as decimal indicator)\ninsert 'default' to use current real location\n -> ")

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
            profile_1.set_preference("geo.wifi.uri", 'data:application/json,{"location": {"lat": ' + str(float(lat) + 0.046) + ', "lng": ' + long + '}, "accuracy": 100.0}')
            profile_2.set_preference("geo.wifi.uri", 'data:application/json,{"location": {"lat": ' + str(float(lat) + 0.046 * 2) + ', "lng": ' + long + '}, "accuracy": 100.0}')
            profile_3.set_preference("geo.wifi.uri", 'data:application/json,{"location": {"lat": ' + str(float(lat) + 0.046 * 4) + ', "lng": ' + long + '}, "accuracy": 100.0}')

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
            driver.get("https://consent.google.com/ui/?continue=https://www.google.com/&origin=https://www.google.com&if=1&gl=IT&hl=it&pc=s")
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


'''end Functions Space'''


if __name__ == "__main__":
    pass
    









