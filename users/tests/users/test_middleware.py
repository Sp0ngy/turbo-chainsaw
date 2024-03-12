from django.test import TestCase, RequestFactory
from django.http import HttpResponseForbidden
from unittest.mock import patch, MagicMock
from users.middleware import ConsentCheckMiddleware
from django_project.settings import OIDC_RP_CLIENT_ID


class ConsentCheckMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('users.middleware.decode_jwt_token')
    def test_process_request_with_consent(self, mock_decode_jwt_token):
        get_response = MagicMock()
        # Setup
        request = self.factory.get('/')
        request.session = {'oidc_access_token': 'some_access_token'}
        mock_decode_jwt_token.return_value = {'consent': {
            OIDC_RP_CLIENT_ID: ['tos-accepted-v1.0']
        }}

        middleware = ConsentCheckMiddleware(get_response)
        response = middleware(request=request)

        self.assertEqual(get_response.return_value, response)

    @patch('users.middleware.decode_jwt_token')
    def test_process_request_without_TOS_consent(self, mock_decode_jwt_token):
        get_response = MagicMock()
        # Setup
        request = self.factory.get('/')
        request.session = {'oidc_access_token': 'some_access_token'}
        mock_decode_jwt_token.return_value = {'consent': {
            OIDC_RP_CLIENT_ID: []
        }}

        middleware = ConsentCheckMiddleware(get_response)
        response = middleware(request=request)

        self.assertIsInstance(response, HttpResponseForbidden)

    def test_exempt_paths(self):
        get_response = MagicMock()
        middleware = ConsentCheckMiddleware(get_response)

        exempt_paths = [
            '/auth',
            '/authenticate',
            '/callback',
            '/logout',
            '/consent',
        ]

        for path in exempt_paths:
            with self.subTest(path=path):
                request = self.factory.get(path)
                response = middleware(request=request)

                # Ensure get_response is called for exempt paths, indicating the request is allowed to proceed.
                get_response.assert_called_once_with(request)

                # Reset mock for the next iteration
                get_response.reset_mock()

