from django.contrib import admin
from .models import Patient, PersonalMedicalInformation, PseudonymizedPersonalIdentifyableInformation

admin.site.register(Patient)
admin.site.register(PersonalMedicalInformation)
admin.site.register(PseudonymizedPersonalIdentifyableInformation)
