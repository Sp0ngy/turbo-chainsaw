from django.http import HttpResponseForbidden
import jwt
import requests
from functools import wraps
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET, UMA_PROTECTION_API_PERMISSION, UMA_PROTECTION_API_RESOURCE
from django_project.permissions import is_valid_scope

from users.models import User
from ehr.models import Patient


def requires_scopes(*required_scopes):
    # # TODO: check as middelware, that each view has a scope, when accessed.
    # if not required_scopes:
    #     raise ValueError("View is not restricted by a scope. This is not allowed.")

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not all(is_valid_scope(scope) for scope in required_scopes):
                raise ValueError("Invalid scope.")

            access_token = request.session.get('oidc_access_token')
            if not access_token:
                return HttpResponseForbidden("Access token is missing.")

            # Prepare the data for the introspection request
            data = {
                'audience': OIDC_RP_CLIENT_ID,
                'client_id': OIDC_RP_CLIENT_ID,
                'client_secret': OIDC_RP_CLIENT_SECRET,
                'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket'
            }
            headers = {'Authorization': f'Bearer {access_token}'}

            try:
                # Send a request to the token introspection endpoint
                response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
                response_data = response.json()
                # TODO: check jwt for details
                # Load the public key from file
                with open('keycloak_public_key.pem', 'r') as pem_file:
                    public_key = pem_file.read()

                decoded_rpt = jwt.decode(response_data['access_token'], key=public_key, algorithms='RS256', audience=OIDC_RP_CLIENT_ID)  # Requesting Party Token, part of User-Managed Access (UMA)

                permission_list = decoded_rpt['authorization']['permissions']

                # Step 1: Collect all allowed scopes into a set for efficient search
                user_scopes = {scope for permission in permission_list if 'scopes' in permission for scope in
                                  permission['scopes']}

                # Step 2: Filter out required scopes that are not in the allowed scopes
                missing_scopes = [scope for scope in required_scopes if scope.value not in user_scopes]

                # Check if missing_scopes is empty
                if not missing_scopes:
                    # Proceed to show the view
                    return view_func(request, *args, **kwargs)
                else:
                    # If missing_scopes is not empty, raise HttpResponseForbidden
                    return HttpResponseForbidden("You do not have permission to access this view.")

            except jwt.DecodeError as e:
                return HttpResponseForbidden(f"JWT exception{e}")

        return _wrapped_view

    return decorator

def uma_protected_resource(*required_scopes):
    """
    Checks, if access to a UMA resource is granted.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            pk = kwargs.get('pk')
            patient = Patient.objects.get(pk=pk)
            user = User.objects.get(patient=patient)
            resource_identifier = user.keycloak_id

            access_token = request.session.get('oidc_access_token')

            # 1. Get resource ID
            # Get owner-owned resource id
            headers = {'Authorization': f'Bearer {access_token}'}
            params = {
                'name': user.keycloak_id
            }
            response = requests.get(UMA_PROTECTION_API_RESOURCE, params=params, headers=headers)
            response = response.json()
            resource_id = response[0]
            print(response)

            # 2. Get token with permission if user has permission
            headers = {'Authorization': f'Bearer {access_token}'}
            data = {'permission': f'{resource_id}#patient-profile.read',
                    'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
                    'audience': f'{OIDC_RP_CLIENT_ID}',}

            response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)

            response_data = response.json()
            try:
                if response.status_code == 400:
                    # Interpret as lack of permission, see commend above. This is very unintuitive.
                    return HttpResponseForbidden("You do not have permission to access this resource.")
                elif response.status_code != 200:
                    # Handle other HTTP errors
                    return HttpResponseForbidden("An error occurred while checking permissions.")

                decoded_token = decode_jwt_token(response_data.get('access_token'), audience=OIDC_RP_CLIENT_ID)
                access_granted = check_user_permissions(decoded_token, required_scopes)
                if access_granted:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("You do not have permission to access this view.")
            except KeyError:
                # Handle cases where 'access_token' is not in response
                return HttpResponseForbidden("Invalid response received from the authorization server.")


        return _wrapped_view
    return decorator


def decode_jwt_token(token, audience):
    """
    Decodes and validates a JWT token.

    Args:
    - token: The JWT token as a string.
    - audience: Expected audience value (OIDC_RP_CLIENT_ID).

    Returns:
    - The decoded JWT if valid, None otherwise.
    """
    try:
        with open('keycloak_public_key.pem', 'r') as pem_file:
            public_key = pem_file.read()

        decoded_token = jwt.decode(token, key=public_key, algorithms='RS256', audience=audience,
                                   options={"verify_aud": True, "verify_iss": True})
        return decoded_token
    except Exception as e:
        print(f"Token validation error: {e}")
        return None


def check_user_permissions(decoded_token, required_scopes):
    """
    Checks if the decoded token contains the required scopes.

    Args:
    - decoded_token: The decoded JWT token.
    - required_scopes: A list of scopes required for access.

    Returns:
    - True if access is granted, False otherwise.
    """
    if decoded_token is None:
        return False

    permission_list = decoded_token.get('authorization', {}).get('permissions', [])
    user_scopes = {scope for permission in permission_list if 'scopes' in permission for scope in permission['scopes']}
    missing_scopes = [scope for scope in required_scopes if scope.value not in user_scopes]

    return len(missing_scopes) == 0


# https://www.keycloak.org/docs/latest/authorization_services/index.html#_service_protection_permission_api_papi
def obtain_uma_protected_resource_permission(*required_scopes):
    """
    View to make a request for a certain UMA protected resource via a permission ticket
    """
    # TODO: Work in progress
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            pk = kwargs.get('pk')
            patient = Patient.objects.get(pk=pk)
            user = User.objects.get(patient=patient)
            resource_id = user.keycloak_id

            access_token = request.session.get('oidc_access_token')
            if not access_token:
                return HttpResponseForbidden("Access token is missing")

            # Send a request for a protected resource without RPT
            response = requests.get(f'{UMA_PROTECTION_API_PERMISSION}/Patient-Profile{resource_id}')
            response.json()

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator





