from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    author = models.ForeignKey("authormgmt.Athor", on_delete=models.SET_NULL, null=True)
