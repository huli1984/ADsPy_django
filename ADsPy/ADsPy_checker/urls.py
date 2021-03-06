from django.urls import path, include
from django.conf.urls import url
from . import views as mysearch_views
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView
from itertools import chain
from .models import MySearch

# Admin Site Config
admin.sites.AdminSite.site_header = 'My site admin header'
admin.sites.AdminSite.site_title = 'My site admin title'
admin.sites.AdminSite.index_title = 'My site admin index'

urlpatterns = [
    #url(r'^$', ListView.as_view(queryset=sorted(chain(MySearch.objects.all()), key=lambda instance: instance.timestamp_now, reverse=True),
    #                            template_name="my_search.html",
    #                            paginate_by=25), name="my_search"),
    url(r'^$', mysearch_views.my_search, name="my_search"),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$', mysearch_views.queries, name="queries"),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/select.html', mysearch_views.select, name="no_presence"),
    url(r'^contacts', mysearch_views.contacts, name="contacts"),
    url(r'^result-table', mysearch_views.create_table, name="results"),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^django-sb-admin/', include('django_sb_admin.urls')),
]


