from django.shortcuts import render
from .models import Patient


# Create your views here.

def index(request):
    patients = list(Patient.objects.all())
    context = {"patients": patients}
    return render(request, "ehr/index.html", context)
