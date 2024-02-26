from django.http import HttpResponse
from django.shortcuts import render


def show_username(request):
    # Get the username of the authenticated user
    username = request.user.username
    first_name = request.user.first_name
    last_name = request.user.last_name

    # Return a simple HttpResponse or use a template
    return HttpResponse(f"Hello, {first_name} {last_name}! Your username is:{username}.")

def login_logout(request):
    return render(request, "users/login_logout.html", {})
