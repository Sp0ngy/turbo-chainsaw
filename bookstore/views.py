from django.shortcuts import render
from .models import Book


# Create your views here.

def index(request):
    books = list(Book.objects.order_by("-title"))
    # output = "\n".join([f"{b.title} {b.price}" for b in books])
    context = {"books": books}
    return render(request, "bookstore/index.html", context)
