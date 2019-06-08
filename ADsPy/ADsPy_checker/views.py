from django.shortcuts import render
from .models import MySearch
from adspy import ADsPyManager
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView
from redis import Redis
from rq import Queue
import time
import re
import json
from .models import MySearch
from django import template
from datetime import datetime
import json

no_run = False


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

#def find_ads_background(el):
#    print("started function")
#    manager = ADsPyManager(el[7], el[8], el[9], el[10], el[6], el[0], el[4], el[3], el[2], el[11]) # el[11] -> unique_id of post
#    q = Queue(connection=Redis())
#   q.enqueue(manager.find_ads, (el[6], el[2]), job_timeout=el[5])


def find_ads_background(el):
    print("started function")
    manager = ADsPyManager(el[7], el[8], el[9], el[10], el[6], el[0], el[4], el[3], el[2], el[11]) # el[11] -> unique_id of post
    q = Queue(connection=Redis())
    q.enqueue(manager.find_ads, (el[6], el[2]), job_timeout=el[5])


@login_required
def my_search(request):
    no_run = False
    block_writing = False
    # sezione cattura impulso bottone: usare il bottone per far partire la scansione sulla tabella voluta
    if request.POST.get("bottone_prova"):
        for elem in MySearch.objects.all():
            print(elem.my_search_query, elem.find_post_id(), request.POST.get("textbox"), request.POST.get("idbox"))
            if (elem.my_search_query == request.POST.get("textbox")) and (str(elem.find_post_id()) == request.POST.get("idbox")):
                element_list = print_all_elements(elem)
                element_list.append(request.POST.get("idbox"))

                # nel returns mettere la pagina di provenienza, se cosa veloce
                # return HttpResponseRedirect("/")

                control_id = elem.id
                control_slug = elem.slug
                control_timeout = elem.job_timeout
                start_query_time = datetime.now()
                data = {"start_value": 0}
                block_writing = False
                try:
                    with open('json_data_query') as json_file:
                        data = json.loads(json_file.read())
                        print("loading JSON in POST - mySearch", data)
                        json_file.close()
                except (FileNotFoundError, TypeError, json.decoder.JSONDecodeError) as e:
                    print(e, "file not found or type error in my search")
                    with open('json_data_query', 'w') as json_file:
                        json.dump("", json_file)
                        json_file.close()

                try:
                    if int(data[str(control_id)]["start_query_time"]) + int(elem.job_timeout) >= int(
                            datetime.now().strftime('%s')):
                        no_run = True
                        block_writing = True
                        print("NO RUN ACTIVATED In POST views.py - MySearch")
                    else:
                        # vedere se serve davvero buttare un no run dentro il json e recuperarlo: credo non serva affatto!! :D
                        no_run = False
                        block_writing = False

                except KeyError as e:
                    print("POST: into exception: file creation - MySearch", e)
                    data[str(control_id)] = {"slug": control_slug, "id": control_id, "job_timeout": control_timeout,
                                             "start_query_time": int(start_query_time.strftime('%s')), "no_run": False}
                    block_writing = True
                    with open('json_data_query', 'w') as json_file:
                        json.dump(data, json_file)
                        json_file.close()

                if not block_writing:
                    # updating JSON
                    data[str(control_id)] = {"slug": control_slug, "id": control_id, "job_timeout": control_timeout,
                                             "start_query_time": int(start_query_time.strftime('%s')), "no_run": False}
                    with open('json_data_query', 'w') as json_file:
                        json.dump(data, json_file)
                        json_file.close()

                if not no_run:
                    find_ads_background(element_list)
                else:
                    print("cannot start query -  main page")
            else:
                print("pukkeka pukkea")
    elif request.GET:
        print("into GET", request)
    # fine sezione bottone
    page_elements = sorted(MySearch.objects.all(), key=lambda sub_elem: sub_elem.timestamp_now, reverse=True)
    context_dict = {"object_list": page_elements}

    return render(request, "my_search.html", context=context_dict)


