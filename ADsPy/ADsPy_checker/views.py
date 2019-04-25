from django.shortcuts import render
'''from django.template import loader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


options = Options()
options.headless = True


# Create your views here.


def search_list(request):
    driver = webdriver.Firefox(options=options)
    driver.get("http://www.socremapeiron.it")
    superstring = driver.page_source
    template = loader.get_template("my_search.html")
    return render(request, "my_search.html", {"superstring": superstring})
    return render(request, "my_search.html")'''


'''def single_query(request):
    return render(request, "queries.html")'''


def create_table(request):
    return render(request, "contacts.html")
    pass


def contacts(request):
    pass




