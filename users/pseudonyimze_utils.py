import zeep

from django_project.settings import GPAS_DOMAIN_NAME, GPAS_WSDL_URL

from users.auth_utils import get_client_PAT_token

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




