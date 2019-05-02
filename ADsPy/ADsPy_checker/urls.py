from django.urls import path
from django.conf.urls import url
from . import views as mysearch_views
from django.views.generic import ListView, DetailView
from .models import MySearch


urlpatterns = [

    url(r'^$', mysearch_views.my_search, name="my_search"),

    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$', DetailView.as_view(model=MySearch, template_name="queries.html"), name="queries"),

    url(r'^contacts', mysearch_views.contacts, name="contacts"),
    url(r'^result-table', mysearch_views.create_table, name="results"),

]


