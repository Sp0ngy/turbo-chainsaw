import requests
from django_project.settings import OIDC_RP_CLIENT_ID, OIDC_EXTENSION_CONSENT_ENDPOINT, OIDC_CONSENT_ENDPOINT

from users.auth_utils import get_client_PAT_token
from users.scopes import ConsentScopes as cs

def get_user_consent(user_id):
    PAT_token = get_client_PAT_token()
    response = get_consent_records(PAT_token, user_id)
    grantedClientScopes = filter_granted_client_scopes(response, OIDC_RP_CLIENT_ID)

    return grantedClientScopes

def update_user_consent(granted_consents, user_id):
    PAT_token = get_client_PAT_token()
    update_consent_records(PAT_token, user_id, granted_consents)
    # Issue new access token

def get_consent_records(access_token, user_id):
    """
    :param access_token:
    :param required_scopes:
    :param resource: takes the keycloak resource id or the resource name
    :return:
    """
    url = f"{OIDC_CONSENT_ENDPOINT}/{user_id}/consents"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def update_consent_records(access_token, user_id, granted_consents):
    url = f"{OIDC_EXTENSION_CONSENT_ENDPOINT}/{user_id}/consents"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'clientId': OIDC_RP_CLIENT_ID,
        'grantedClientScopes': granted_consents,
    }
    response = requests.put(url, json=payload, headers=headers)
    return response

def filter_granted_client_scopes(data, target_client_id):
    """
    Filters and compiles the grantedClientScopes for a specific clientId.

    :param data: List of dictionaries, each containing client data.
    :param target_client_id: The clientId to filter by.
    :return: List of grantedClientScopes for the specified clientId.
    """
    # Filter the list for the specified clientId and compile the grantedClientScopes
    scopes = [
        item['grantedClientScopes']
        for item in data
        if item['clientId'] == target_client_id
    ]

    # Flatten the list of lists into a single list
    granted_scopes_str = [scope for sublist in scopes for scope in sublist]

    return map_strings_to_consent_scopes(granted_scopes_str)

def map_strings_to_consent_scopes(scope_strings):
    """
    Maps a list of scope strings to their corresponding ConsentScopes enum values.

    :param scope_strings: List of strings representing the scope identifiers.
    :return: List of ConsentScopes enum values corresponding to the input strings.
    """
    # Use the .value attribute to compare strings to enum values
    valid_scopes = [scope for scope in scope_strings if scope in [e.value for e in cs]]
    # Map valid string values to their corresponding enum instances
    return [cs(scope) for scope in valid_scopes]
