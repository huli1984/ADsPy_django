from django.db import models
from django.urls import reverse


# Create your models here.
class MySearch(models.Model):
    """A typical class defining a model, derived from the Model class."""

    # Fields
    my_query = models.CharField(max_length=250)
    geolocation = models.CharField(max_length=250)
    timestamp_now = models.DateField(auto_now=False, auto_now_add=True)
    result_field = models.TextField()
    slug = models.SlugField()

    # Metadata
    class Meta:
        ordering = ['-my_query']

    # Methods
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return str(self.my_query).upper()

    def get_url(self):
        return reverse("queries", kwargs={"id": self.id, "slug": self.slug})
