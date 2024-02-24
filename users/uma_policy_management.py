import requests
from django.http import HttpResponseForbidden

from django_project.settings import UMA_PROTECTION_API_POLICY, OIDC_RP_CLIENT_SECRET, OIDC_RP_CLIENT_ID, OIDC_OP_TOKEN_ENDPOINT, UMA_PROTECTION_API_RESOURCE

from users.decorators import decode_jwt_token

def grant_resource_permission(request):
    # Get User access_token
    access_token = request.session.get('oidc_access_token')
    if not access_token:
        return HttpResponseForbidden("Access token is missing.")

    keycloak_user_id = request.user.keycloak_id
    # TODO: Here it would make sense to query all resources from the app db to grant permission for them.
    #  Or separate them up. But this would need a good synchronization service as well.

    # # 1. Obtain bearer token representing consent granted by user
    # data = {
    #     'client_id': OIDC_RP_CLIENT_ID,
    #     'client_secret': OIDC_RP_CLIENT_SECRET,
    #     'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
    #     'subject_token': access_token,
    #     'requested_token_type': 'urn:ietf:params:oauth:token-type:access_token',
    #     'audience': OIDC_RP_CLIENT_ID,
    #     'requested_subject': keycloak_user_id
    # }
    #
    # response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data)
    # exchange_token = decode_jwt_token(response.json()['access_token'], audience=OIDC_RP_CLIENT_ID)

    # Try PAT instead, but then resource is not found
    # data = {
    #     'scope': 'uma_protection',
    #     'grant_type': 'password'
    # }
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    #
    # response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
    # pat = response.json()['access_token']

    # Get owner-owned resource id
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'name': keycloak_user_id
    }
    response = requests.get(UMA_PROTECTION_API_RESOURCE, params=params, headers=headers)
    response = response.json()
    print(response)
    # f08d0560-9ead-4937-b41a-70843ffa342e
    resource_id = response[0]  # Permission has same name as resource_id
    #Get resource permission
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'resource': resource_id
    }
    response1 = requests.get(UMA_PROTECTION_API_RESOURCE, params=params, headers=headers)
    response1 = response1.json()
    print(response1)
    permission_id = response1[0]

    # User needs uma-protection role as well

    # 2. Create a custom permission for a role
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
    data = {
        'name': f'Patient-Profile-Permission-{keycloak_user_id}',
        'description': 'Allow access to any admin and staff',
        'scopes': [
            'patient-profile.read',
        ],
        'roles': ['admin', 'staff']
    }
    response2 = requests.post(f'{UMA_PROTECTION_API_POLICY}/{resource_id}', json=data, headers=headers)
    response2_json = response2.json()
    print(response2_json)

    # OR update via Put an existing Permission
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    data = {
        'id': f'{permission_id}',
        'description': 'Allow access to any admin and staff',
        'scopes': [
            'patient-profile.read',
        ],
        'roles': ['admin', 'staff'],
        'owner': keycloak_user_id
    }
    response3 = requests.put(f'{UMA_PROTECTION_API_POLICY}/{permission_id}', json=data, headers=headers)
    response3 = response3.json()
    print(response3)

