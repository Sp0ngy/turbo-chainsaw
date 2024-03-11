import zeep
import unicodedata
import requests

from django.conf import settings

from django_project.settings import GPAS_DOMAIN_NAME, GPAS_WSDL_URL, OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET

def generate_username(email):
    # Using Python 3 and Django 1.11, usernames can contain alphanumeric
    # (ascii and unicode), _, @, +, . and - characters. So we normalize
    # it and slice at 150 characters.
    return unicodedata.normalize('NFKC', email)[:150]

def oidc_op_logout(request):
    oidc_op_logout_endpoint = settings.OIDC_OP_LOGOUT_ENDPOINT
    # Retrieve the ID token stored in the session at login
    id_token_hint = request.session.get('oidc_id_token')
    # Construct the post logout redirect URI
    post_logout_redirect_uri = request.build_absolute_uri(getattr(settings, 'LOGOUT_REDIRECT_URL', '/'))

    # Construct the logout URL with the post_logout_redirect_uri and id_token_hint parameters
    logout_url = f"{oidc_op_logout_endpoint}?post_logout_redirect_uri={post_logout_redirect_uri}&id_token_hint={id_token_hint}"

    return logout_url


def pseudonymize(value):
    access_token = get_client_PAT_token()
    settings = zeep.Settings(extra_http_headers={'Authorization': f'Bearer {access_token}'})
    try:
        client = zeep.Client(GPAS_WSDL_URL, settings=settings)
        pseudonymized_data = client.service.getOrCreatePseudonymFor(value=value, domainName=GPAS_DOMAIN_NAME)
    except Exception as e:
        raise Exception(e)
    return pseudonymized_data

def de_pseudonymize(value):
    access_token = get_client_PAT_token()
    settings = zeep.Settings(extra_http_headers={'Authorization': f'Bearer {access_token}'})
    try:
        client = zeep.Client(GPAS_WSDL_URL, settings=settings)
        de_pseudonymized_data = client.service.getValueFor(psn=value, domainName=GPAS_DOMAIN_NAME)
    except Exception as e:
        raise Exception(e)
    return de_pseudonymized_data

def mask(value):
    """Shift characters/numbers/date values by one to mask the value of personal data."""
    return pseudonymize(value)

def unmask(value):
    """Shift characters/numbers/date values by one to recover the original value of masked data."""
    return de_pseudonymize(value)

def get_client_PAT_token():
    data = {
        'client_id': OIDC_RP_CLIENT_ID,
        'client_secret': OIDC_RP_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
        pat = response.json()['access_token']
    except Exception as e:
        raise Exception(f"Failed to obtain access token: {e}")

    return pat


