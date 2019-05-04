from django.shortcuts import render
from django.conf.urls import url
from . import views as post_views
from django.views.generic import ListView, DetailView
from .models import MySearch
from django.shortcuts import render_to_response
from django.template import RequestContext


def my_search(request):

    # sezione cattura impulso bottone: usare il bottone per far partire la scansione sulla tabella voluta
    if (request.GET.get("bottone_prova")):
        print("impulso bottone catturato", request.GET.get("textbox"))
        for elem in MySearch.objects.all():
            if elem.my_search_query == request.GET.get("textbox"):
                print(elem.my_search_query)
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


