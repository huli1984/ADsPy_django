from django.contrib import admin

# Register your models here.
from .models import MySearch


class MySearchAdmin(admin.ModelAdmin):
    list_display = ["__str__", "timestamp_now", "geolocation"]
    list_filter = ["my_query", "geolocation"]
    search_fields = ["my_query", "result_field", "geolocation"]
    prepopulated_fields = {"slug": ("my_query",)}

    class Meta:
        model = MySearch


admin.site.register(MySearch, MySearchAdmin)
