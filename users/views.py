from django.http import HttpResponse
from django.shortcuts import render

from users.consent_utils import get_user_consent, update_user_consent
from users.scopes import ConsentScopes as cs
from users.auth_utils import decode_jwt_token

def show_username(request):
    # Get the username of the authenticated user
    username = request.user.username
    first_name = request.user.first_name
    last_name = request.user.last_name

    # Return a simple HttpResponse or use a template
    return HttpResponse(f"Hello, {first_name} {last_name}! Your username is:{username}.")

def login_logout(request):
    return render(request, "users/login_logout.html", {})


def consent(request):
    context = {"tos_accepted": False, "marketing_accepted": False}
    user_access_token = request.session.get('oidc_access_token')
    claims = decode_jwt_token(user_access_token, 'account')
    user_id = claims.get("sub")

    if request.method == 'POST':
        granted_consents = []

        if 'tos_accepted' in request.POST:
            granted_consents.append(cs.TOS_ACCEPTED_V1_0.value)

        if 'marketing_accepted' in request.POST:
            granted_consents.append(cs.MARKETING_ACCEPTED_V1_0.value)

        context["tos_accepted"] = 'tos_accepted' in request.POST
        context["marketing_accepted"] = 'marketing_accepted' in request.POST

        update_user_consent(granted_consents, user_id)


    else:
        granted_consents = get_user_consent(user_id)
        if cs.TOS_ACCEPTED_V1_0 in granted_consents:
            context["tos_accepted"] = True
        if cs.MARKETING_ACCEPTED_V1_0 in granted_consents:
            context["marketing_accepted"] = True

    return render(request, "users/consent.html", context)