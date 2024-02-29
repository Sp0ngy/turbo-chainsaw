import requests
from django.contrib.auth.models import Group
from django.db import transaction
from django_project.settings import OIDC_OP_TOKEN_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET, UMA_PROTECTION_API_RESOURCE
from mozilla_django_oidc import auth

from ehr.models import Patient
from users.models import Resource


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
        # Create a new resource and save in app db
        resource_id = create_resource(user)
        save_resource_in_db(user, resource_id, Resource.ResourceTypes.PATIENT_PROFILE)
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

def create_resource(user):
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

    resource_name = f'Patient-Profile-{user.patient.identifier}-{user.keycloak_id}'

    # Create a new resource
    #TODO: add script to add policies, scopes, etc. if not existing, based on django_project/permission.py GlobalScopes
    headers = {'Authorization': f'Bearer {pat}', 'Content-Type': 'application/json'}
    data = {
        'name': resource_name,
        'type': 'urn:turbo:resources:patient-profile',
        'resource_scopes': [
            'patient-profile.read',
            'patient-profile.write'
        ],
        'attributes': {'associated_user_id': user.keycloak_id}
    }

    try:
        response = requests.post(UMA_PROTECTION_API_RESOURCE, json=data, headers=headers)
        if response.ok:
            resource_data = response.json()  # Assuming response contains resource ID
            resource_id = resource_data.get('_id')  # Extract the actual resource ID
            return resource_id
    except Exception as e:
        raise Exception(f"Failed to create resource: {e}")


def save_resource_in_db(user, resource_id, type):
    Resource.objects.create(user=user, keycloak_resource_id=resource_id, type=type)
    return







