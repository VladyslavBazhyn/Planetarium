from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome, ShowSession, ShowTheme, AstronomyShow, ShowSpeaker
from planetarium.serializers import ShowSessionListSerializer, ShowSessionDetailSerializer, ShowSessionSerializer, \
    ShowThemeListSerializer, ShowThemeDetailSerializer

SHOW_THEMES_URL = reverse("planetarium:showtheme-list")


def detail_url(show_theme_id):
    return reverse(
        "planetarium:showtheme-detail",
        args=[show_theme_id]
    )

def sample_show_theme(**params):
    def_params = {
        "name": "Test_theme_zero"
    }
    def_params.update(params)
    return ShowTheme.objects.create(**def_params)


class UnauthenticatedUserPlanetariumApiTest(TestCase):
    def setup(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_THEMES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_show_theme_retrieve_list(self):
        sample_show_theme()
        sample_show_theme(name="Test_first")
        sample_show_theme(name="Test_second")

        res = self.client.get(SHOW_THEMES_URL)
        show_themes = ShowTheme.objects.all()

        serializer = ShowThemeListSerializer(show_themes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_themes_filter_by_name(self):
        show_theme_1 = sample_show_theme()
        show_theme_2 = sample_show_theme(name="1_Test_first")
        show_theme_3 = sample_show_theme(name="1_Test_second")

        res = self.client.get(
            SHOW_THEMES_URL,
            {"name": "1"}
        )

        serializer_1 = ShowThemeListSerializer(show_theme_1)
        serializer_2 = ShowThemeListSerializer(show_theme_2)
        serializer_3 = ShowThemeListSerializer(show_theme_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertIn(serializer_3.data, res.data)

    def test_show_theme_retrieve_detail(self):
        sample = sample_show_theme()

        url = detail_url(sample.id)
        res = self.client.get(url)

        show_theme = ShowTheme.objects.get(pk=sample.id)

        serializer = ShowThemeDetailSerializer(show_theme)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_session_str_correct(self):
        show_theme = sample_show_theme()

        self.assertEqual(str(show_theme), show_theme.name)

    def test_show_theme_create_forbidden(self):
        payload = {
            "name": "Test_theme"
        }

        res = self.client.post(SHOW_THEMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

