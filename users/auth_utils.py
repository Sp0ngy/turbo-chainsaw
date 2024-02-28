from django.http import HttpResponseForbidden
import jwt
import requests
from functools import wraps
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID
from django_project.permissions import GlobalsScopes

from users.models import Resource

def requires_scope(*required_scopes):
    """
    Checks if a user has permission to access a generic type of resource.
    Based on the required scopes it is associated with a generic resource in keycloak.

    :param required_scopes:
    :return:
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            scope_to_resource = {
                GlobalsScopes.STAFF_PORTAL_READ: 'Staff-Portal',
                GlobalsScopes.STAFF_PORTAL_WRITE: 'Staff-Portal',
            }
            access_token = request.session.get('oidc_access_token')

            # Identify resource based on required scopes
            resource = set([scope_to_resource[scope] for scope in required_scopes if scope in scope_to_resource])

            if len(resource) > 1:
                # Implementation only for scopes, which are mapped to the same resource. Can be extended:
                # https://www.keycloak.org/docs/latest/authorization_services/#_service_obtaining_permissions
                # Currently, we handle scopes mapping to the same resource. Redirect or handle error.
                return HttpResponseForbidden("Error: Required scopes map to multiple resources.")

            headers = {'Authorization': f'Bearer {access_token}'}
            data = {'permission': f'{resource.pop()}#{",".join(scope.value for scope in required_scopes)}',
                    # 'resource_id#patient-profile.read,patient-profile.write'
                    'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
                    'audience': f'{OIDC_RP_CLIENT_ID}', }
            response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
            if not response.status_code == 403:  # Unauthorized
                token_w_scopes = response.json()['access_token']
                if not has_required_permissions(token_w_scopes, required_scopes=required_scopes):
                    return HttpResponseForbidden("You do not have the required permission to access this resource.")
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You are not authorized to view this resource.")
        return _wrapped_view
    return decorator

def protected_user_resource(*required_scopes):
    """
    Use this decorator if a specific user resource is accessed. User resources are identified by patient identifier.

    keycloak_resource_id required as parameter.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            keycloak_resource_id = kwargs.get('keycloak_resource_id')
            access_token = request.session.get('oidc_access_token')

            # Get token with permissions
            headers = {'Authorization': f'Bearer {access_token}'}
            data = {'permission': f'{keycloak_resource_id}#{",".join(scope.value for scope in required_scopes)}',
                    # 'resource_id#patient-profile.read,patient-profile.write'
                    'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
                    'audience': f'{OIDC_RP_CLIENT_ID}', }

            response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
            if not response.status_code == 403:  # Unauthorized
                token_w_scopes = response.json()['access_token']
                if keycloak_resource_id:
                    if not has_required_permissions(token_w_scopes, required_scopes=required_scopes):
                        return HttpResponseForbidden("You do not have the required permission to access this resource.")
                    return view_func(request, *args, **kwargs)
                else:
                    # If keycloak_resource_id is not provided, deny access
                    return HttpResponseForbidden("No Resource ID provided.")
            else:
                return HttpResponseForbidden("You are not authorized to view this resource.")
        return _wrapped_view
    return decorator

def has_required_scope(request, required_scopes):
    access_token = request.session.get('oidc_access_token')
    resource = identify_requested_resource(required_scopes)

    response = call_token_endpoint_with_resource_scope(access_token, required_scopes, resource)
    if response.status_code == 403:  # Unauthorized
        return False, "Unauthorized"

    token_w_scopes = response.json()['access_token']
    if not has_required_permissions(token_w_scopes, required_scopes=required_scopes):
        return False, "You do not have the required permission to access this resource."

    return True, "Authorized"

def has_protected_user_resource_scope(request, required_scopes, keycloak_resource_id):
    """

    :param request:
    :param required_scopes:
    :param keycloak_resource_id:
    :return:
    """
    access_token = request.session.get('oidc_access_token')

    response = call_token_endpoint_with_resource_scope(access_token, required_scopes, keycloak_resource_id)

    if response.status_code == 403:  # Unauthorized
        return False, "Unauthorized"

    token_w_scopes = response.json()['access_token']
    if not has_required_permissions(token_w_scopes, required_scopes=required_scopes):
        return False, "You do not have the required permission to access this resource."

    return True, "Authorized"

def has_required_permissions(permission_token, required_scopes):
    """
    Checks if the decoded token contains the required scopes.

    Args:
    - decoded_token: The decoded JWT token.
    - required_scopes: A list of scopes required for access.

    Returns:
    - True if access is granted, False otherwise.
    """
    decoded_token = decode_jwt_token(permission_token, OIDC_RP_CLIENT_ID)
    if decoded_token is None:
        return False

    permission_list = decoded_token.get('authorization', {}).get('permissions', [])
    user_scopes = {scope for permission in permission_list if 'scopes' in permission for scope in permission['scopes']}
    missing_scopes = [scope for scope in required_scopes if scope.value not in user_scopes]

    if len(missing_scopes) == 0:
        return True
    else:
        return False

def identify_requested_resource(required_scopes):
    scope_to_resource = {
        GlobalsScopes.STAFF_PORTAL_READ: 'Staff-Portal',
        GlobalsScopes.STAFF_PORTAL_WRITE: 'Staff-Portal',
    }
    resources = set([scope_to_resource[scope] for scope in required_scopes if scope in scope_to_resource])
    if len(resources) > 1:
        # Implementation only for scopes, which are mapped to the same resource. Can be extended:
        # https://www.keycloak.org/docs/latest/authorization_services/#_service_obtaining_permissions
        # Currently, we handle scopes mapping to the same resource. Redirect or handle error.
        raise KeyError("Error: Required scopes map to multiple resources.")
    resource = resources.pop()
    return resource

def call_token_endpoint_with_resource_scope(access_token, required_scopes, resource):
    """

    :param access_token:
    :param required_scopes:
    :param resource: takes the keycloak resource id or the resource name
    :return:
    """
    headers = {'Authorization': f'Bearer {access_token}'}
    permissions_str = ",".join(scope.value for scope in required_scopes)  # patient-profile.read,patient-profile.write'
    data = {'permission': f'{resource}#{permissions_str}',
            'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'audience': f'{OIDC_RP_CLIENT_ID}', }

    response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
    return response

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




