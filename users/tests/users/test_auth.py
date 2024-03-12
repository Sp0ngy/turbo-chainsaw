from unittest.mock import patch
from django.test import TestCase

from users.auth import OIDCAuthenticationBackend
from users.models import Resource
from ehr.models import Patient
class TestAuthBackend(TestCase):
    def setUp(self):
        self.claims = {
            'sub': 'test_keycloak_id',
            'roles': ['admin']
        }
        self.auth_backend = OIDCAuthenticationBackend()

    @patch("users.auth.create_resource")
    def test_create_user(self, mock_create_resource):
        mock_create_resource.return_value = 'resource_id'

        user = self.auth_backend.create_user(self.claims)

        self.assertIsNotNone(user.id, "User has been created.")
        self.assertEqual(user.keycloak_id, self.claims['sub'])
        self.assertTrue(user.is_staff, True)
        self.assertTrue(user.is_superuser, True)

        patient = Patient.objects.filter(user=user).first()
        self.assertIsNotNone(patient, "Patient profile has been created for the user.")

        resource = Resource.objects.filter(user=user, type=Resource.ResourceTypes.PATIENT_PROFILE).first()
        self.assertIsNotNone(resource, "Resource for patient profile has been created.")

