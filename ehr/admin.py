from django.contrib import admin
from .models import Patient, PersonalMedicalInformation

admin.site.register(Patient)
admin.site.register(PersonalMedicalInformation)
