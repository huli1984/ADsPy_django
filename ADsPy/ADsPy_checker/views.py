from django.shortcuts import render
from django.conf.urls import url
from . import views as post_views
from django.views.generic import ListView, DetailView
from .models import MySearch
from django.shortcuts import render_to_response
from django.template import RequestContext
from adspy import ADsPyManager

from redis import Redis
from rq import Queue


def print_all_elements(elem):
    elemlist = [elem.my_search_query, # 0
                elem.timestamp_now,   # 1
                elem.latandlong,      # 2
                elem.wanna_check_distance, # 3
                elem.initialize, # 4
                elem.job_timeout, # 5
                elem.csv_address, # 6
                elem.prof, # 7
                elem.prof_one, # 8
                elem.prof_two, # 9
                elem.prof_three] # 10

    return elemlist


def find_ads_background(el):
    print("started function")
    manager = ADsPyManager(el[7], el[8], el[9], el[10], el[6], el[0], el[4], el[3], el[2])
    q = Queue(connection=Redis())
    q.enqueue(manager.find_ads, el[6], job_timeout=el[5])


def my_search(request):

    # sezione cattura impulso bottone: usare il bottone per far partire la scansione sulla tabella voluta
    if (request.GET.get("bottone_prova")):
        print("impulso bottone catturato", request.GET.get("textbox"))
        for elem in MySearch.objects.all():
            if elem.my_search_query == request.GET.get("textbox"):
                print(elem.my_search_query, "my search query")
                # print(print_all_elements(elem), "element list if check in passed")
                find_ads_background(print_all_elements(elem))

    else:
        print("nothing happened")
    # fine sezione bottone

    context = RequestContext(request)

    page_elements = sorted(MySearch.objects.all(), key=lambda sub_elem: sub_elem.timestamp_now, reverse=True)

    context_dict = {"object_list": page_elements}

    return render_to_response("my_search.html", context_dict, context)


def create_table(request):
    pass


def contacts(request):
    return render(request, "contacts.html")

