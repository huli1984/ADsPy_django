from django.shortcuts import render
from .models import MySearch
from adspy import ADsPyManager
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from redis import Redis
from rq import Queue
import time
import re
import json
from .models import MySearch
from django import template


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
    manager = ADsPyManager(el[7], el[8], el[9], el[10], el[6], el[0], el[4], el[3], el[2], el[11]) # el[11] -> unique_id of post
    q = Queue(connection=Redis())
    q.enqueue(manager.find_ads, (el[6], el[2]), job_timeout=el[5])


def my_search(request):
    # sezione cattura impulso bottone: usare il bottone per far partire la scansione sulla tabella voluta
    if request.POST.get("bottone_prova"):
        for elem in MySearch.objects.all():
            print(elem.my_search_query, elem.find_post_id(), request.POST.get("textbox"), request.POST.get("idbox"))
            if (elem.my_search_query == request.POST.get("textbox")) and (str(elem.find_post_id()) == request.POST.get("idbox")):
                element_list = print_all_elements(elem)
                element_list.append(request.POST.get("idbox"))
                find_ads_background(element_list)
                return HttpResponseRedirect("/")
            else:
                print("pukkeka pukkea")
    else:
        print("nothing happened", request)
    # fine sezione bottone
    page_elements = sorted(MySearch.objects.all(), key=lambda sub_elem: sub_elem.timestamp_now, reverse=True)
    context_dict = {"object_list": page_elements}

    return render(request, "my_search.html", context=context_dict)


def queries(request, id, slug):
    if request.POST.get("bottone-richiesta"):
        for elem in MySearch.objects.all():
            print(elem.my_search_query, elem.find_post_id(), request.POST.get("textbox"), request.POST.get("idbox"))
            if (elem.my_search_query == request.POST.get("textbox")) and (str(elem.find_post_id()) == request.POST.get("idbox")):
                element_list = print_all_elements(elem)
                element_list.append(request.POST.get("idbox"))
                find_ads_background(element_list)
                return HttpResponseRedirect("/")
            else:
                print("pukkeka pukkea")
    else:
        print("nothing happens")

    # fine sezione bottone
    page_elements = sorted(MySearch.objects.all(), key=lambda sub_elem: sub_elem.timestamp_now, reverse=True)
    page_elements.append(int(id))
    context_dict = {"object_list": page_elements}

    return render(request, "queries.html", context=context_dict)


def select(request, id, slug):
    page_elements = sorted(MySearch.objects.all(), key=lambda sub_elem: sub_elem.timestamp_now, reverse=True)
    page_elements.append(int(id))
    context_dict = {"object_list": page_elements}

    return render(request, "select.html", context=context_dict)


def update_table(request):
    print("function triggered")
    template_name = "queries.html"
    form_class = UserCreationForm
    removePresence = request.POST.get("removePresence", None)


def create_table(request):
    pass


def contacts(request):
    return render(request, "contacts.html")



