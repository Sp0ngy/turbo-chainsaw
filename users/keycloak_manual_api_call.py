import jwt
import datetime
import requests
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET, UMA_PROTECTION_API_RESOURCE, UMA_PROTECTION_API_POLICY, OIDC_HOST, OIDC_REALM, OIDC_EXTENSION_CONSENT_ENDPOINT

def create_resource():
    data = {
        'client_id': OIDC_RP_CLIENT_ID,
        'client_secret': OIDC_RP_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
    pat = response.json()['access_token']

    # Create a new resource
    headers = {'Authorization': f'Bearer {pat}', 'Content-Type': 'application/json'}
    data = {
        'owner': 'db9b8c9f-abf4-446b-8060-95475fc8bf45',  # TODO: Get owner from ID_token via introspection endpoint
        'name': 'Questionnaire-1',
        'type': 'urn:turbo:resources:questionnaire',
        'resource_scopes': [
            'questionnaire.read',
            'questionnaire.write'
        ],
        'ownerManagedAccess': True
    }

    response = requests.post(UMA_PROTECTION_API_RESOURCE, json=data, headers=headers)
    response_json = response.json()
    resource_id = response_json['_id']




    # Check resources
    param = {
        'type': 'urn:turbo:resources:patient-profile'
    }
    resource_id = 'f08d0560-9ead-4937-b41a-70843ffa342e'
    response_2 = requests.get(f'{UMA_PROTECTION_API_RESOURCE}', params=param, headers=headers)
    print(response_2.json())
    response_2_json = response_2.json()
    print('Done.')

def get_RPT():
    # Prepare the data for the introspection request
    data = {
        'client_id': OIDC_RP_CLIENT_ID,
        'client_secret': OIDC_RP_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
    pat = response.json()['access_token']
    return pat

def get_admin_cli_token():
    # Prepare the data for the introspection request
    data = {
        'client_id': 'admin-cli',
        'client_secret': 'tcoL7KPdrXxfAKXde8uLZyAmwsUOcfj5',
        'grant_type': 'client_credentials'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
    pat = response.json()['access_token']
    return pat

def update_user_consent(user_id):
    token = get_RPT()

    url = f"{OIDC_HOST}/admin/realms/{OIDC_REALM}/users/{user_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'firstName': 'Sabine1234',
        'clientConsents': [{
            'clientId': OIDC_RP_CLIENT_ID,
            'grantedClientScopes': ['tos-accepted'],
        }
        ]
    }
    response = requests.put(url, json=payload, headers=headers)
    print(response.status_code, response.text)

def get_user_details(user_id):
    token = get_RPT()

    url = f"{OIDC_HOST}/admin/realms/{OIDC_REALM}/users/{user_id}/consents"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    print(response.status_code, response.text)

def update_consent_record():
    token = get_RPT()
    user_id = '86ddd477-a536-471b-94ff-b7a4ff7cf529'

    url = f"{OIDC_EXTENSION_CONSENT_ENDPOINT}/{user_id}/consents"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'clientId': OIDC_RP_CLIENT_ID,
        'grantedClientScopes': ['tos-accepted-v1.0'], #  'marketing-accepted-v1.0'
    }
    response = requests.put(url, json=payload, headers=headers)
    print(response.status_code, response.text)


# def test_PUT():
#     token = get_RPT()
#
#     url = f"{OIDC_HOST}/realms/{OIDC_REALM}/custom-consent/test-put"
#     headers = {
#         'Authorization': f'Bearer {token}',
#         'Content-Type': 'application/json'
#     }
#     payload = {
#         'clientId': OIDC_RP_CLIENT_ID,
#         'grantedClientScopes': ['tos-accepted-v1.0']  #  'marketing-accepted-v1.0'
#     }
#     response = requests.put(url, json=payload, headers=headers)
#     print(response.status_code, response.text)

def get_consents():
    token = get_RPT()
    user_id = '281bf263-ea21-447d-b5e5-70fbc3f8061a'

    url = f"{OIDC_HOST}/admin/realms/{OIDC_REALM}/users/{user_id}/consents"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    print(response.status_code, response.text)

if __name__ == '__main__':
    # test_PUT()
    update_consent_record()
    # get_consents()
    # update_user_consent('267299fd-a061-4e2e-a175-f83a2d1515bb')
    # get_user_details('267299fd-a061-4e2e-a175-f83a2d1515bb')