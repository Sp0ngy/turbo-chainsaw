from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from django_project.settings import OIDC_RP_CLIENT_ID

from users.auth_utils import decode_jwt_token
from users.scopes import ConsentScopes as cs

class ConsentCheckMiddleware(MiddlewareMixin):
    """
    Middleware which checks the consent claim within the access token.
    """

    def process_request(self, request):
        # Define all Exempt-URLs
        if request.path.startswith('/auth'):
            return None

        if request.path.startswith('/authenticate'):
            return None

        if request.path.startswith('/callback'):
            return None

        if request.path.startswith('/logout'):
            return None

        if request.path.startswith('/consent'):
            return None

        # Check if the user has consented, this is just a placeholder
        # Implement your logic here to check if the user has given the required consent
        user_has_consented = self.check_TOS_consent(request)

        if not user_has_consented:
            #TODO: Redirect to consent page and raise Alert
            return HttpResponseForbidden("You must accept the terms of service to proceed.")

        return None

    def check_TOS_consent(self, request):
        """
        Check for Terms of Service consent.
        """
        user_access_token = request.session.get('oidc_access_token')
        claims = decode_jwt_token(user_access_token, 'account')
        consents = claims.get("consent")

        if OIDC_RP_CLIENT_ID in consents and cs.TOS_ACCEPTED_V1_0.value in consents[OIDC_RP_CLIENT_ID]:
            return True
        else:
            return False



