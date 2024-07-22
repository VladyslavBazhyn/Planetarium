"""File with all tests for user model"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_THEMES_URL = reverse("planetarium:showtheme-list")
PLANETARIUM_DOME_URL = reverse("planetarium:planetariumdome-list")
RESERVATIONS_URL = reverse("planetarium:reservation-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")
SHOW_SPEAKERS_ULR = reverse("planetarium:showspeaker-list")

USER_ME_URL = reverse("user:manage")
USER_REGISTER_URL = reverse("user:create")
USER_TOKEN_URL = reverse("user:token_obtain_pair")
USER_TOKEN_REFRESH_URL = reverse("user:token_refresh")
USER_TOKEN_VERIFY_URL = reverse("user:token_verify")


class UnauthenticatedUserPlanetariumApiTest(TestCase):
    def setup(self):
        self.client = APIClient()

    def test_auth_required(self):

        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.get(SHOW_THEMES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.get(PLANETARIUM_DOME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.get(RESERVATIONS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.get(SHOW_SPEAKERS_ULR)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.get(USER_ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {
            "email": "same@mail.com",
            "password": "some password"
        }
        res = self.client.post(USER_TOKEN_URL, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        registration_data = {
            "email": "test@test.com",
            "password": "testpass",
            "username": "testuser"
        }
        res = self.client.post(USER_REGISTER_URL, registration_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = {
            "refresh": "invalidtokenrefresh"
        }
        res = self.client.post(USER_TOKEN_REFRESH_URL, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {
            "token": "invalidtoken"
        }
        res = self.client.post(USER_TOKEN_VERIFY_URL, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_user_do_not_have_username_field(self):
        """User model should"t have a "username" field"""
        self.assertEqual(
            getattr(self.user, "username"),
            None
        )
