from django.shortcuts import render
from .models import Athor

# Create your views here.

def index(request):
    authors = list(Athor.objects.order_by("name"))
    context = {"authors": authors}
    return render(request, "authormgmt/index.html", context)
