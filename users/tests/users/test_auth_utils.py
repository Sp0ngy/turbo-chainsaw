from django.test import TestCase

from unittest.mock import patch, MagicMock

from users.auth_utils import has_required_scope, identify_requested_resource
from users.scopes import GlobalsScopes as gs

class TestAuthUtils(TestCase):

    def setUp(self):
        self.user_id = '281bf263-ea21-447d-b5e5-70fbc3f8061a'
        self.response_data = {
            'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ0ZmVOTGNhekRhcVZLMDVpTGxMNUJWdmhnTElZMGFPcnh0dG9oMC1nU3RvIn0.eyJleHAiOjE3MTAyMzI5MzMsImlhdCI6MTcxMDIzMjMzMywiYXV0aF90aW1lIjoxNzEwMjMxOTM5LCJqdGkiOiJiYmUxNmI1YS05ODk2LTRmMGUtYjgzNS1jMjAyZjFiYzMyNmYiLCJpc3MiOiJodHRwOi8vaWFtLmN1cmllc2NpZW5jZS5jb206ODA4MC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoidHVyYm8iLCJzdWIiOiIyODFiZjI2My1lYTIxLTQ0N2QtYjVlNS03MGZiYzNmODA2MWEiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ0dXJibyIsInNlc3Npb25fc3RhdGUiOiIzOTY1Yzc4YS1iOTcwLTQxM2MtODRiMS1lMDg5MjFjMTExNjIiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODAwMCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsicm9sZS5ncGFzLmFkbWluIiwiY3JlYXRlLXJlYWxtIiwicm9sZS5ncGFzLnVzZXIiLCJkZWZhdWx0LXJvbGVzLW1hc3RlciIsIm9mZmxpbmVfYWNjZXNzIiwiYWRtaW4iLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7InR0cC1yZWFsbSI6eyJyb2xlcyI6WyJ2aWV3LXJlYWxtIiwidmlldy1pZGVudGl0eS1wcm92aWRlcnMiLCJtYW5hZ2UtaWRlbnRpdHktcHJvdmlkZXJzIiwiaW1wZXJzb25hdGlvbiIsImNyZWF0ZS1jbGllbnQiLCJtYW5hZ2UtdXNlcnMiLCJxdWVyeS1yZWFsbXMiLCJ2aWV3LWF1dGhvcml6YXRpb24iLCJxdWVyeS1jbGllbnRzIiwicXVlcnktdXNlcnMiLCJtYW5hZ2UtZXZlbnRzIiwibWFuYWdlLXJlYWxtIiwidmlldy1ldmVudHMiLCJ2aWV3LXVzZXJzIiwidmlldy1jbGllbnRzIiwibWFuYWdlLWF1dGhvcml6YXRpb24iLCJtYW5hZ2UtY2xpZW50cyIsInF1ZXJ5LWdyb3VwcyJdfSwidHVyYm8iOnsicm9sZXMiOlsic3RhZmYiXX0sIm1hc3Rlci1yZWFsbSI6eyJyb2xlcyI6WyJ2aWV3LWlkZW50aXR5LXByb3ZpZGVycyIsInZpZXctcmVhbG0iLCJtYW5hZ2UtaWRlbnRpdHktcHJvdmlkZXJzIiwiaW1wZXJzb25hdGlvbiIsImNyZWF0ZS1jbGllbnQiLCJtYW5hZ2UtdXNlcnMiLCJxdWVyeS1yZWFsbXMiLCJ2aWV3LWF1dGhvcml6YXRpb24iLCJxdWVyeS1jbGllbnRzIiwicXVlcnktdXNlcnMiLCJtYW5hZ2UtZXZlbnRzIiwibWFuYWdlLXJlYWxtIiwidmlldy1ldmVudHMiLCJ2aWV3LXVzZXJzIiwidmlldy1jbGllbnRzIiwibWFuYWdlLWF1dGhvcml6YXRpb24iLCJtYW5hZ2UtY2xpZW50cyIsInF1ZXJ5LWdyb3VwcyJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwiYXV0aG9yaXphdGlvbiI6eyJwZXJtaXNzaW9ucyI6W3sic2NvcGVzIjpbInN0YWZmLXBvcnRhbC53cml0ZSIsInN0YWZmLXBvcnRhbC5yZWFkIl0sInJzaWQiOiI0NmQxYjRlOS1iZjg3LTRjM2MtODRmYy0yMGQwYTQwOGZjZGYiLCJyc25hbWUiOiJTdGFmZi1Qb3J0YWwifV19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIHBhdGllbnQtcHJvZmlsZS1hY2Nlc3MgZW1haWwiLCJzaWQiOiIzOTY1Yzc4YS1iOTcwLTQxM2MtODRiMS1lMDg5MjFjMTExNjIiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJOaWNvIFNjaMO8cnJsZSIsInByZWZlcnJlZF91c2VybmFtZSI6Im5pY29Ad2ViLmRlIiwiZ2l2ZW5fbmFtZSI6Ik5pY28iLCJjb25zZW50Ijp7InR1cmJvIjpbInRvcy1hY2NlcHRlZC12MS4wIl19LCJmYW1pbHlfbmFtZSI6IlNjaMO8cnJsZSIsImVtYWlsIjoibmljb0B3ZWIuZGUifQ.LUctNZOb498pvrXX1TDKAf6FUI6b2H627r_vRYUkdcoE6HH2_z8HBWIMxJeKwKbZNRvyoYEEmrbvC9s4_XXBsqjux9K3Gs0IGDemooXVzSQ35OxVkvHo5AXpkSCmvzCHOudT2d96Rea-oy4d5UXbtP8t7hMEi1HVGGUN0NP5QjQ9FVlooEgslr9pB33OuaA4-e4mFpnxtnZ9kKALz9mpsNDwZW96XGKM7-Klyux_HE1FNr5K-WgC9sg5dJt7cHrzx0I114RwMYdiMhdmFin2GMiic_aRpO5Um9J_sNKjDlrr-xCGy2FItsFdWsdm3iigABgRDIamybV2FtlKPtGGuw'
        }
        self.decoded_token = {
                  "exp": 1710232933,
                  "iat": 1710232333,
                  "auth_time": 1710231939,
                  "jti": "bbe16b5a-9896-4f0e-b835-c202f1bc326f",
                  "iss": "http://iam.curiescience.com:8080/realms/master",
                  "aud": "turbo",
                  "sub": "281bf263-ea21-447d-b5e5-70fbc3f8061a",
                  "typ": "Bearer",
                  "azp": "turbo",
                  "session_state": "3965c78a-b970-413c-84b1-e08921c11162",
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
                        "staff"
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
                  "authorization": {
                    "permissions": [
                      {
                        "scopes": [
                          "staff-portal.write",
                          "staff-portal.read"
                        ],
                        "rsid": "46d1b4e9-bf87-4c3c-84fc-20d0a408fcdf",
                        "rsname": "Staff-Portal"
                      }
                    ]
                  },
                  "scope": "openid profile patient-profile-access email",
                  "sid": "3965c78a-b970-413c-84b1-e08921c11162",
                  "email_verified": "false",
                  "name": "Mustermann Mustermann",
                  "preferred_username": "Mustermann@web.de",
                  "given_name": "Mustermann",
                  "consent": {
                    "turbo": [
                      "tos-accepted-v1.0"
                    ]
                  },
                  "family_name": "Mustermann",
                  "email": "Mustermann@web.de"
                }

        self.response_data_missing_permission = {
            'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ0ZmVOTGNhekRhcVZLMDVpTGxMNUJWdmhnTElZMGFPcnh0dG9oMC1nU3RvIn0.eyJleHAiOjE3MTAyMzQwMzEsImlhdCI6MTcxMDIzMzQzMSwiYXV0aF90aW1lIjoxNzEwMjMzNDIwLCJqdGkiOiIwNDZlMjRiNC1jMDkwLTQxZGMtYTY1NC1jZjhlNTk0MDRlMzgiLCJpc3MiOiJodHRwOi8vaWFtLmN1cmllc2NpZW5jZS5jb206ODA4MC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjI2NzI5OWZkLWEwNjEtNGUyZS1hMTc1LWY4M2EyZDE1MTViYiIsInR5cCI6IkJlYXJlciIsImF6cCI6InR1cmJvIiwibm9uY2UiOiJ4WHJIbjNDMkt0QktIS01PR082dVFFaHl3M2l3eWRZUyIsInNlc3Npb25fc3RhdGUiOiJkYjk3NmY0OC0xNDMwLTQyNDgtOGI3Ny00OWM5ZDEwNTRlYTMiLCJhY3IiOiIwIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODAwMCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1tYXN0ZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBwYXRpZW50LXByb2ZpbGUtYWNjZXNzIGVtYWlsIiwic2lkIjoiZGI5NzZmNDgtMTQzMC00MjQ4LThiNzctNDljOWQxMDU0ZWEzIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiU2FiaW5lMTIzNCBTY2jDvHJybGUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzYWJpbmVAd2ViLmRlIiwiZ2l2ZW5fbmFtZSI6IlNhYmluZTEyMzQiLCJjb25zZW50Ijp7InR1cmJvIjpbInRvcy1hY2NlcHRlZC12MS4wIl19LCJmYW1pbHlfbmFtZSI6IlNjaMO8cnJsZSIsImVtYWlsIjoic2FiaW5lQHdlYi5kZSJ9.Qrpk4LUsLFFVDDsAPzoYQtQ52PoVaFlk3fzF4LyvmsVnCCnO0BBhcqB6ZSDAivi_zTy_jFP7tyWOuD2AbIrPTnDHeI_uP44LyKhwovKJDSNdiYaR7EEnKRJv9v1WX-KBa2cqQWo7PY234SHwLyM6vMLXeFcu-VdmKAnrsUn7dyTHSr0e_mhvWBINad0ufuJ4hM_y5-_Mm9N6wVufYHCXPfVCgsJvhnT6lU14ByIsH3ag2FvJoFd-Quna_z-U8j9K0N4ARVtAymbkk29wMihLs5VU_BFOSEKvZzzOaXgesKs5zBJs0vtfrQpuus0Xvut1-gKSnMyBjHbNRD3UVneoRw'
            # others are not relevant
        }
        self.decoded_token_missing_permission = {
              "exp": 1710234031,
              "iat": 1710233431,
              "auth_time": 1710233420,
              "jti": "046e24b4-c090-41dc-a654-cf8e59404e38",
              "iss": "http://iam.curiescience.com:8080/realms/master",
              "aud": "account",
              "sub": "267299fd-a061-4e2e-a175-f83a2d1515bb",
              "typ": "Bearer",
              "azp": "turbo",
              "nonce": "xXrHn3C2KtBKHKMOGO6uQEhyw3iwydYS",
              "session_state": "db976f48-1430-4248-8b77-49c9d1054ea3",
              "acr": "0",
              "allowed-origins": [
                "http://localhost:8000"
              ],
              "realm_access": {
                "roles": [
                  "default-roles-master",
                  "offline_access",
                  "uma_authorization"
                ]
              },
              "resource_access": {
                "account": {
                  "roles": [
                    "manage-account",
                    "manage-account-links",
                    "view-profile"
                  ]
                }
              },
              "scope": "openid profile patient-profile-access email",
              "sid": "db976f48-1430-4248-8b77-49c9d1054ea3",
              "email_verified": "false",
              "name": "Mustermann Mustermann",
              "preferred_username": "sabine@web.de",
              "given_name": "Sabine1234",
              "consent": {
                "turbo": [
                  "tos-accepted-v1.0"
                ]
              },
              "family_name": "Mustermann",
              "email": "mustermann@web.de"
            }

        self.response_data_user_associated = {
            'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ0ZmVOTGNhekRhcVZLMDVpTGxMNUJWdmhnTElZMGFPcnh0dG9oMC1nU3RvIn0.eyJleHAiOjE3MTAyMzU4MDYsImlhdCI6MTcxMDIzNTIwNiwiYXV0aF90aW1lIjoxNzEwMjM0ODkwLCJqdGkiOiI2Yjg3ZDk0Yi1kOTFkLTRhZjktYTE4Ny0yYjQwM2NkYjZiNTMiLCJpc3MiOiJodHRwOi8vaWFtLmN1cmllc2NpZW5jZS5jb206ODA4MC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoidHVyYm8iLCJzdWIiOiI4NmRkZDQ3Ny1hNTM2LTQ3MWItOTRmZi1iN2E0ZmY3Y2Y1MjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ0dXJibyIsInNlc3Npb25fc3RhdGUiOiJiYjQ0MmU3MS02NGZlLTRlMzEtOWYwOC1iYTIzZDFlNzE2MmMiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODAwMCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1tYXN0ZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsidHVyYm8iOnsicm9sZXMiOlsic3RhZmYiXX0sImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sImF1dGhvcml6YXRpb24iOnsicGVybWlzc2lvbnMiOlt7InNjb3BlcyI6WyJwYXRpZW50LXByb2ZpbGUud3JpdGUiLCJwYXRpZW50LXByb2ZpbGUucmVhZCJdLCJyc2lkIjoiZjQ1Y2Y1MTctMjY1OC00ZGZhLWE4NWQtNWQ1NmFiNWZkZTY0IiwicnNuYW1lIjoiUGF0aWVudC1Qcm9maWxlLVAxOC04NmRkZDQ3Ny1hNTM2LTQ3MWItOTRmZi1iN2E0ZmY3Y2Y1MjkifV19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIHBhdGllbnQtcHJvZmlsZS1hY2Nlc3MgZW1haWwiLCJzaWQiOiJiYjQ0MmU3MS02NGZlLTRlMzEtOWYwOC1iYTIzZDFlNzE2MmMiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJCZXJmaW4gQ2FudGVwZSIsInByZWZlcnJlZF91c2VybmFtZSI6ImJlcmZpbkB3ZWIuZGUiLCJnaXZlbl9uYW1lIjoiQmVyZmluIiwiY29uc2VudCI6eyJ0dXJibyI6WyJ0b3MtYWNjZXB0ZWQtdjEuMCJdfSwiZmFtaWx5X25hbWUiOiJDYW50ZXBlIiwiZW1haWwiOiJiZXJmaW5Ad2ViLmRlIn0.W0sdEv_61MKoxdvjaGh_JcbH3ueginGgkkyWKlgGwIl6Pzwq0mNopZIfWgUGtXg7gsSnkXIfz5QqOLiodfjmdAmPGPxqwLdSsXaBf6SeAaBTja5P85ZKnSnUi3Re15gMnm9kfwmXW5iZRxesYylK3W3PhkithVk7froNvOLab4zL59MEAo8rTkzUiDhw6e2N9o8EQidRSPU90pvc4sikH5Jk-bwVVW4DbusiC9fgRP_CoqeZRQ6CHhOaEGRHgbWVPk5H-TDFiJT77fUaBlp5tqmI_HbGvaXYLetRL80uQHyWgbCd0s_f6Y6N7LtlgDYKCSsf6CJE-IuUUkeNGQGoag'
        }

        self.decoded_token_user_associated = {
              "exp": 1710235806,
              "iat": 1710235206,
              "auth_time": 1710234890,
              "jti": "6b87d94b-d91d-4af9-a187-2b403cdb6b53",
              "iss": "http://iam.curiescience.com:8080/realms/master",
              "aud": "turbo",
              "sub": "86ddd477-a536-471b-94ff-b7a4ff7cf529",
              "typ": "Bearer",
              "azp": "turbo",
              "session_state": "bb442e71-64fe-4e31-9f08-ba23d1e7162c",
              "acr": "1",
              "allowed-origins": [
                "http://localhost:8000"
              ],
              "realm_access": {
                "roles": [
                  "default-roles-master",
                  "offline_access",
                  "uma_authorization"
                ]
              },
              "resource_access": {
                "turbo": {
                  "roles": [
                    "staff"
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
              "authorization": {
                "permissions": [
                  {
                    "scopes": [
                      "patient-profile.write",
                      "patient-profile.read"
                    ],
                    "rsid": "f45cf517-2658-4dfa-a85d-5d56ab5fde64",
                    "rsname": "Patient-Profile-P18-86ddd477-a536-471b-94ff-b7a4ff7cf529"
                  }
                ]
              },
              "scope": "openid profile patient-profile-access email",
              "sid": "bb442e71-64fe-4e31-9f08-ba23d1e7162c",
              "email_verified": "false",
              "name": "Musterfrau Musterfrau",
              "preferred_username": "Musterfrau@web.de",
              "given_name": "Musterfrau",
              "consent": {
                "turbo": [
                  "tos-accepted-v1.0"
                ]
              },
              "family_name": "Musterfrau",
              "email": "Musterfrau@web.de"
            }


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


    @patch("users.auth_utils.decode_jwt_token")
    @patch("users.auth_utils.call_token_endpoint_with_resource_scope")
    def test_has_required_scope_generic_resource_authorized(self, mock_call_token_endpoint_with_resource_scope, mock_decode_jwt_token):
        mock_request = MagicMock()
        mock_request.session = {'oidc_access_token': 'not relevant token as it is mocked'}

        mock_call_token_endpoint_with_resource_scope.return_value = (self.response_data, 200)
        mock_decode_jwt_token.return_value = self.decoded_token

        result, msg = has_required_scope(mock_request, [gs.STAFF_PORTAL_READ, gs.STAFF_PORTAL_WRITE])

        self.assertTrue(result)
        self.assertEqual(msg, "Authorized")

    @patch("users.auth_utils.decode_jwt_token")
    @patch("users.auth_utils.call_token_endpoint_with_resource_scope")
    def test_has_required_scope_generic_resource_missing_permission(self, mock_call_token_endpoint_with_resource_scope, mock_decode_jwt_token):
        mock_request = MagicMock()
        mock_request.session = {'oidc_access_token': 'not relevant token as it is mocked'}

        mock_call_token_endpoint_with_resource_scope.return_value = (self.response_data_missing_permission, 200)
        mock_decode_jwt_token.return_value = self.decoded_token_missing_permission

        result, msg = has_required_scope(mock_request, [gs.STAFF_PORTAL_READ, gs.STAFF_PORTAL_WRITE])

        self.assertFalse(result)
        self.assertEqual(msg, "You do not have the required permission to access this resource.")

    @patch("users.auth_utils.decode_jwt_token")
    @patch("users.auth_utils.call_token_endpoint_with_resource_scope")
    def test_has_required_scope_user_associated_resource_authorized(self, mock_call_token_endpoint_with_resource_scope,
                                                            mock_decode_jwt_token):
        mock_request = MagicMock()
        mock_request.session = {'oidc_access_token': 'not relevant token as it is mocked'}

        mock_call_token_endpoint_with_resource_scope.return_value = (self.response_data_user_associated, 200)
        mock_decode_jwt_token.return_value = self.decoded_token_user_associated

        result, msg = has_required_scope(mock_request, [gs.PATIENT_PROFILE_READ, gs.PATIENT_PROFILE_WRITE], '56f0a1ab-6c73-465c-96ea-ce3d17428781')

        self.assertTrue(result)
        self.assertEqual(msg, "Authorized")

    @patch("users.auth_utils.decode_jwt_token")
    @patch("users.auth_utils.call_token_endpoint_with_resource_scope")
    def test_has_required_scope_user_associated_resource_missing_permission(self, mock_call_token_endpoint_with_resource_scope,
                                                                    mock_decode_jwt_token):
        mock_request = MagicMock()
        mock_request.session = {'oidc_access_token': 'not relevant token as it is mocked'}

        mock_call_token_endpoint_with_resource_scope.return_value = (self.response_data, 200)
        mock_decode_jwt_token.return_value = self.decoded_token

        result, msg = has_required_scope(mock_request, [gs.PATIENT_PROFILE_READ, gs.PATIENT_PROFILE_WRITE],
                                         '56f0a1ab-6c73-465c-96ea-ce3d17428781')

        self.assertFalse(result)
        self.assertEqual(msg, "You do not have the required permission to access this resource.")

    @patch("users.auth_utils.decode_jwt_token")
    @patch("users.auth_utils.call_token_endpoint_with_resource_scope")
    def test_has_required_scope_user_associated_resource_one_missing_permission(self,
                                                                            mock_call_token_endpoint_with_resource_scope,
                                                                            mock_decode_jwt_token):
        mock_request = MagicMock()
        mock_request.session = {'oidc_access_token': 'not relevant token as it is mocked'}

        mock_call_token_endpoint_with_resource_scope.return_value = (self.response_data_user_associated, 200)
        mock_decode_jwt_token.return_value = self.decoded_token_user_associated

        result, msg = has_required_scope(mock_request, [gs.PATIENT_PROFILE_READ, gs.STAFF_PORTAL_WRITE],
                                         '56f0a1ab-6c73-465c-96ea-ce3d17428781')

        self.assertFalse(result)
        self.assertEqual(msg, "You do not have the required permission to access this resource.")

    def test_raise_exception_for_identify_requested_resource(self):
        with self.assertRaisesRegex(ValueError, "One or more required scopes are not recognized. Please check, if you use the correct method for user-associated or generic resources."):
            identify_requested_resource([gs.PATIENT_PROFILE_WRITE, gs.PATIENT_PROFILE_READ])



