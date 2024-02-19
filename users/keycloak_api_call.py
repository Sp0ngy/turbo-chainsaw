import jwt
import requests
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET, UMA_PROTECTION_API

def create_resource():
    # Prepare the data for the introspection request
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
        'owner': '5594da45-e137-44ab-b208-94ee43b0b4cb',  # TODO: Get owner from ID_token via introspection endpoint
        'name': 'Questionnaire-1',
        'type': 'urn:turbo:resources:questionnaire',
        'resource_scopes': [
            'questionnaire.read',
            'questionnaire.write'
        ],
        'ownerManagedAccess': True
    }

    response = requests.post(UMA_PROTECTION_API, json=data, headers=headers)
    response_json = response.json()

    # Check resources
    param = {
        'name': 'Questionnaire'
    }
    response_2 = requests.get(UMA_PROTECTION_API, params=param, headers=headers)
    print(response_2.json())
    response_2_json = response_2.json()
    print('Done.')

if __name__ == '__main__':
    create_resource()