@login_required
def queries(request, id, slug):
    no_run = False
    block_writing = False
    control_id = None
    control_slug = None
    control_timeout = None
    if request.POST.get("bottone-richiesta"):
        for elem in MySearch.objects.all():
            print(elem.my_search_query, elem.find_post_id(), request.POST.get("textbox"), request.POST.get("idbox"))
            if (elem.my_search_query == request.POST.get("textbox")) and (str(elem.find_post_id()) == request.POST.get("idbox")):
                element_list = print_all_elements(elem)
                element_list.append(request.POST.get("idbox"))

                control_id = elem.id
                control_slug = elem.slug
                control_timeout = elem.job_timeout
                start_query_time = datetime.now()
                data = {}
                block_writing = False
                try:
                    with open('json_data_query') as json_file:
                        data = json.loads(json_file.read())
                        print("loading JSON in POST", data)
                        json_file.close()
                except (FileNotFoundError, TypeError) as e:
                    print(e, "file not found?")
                    with open('json_data_query', 'w') as json_file:
                        json.dump("", json_file)
                        json_file.close()

                print(data, "data check")
                try:
                    if int(data[str(control_id)]["start_query_time"]) + int(elem.job_timeout) >= int(datetime.now().strftime('%s')):
                        no_run = True
                        block_writing = True
                    else:
                        # vedere se serve davvero buttare un no run dentro il json e recuperarlo: credo non serva affatto!! :D
                        no_run = False
                        block_writing = False

                except KeyError as e:
                    print("POST: into exception: file creation", e)
                    data[str(control_id)] = {"slug": control_slug, "id": control_id, "job_timeout": control_timeout, "start_query_time": int(start_query_time.strftime('%s')), "no_run": False}
                    block_writing = True
                    with open('json_data_query', 'w') as json_file:
                        json.dump(data, json_file)
                        json_file.close()

                if not block_writing:
                    # updating JSON
                    data[str(control_id)] = {"slug": control_slug, "id": control_id, "job_timeout": control_timeout,
                                             "start_query_time": int(start_query_time.strftime('%s')), "no_run": False}
                    with open('json_data_query', 'w') as json_file:
                        json.dump(data, json_file)
                        json_file.close()

                if not no_run:
                    find_ads_background(element_list)
                else:
                    print("cannot run query")

            else:
                print("pukkeka pukkea")
    else:
        control_name = None
        control_id = None
        control_timeout = None
        control_slug = None
        request_mark = str(request).replace("<WSGIRequest: GET '/", "").replace("/'>", "")
        request_slug = request_mark.split("/")[1]
        request_id = request_mark.split("/")[0]

        try:
            with open('json_data_query') as json_file:
                data = json.loads(json_file.read())
        except FileNotFoundError:
            print("no json file with running queries")

        for elem in MySearch.objects.all():
            if (elem.slug == request_slug) and (elem.id == int(request_id)):
                control_name = elem.my_search_query
                control_slug = elem.slug
                control_id = elem.id
                control_timeout = elem.job_timeout
                start_query_time = datetime.now()

                try:
                    if int(data[str(control_id)]["start_query_time"]) + int(elem.job_timeout) >= int(datetime.now().strftime('%s')):
                        block_writing = True
                        print("NO RUN activated")
                        print(int(datetime.now().strftime('%s')))
                        data[str(control_id)]["no_run"] = True
                        with open('json_data_query', 'w') as json_file:
                            json.dump(data, json_file)
                            json_file.close()
                    else:
                        block_writing = False
                        data[str(control_id)]["no_run"] = False
                        with open('json_data_query', 'w') as json_file:
                            json.dump(data, json_file)
                            json_file.close()
                except (KeyError, TypeError, UnboundLocalError) as e:
                    print("no match!", e)
                    pass
            else:
                print(elem.id, request_id, type(elem.id), type(request_id))

        print("into GET - queries.html", request.GET, request)

    # fine sezione bottone
    page_elements = sorted(MySearch.objects.all(), key=lambda sub_elem: sub_elem.timestamp_now, reverse=True)
    if control_id and no_run:
        print(control_id, "control id")
        page_elements.append(str(control_id))
        page_elements.append(control_slug)
        page_elements.append("<p id=\"query-timeout-warning\">cannot send the same query within the query duration. Kill the query or contact an Administrator</p>")
    else:
        print("no control id")
    page_elements.append(int(id))
    print(page_elements, "page elements")
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



