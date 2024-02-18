from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.authtoken.models import Token
from .views import login, signup
from .serializers import UserSerializer


class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_login_success(self):
        # Create a user
        username = 'testuser'
        password = 'testpassword'
        user = User.objects.create_user(username=username, password=password)

        # Make a login request
        request_data = {'username': username, 'password': password}
        request = self.factory.post('/login/', request_data)
        response = login(request)

        # Check response status and content
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user'], UserSerializer(user).data)

    def test_login_invalid_credentials(self):
        # Make a login request with invalid credentials
        request_data = {'username': 'invaliduser',
                        'password': 'invalidpassword'}
        request = self.factory.post('/login/', request_data)
        response = login(request)

        # Check response status and content
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'detail': 'Invalid Credentials'})

    def test_signup_success(self):
        # Make a signup request
        username = 'testuser'
        password = 'testpassword'
        request_data = {'username': username, 'password': password}
        request = self.factory.post('/signup/', request_data)
        response = signup(request)

        # Check response status and content
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_signup_invalid_data(self):
        # Make a signup request with invalid data
        request_data = {'username': '', 'password': 'testpassword'}
        request = self.factory.post('/signup/', request_data)
        response = signup(request)

        # Check response status and content
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
