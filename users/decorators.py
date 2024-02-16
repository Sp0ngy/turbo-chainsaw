from django.http import HttpResponseForbidden
import jwt
import requests
from functools import wraps
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET


def requires_scopes(*required_scopes):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
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

                allowed_scopes = decoded_rpt['authorization']['permissions'][0]['scopes']

                for required_scope in required_scopes:
                    if required_scope not in allowed_scopes:
                        #TODO: remove scopes from print
                        return HttpResponseForbidden(f"{required_scope} is not in {allowed_scopes}")

                # If checks pass, call the original view
                return view_func(request, *args, **kwargs)
            except jwt.DecodeError as e:
                return HttpResponseForbidden(f"JWT exception{e}")

        return _wrapped_view

    return decorator
