from django.shortcuts import render
from django.conf.urls import url
from . import views as post_views
from django.views.generic import ListView, DetailView
from .models import MySearch
from django.shortcuts import render_to_response
from django.template import RequestContext


def my_search(request):

    context = RequestContext(request)

    page_elements = sorted(MySearch.objects.all(), key=lambda sub_elem: sub_elem.timestamp_now, reverse=True)

    context_dict = {"object_list": page_elements}

    return render_to_response("my_search.html", context_dict, context)


def create_table(request):
    pass


def contacts(request):
    return render(request, "contacts.html")


