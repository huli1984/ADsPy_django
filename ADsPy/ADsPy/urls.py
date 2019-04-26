"""locallibrary URL Configuration


L'elenco "urlpatterns" indirizza gli URL alle viste. Per maggiori informazioni vedi    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Esempi:
Funzioni di views
    1. Aggiungi un import:  da my_app import views
    2. aggiungi un URL a urlpatterns:  path('', views.home, name='home')
 views basate su classi
    1. Aggiungi un import:  da other_app.views import Home
    2. Aggiungo un URL a urlpatterns:  path('', Home.as_view(), name='home')
Possibilità di includere un altro URLconf
    1. Importare la funzione include (): da django.urls import include, path
    2. Aggiungi URL a urlpatterns: path ('blog /', include ('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
# Add URL maps to redirect the base URL to our application
from django.views.generic import RedirectView
from django.urls import include
# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    # path('ADsPy_checker/', admin.site.urls),
    path('', include('ADsPy_checker.urls'))
]


urlpatterns += [
    # path('', RedirectView.as_view(url='/ADsPy_checker/', permanent=True)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)