import unicodedata

from django.conf import settings

from zeep import Client

from django_project.settings import GPAS_DOMAIN_NAME, GPAS_WSDL_URL

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
    try:
        client = Client(GPAS_WSDL_URL)
        pseudonymized_data = client.service.getOrCreatePseudonymFor(value=value, domainName=GPAS_DOMAIN_NAME)
    except Exception as e:
        raise Exception(e)
    return pseudonymized_data

def de_pseudonymize(value):
    try:
        client = Client(GPAS_WSDL_URL)
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
