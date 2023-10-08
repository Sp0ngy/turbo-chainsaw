from django.db import models

# Create your models here.

class Athor(models.Model): #NOTE: Here we introduce an intentional typo as error! Should be Author
    name = models.CharField(max_length=200)
    birthday = models.DateField()