import zeep

from django_project.settings import GPAS_DOMAIN_NAME, GPAS_WSDL_URL

from users.auth_utils import get_client_PAT_token

class gPAS_Client():
    access_token = None
    settings = None
    _client = None
    def __init__(self, access_token, settings):
        self.access_token = access_token
        self.settings = settings
        self._client = zeep.Client(GPAS_WSDL_URL, settings=settings)

    def pseudonymize(self, value):
        try:
            pseudonymized_data = self._client.service.getOrCreatePseudonymFor(value=value, domainName=GPAS_DOMAIN_NAME)
        except Exception as e:
            raise Exception(e)
        return pseudonymized_data

    def de_pseudonymize(self, value):
        try:
            de_pseudonymized_data = self._client.service.getValueFor(psn=value, domainName=GPAS_DOMAIN_NAME)
        except Exception as e:
            raise Exception(e)
        return de_pseudonymized_data


def get_gPAS_client():
    access_token = get_client_PAT_token()
    settings = zeep.Settings(extra_http_headers={'Authorization': f'Bearer {access_token}'})
    gPAS_client = gPAS_Client(access_token, settings)
    return gPAS_client

def mask(value):
    client = get_gPAS_client()
    pseudonymized_value = client.pseudonymize(value)
    return pseudonymized_value

def unmask(value):
    client = get_gPAS_client()
    de_pseudonymized_value = client.de_pseudonymize(value)
    return de_pseudonymized_value




