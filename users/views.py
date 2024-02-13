from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def show_username(request):
    # Get the username of the authenticated user
    username = request.user.username
    # Return a simple HttpResponse or use a template
    return HttpResponse(f"Hello, {username}!")


