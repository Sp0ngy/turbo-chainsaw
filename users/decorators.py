from django.http import HttpResponseForbidden
import jwt
import requests
from functools import wraps
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET
from django_project.permissions import is_valid_permission

def requires_scopes(*required_scopes):
    # # TODO: check as middelware, that each view has a scope, when accessed.
    # if not required_scopes:
    #     raise ValueError("View is not restricted by a scope. This is not allowed.")
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not all(is_valid_permission(scope) for scope in required_scopes):
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
                decoded_rpt = jwt.decode(response_data['access_token'], options={"verify_signature": False}, algorithms='RS256')  # Requesting Party Token, part of User-Managed Access (UMA)

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
