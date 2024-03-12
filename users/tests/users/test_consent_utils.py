from django.test import TestCase

from unittest.mock import patch, MagicMock

from users.consent_utils import get_user_consent
from users.scopes import ConsentScopes as cs

class TestConsentUtils(TestCase):

    def setUp(self):
        self.user_id = '281bf263-ea21-447d-b5e5-70fbc3f8061a'
        self.consent_response_json = [{
            'lastUpdatedDate':  1710174060854,
            'clientId': 'turbo',
            'createdDate': 1710174060853,
            'grantedClientScopes': ['tos-accepted-v1.0', 'marketing-accepted-v1.0'],
            'additionalGrants': []
        }]

        self.PAT_token = {
                  "exp": 1710229676,
                  "iat": 1710229076,
                  "jti": "6fe85981-4600-4baf-b374-37958f03de64",
                  "iss": "http://iam.curiescience.com:8080/realms/master",
                  "aud": [
                    "ttp-realm",
                    "master-realm",
                    "account"
                  ],
                  "sub": "9e062eb2-9e2a-40d9-b332-8a01c85206ba",
                  "typ": "Bearer",
                  "azp": "turbo",
                  "acr": "1",
                  "allowed-origins": [
                    "http://localhost:8000"
                  ],
                  "realm_access": {
                    "roles": [
                      "role.gpas.admin",
                      "create-realm",
                      "role.gpas.user",
                      "default-roles-master",
                      "offline_access",
                      "admin",
                      "uma_authorization"
                    ]
                  },
                  "resource_access": {
                    "ttp-realm": {
                      "roles": [
                        "view-realm",
                        "view-identity-providers",
                        "manage-identity-providers",
                        "impersonation",
                        "create-client",
                        "manage-users",
                        "query-realms",
                        "view-authorization",
                        "query-clients",
                        "query-users",
                        "manage-events",
                        "manage-realm",
                        "view-events",
                        "view-users",
                        "view-clients",
                        "manage-authorization",
                        "manage-clients",
                        "query-groups"
                      ]
                    },
                    "turbo": {
                      "roles": [
                        "uma_protection"
                      ]
                    },
                    "master-realm": {
                      "roles": [
                        "view-identity-providers",
                        "view-realm",
                        "manage-identity-providers",
                        "impersonation",
                        "create-client",
                        "manage-users",
                        "query-realms",
                        "view-authorization",
                        "query-clients",
                        "query-users",
                        "manage-events",
                        "manage-realm",
                        "view-events",
                        "view-users",
                        "view-clients",
                        "manage-authorization",
                        "manage-clients",
                        "query-groups"
                      ]
                    },
                    "account": {
                      "roles": [
                        "manage-account",
                        "manage-account-links",
                        "view-profile"
                      ]
                    }
                  },
                  "scope": "profile patient-profile-access email",
                  "email_verified": "false",
                  "clientHost": "172.18.0.4",
                  "preferred_username": "service-account-turbo",
                  "consent": {},
                  "clientAddress": "172.18.0.4",
                  "client_id": "turbo"
                }

    @patch("users.pseudonymize_utils.get_gPAS_client")
    def test(self, mock_get_gpas_client):
        mock_client = MagicMock()
        mock_client.service.getOrCreatePseudonymFor.return_value = 'pseudonymized_value'
        mock_client.service.getValueFor.return_value = 'original_value'

        # Configure the mock_get_gpas_client to return the mock_client
        mock_get_gpas_client.return_value = mock_client

    @patch("users.consent_utils.get_consent_records")
    @patch("users.auth_utils.get_client_PAT_token")
    def test_get_user_consent(self, mock_get_client_PAT_token, mock_get_consent_records):
        mock_get_client_PAT_token.return_value = self.PAT_token
        mock_get_consent_records.return_value = self.consent_response_json

        grantedClientScopes = get_user_consent(self.user_id)

        self.assertIn(cs.TOS_ACCEPTED_V1_0, grantedClientScopes)
        self.assertIn(cs.MARKETING_ACCEPTED_V1_0, grantedClientScopes)

    @patch("users.auth_utils.get_client_PAT_token")
    def test_update_user_consent(self, mock_get_client_PAT_token):
        mock_get_client_PAT_token.return_value = self.PAT_token
        # Not testable as response from API would be mocked


