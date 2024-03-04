import jwt
import requests
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET, UMA_PROTECTION_API_RESOURCE, UMA_PROTECTION_API_POLICY

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

if __name__ == '__main__':
    create_resource()