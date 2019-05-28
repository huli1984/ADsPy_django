from django.urls import path
from django.conf.urls import url
from . import views as mysearch_views
from django.contrib import admin
from django.views.generic import ListView, DetailView
from .models import MySearch

# Admin Site Config
admin.sites.AdminSite.site_header = 'My site admin header'
admin.sites.AdminSite.site_title = 'My site admin title'
admin.sites.AdminSite.index_title = 'My site admin index'

urlpatterns = [
    url(r'^$', mysearch_views.my_search, name="my_search"),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$', mysearch_views.queries, name="queries"),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/select.html', mysearch_views.select, name="no_presence"),
    url(r'^contacts', mysearch_views.contacts, name="contacts"),
    url(r'^result-table', mysearch_views.create_table, name="results"),
]


