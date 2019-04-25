from django.urls import path
from django.conf.urls import url
from . import views as mysearch_views
from django.views.generic import ListView, DetailView
from .models import MySearch


urlpatterns = [

    # url(r'^', mysearch_views.search_list, name="my_search"),
    url(r'^$', ListView.as_view(
        queryset=MySearch.objects.all().order_by("-timestamp_now"),
        template_name="my_search.html",
        paginate_by=5), name="my_search"),

    # url(r'^search-detail', mysearch_views.single_query, name="queries"),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$', DetailView.as_view(model=MySearch, template_name="queries.html"), name="queries"),

    url(r'^contacts', mysearch_views.contacts, name="contacts"),
    url(r'^result-table', mysearch_views.create_table, name="results"),

]


