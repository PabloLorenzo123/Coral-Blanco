from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse_lazy

# Create your models here.
class Report(models.Model):
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return "Hi!"
    


