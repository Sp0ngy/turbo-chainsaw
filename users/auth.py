import requests
from django.contrib.auth.models import Group
from django.db import transaction
from mozilla_django_oidc import auth
from ehr.models import Patient
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET, UMA_PROTECTION_API_RESOURCE


class OIDCAuthenticationBackend(auth.OIDCAuthenticationBackend):

    def filter_users_by_claims(self, claims):
        """Return all users matching the specified Keycloak ID."""
        keycloak_id = claims.get("sub")  # Assuming 'sub' claim is used as Keycloak ID
        if not keycloak_id:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(keycloak_id=keycloak_id)

    def create_user(self, claims):
        """Return object for a newly created user account."""
        keycloak_id = claims.get("sub")
        user = self.UserModel.objects.create_user(keycloak_id)
        # Set any additional fields from claims here
        Patient.objects.get_or_create(user=user)
        # Create a new resource
        create_uma_resource(user)
        user.save()
        self._assign_roles_to_user(user, claims)
        self.update_groups(user, claims)
        return user

    def update_user(self, user, claims):
        user.keycloak_id = claims.get('sub')
        user.save()
        self._assign_roles_to_user(user, claims)
        self.update_groups(user, claims)

        return user


    # TODO: add delete_user method

    def update_groups(self, user, claims):
        """
        Transform roles obtained from keycloak into Django Groups and
        add them to the user. Note that any role not passed via keycloak
        will be removed from the user.
        """
        with transaction.atomic():
            user.groups.clear()
            for role in claims.get('roles'):
                group, _ = Group.objects.get_or_create(name=role)
                group.user_set.add(user)

    def get_userinfo(self, access_token, id_token, payload):
        """
        Get user details from the access_token and id_token and return
        them in a dict.
        """
        userinfo = super().get_userinfo(access_token, id_token, payload)
        accessinfo = self.verify_token(access_token, nonce=payload.get('nonce'))
        roles = accessinfo.get('realm_access', {}).get('roles', [])

        userinfo['roles'] = roles
        return userinfo

    def _assign_roles_to_user(self, user, claims):
        roles = claims.get('roles', [])
        if 'admin' in roles or 'superuser' in roles:
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        user.save()


def create_uma_resource(user):
    # Get Access token
    data = {
        'client_id': OIDC_RP_CLIENT_ID,
        'client_secret': OIDC_RP_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers)
        pat = response.json()['access_token']
    except Exception as e:
        raise Exception(f"Failed to obtain access token: {e}")

    # Create a new resource
    headers = {'Authorization': f'Bearer {pat}', 'Content-Type': 'application/json'}
    data = {
        'owner': f'{user.keycloak_id}',
        'name': f'Patient-Profile-{user.keycloak_id}',  # TODO: write method to get PatientProfile identifier
        'type': 'urn:turbo:resources:patient-profile',
        'resource_scopes': [
            'patient-profile.read',
            'patient-profile.write'
        ],
        'ownerManagedAccess': True
    }

    try:
        requests.post(UMA_PROTECTION_API_RESOURCE, json=data, headers=headers)
    except Exception as e:
        raise Exception(f"Failed to create resource: {e}")




