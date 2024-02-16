from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from users.decorators import requires_scopes

# @login_required
@requires_scopes('')
def show_username(request):
    # Get the username of the authenticated user
    username = request.user.username
    # Return a simple HttpResponse or use a template
    return HttpResponse(f"Hello, {username}!")

def login_logout(request):
    return render(request, "users/login_logout.html", {})
