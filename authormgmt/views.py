from django.shortcuts import render
from .models import Author

# Create your views here.

def index(request):
    authors = list(Author.objects.order_by("name"))
    context = {"authors": authors}
    return render(request, "authormgmt/index.html", context)
