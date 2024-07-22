"""File with all tests show themes list and detail endpoints"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import ShowTheme
from planetarium.serializers import (
    ShowThemeListSerializer,
    ShowThemeDetailSerializer
)
from planetarium.tests.sample_functions import sample_show_theme

SHOW_THEMES_URL = reverse("planetarium:showtheme-list")


def detail_url(show_theme_id):
    """Return URL for detail endpoint of given id"""
    return reverse(
        "planetarium:showtheme-detail",
        args=[show_theme_id]
    )


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_show_theme_retrieve_list_serializer(self):
        """Test whether retrieve correct list serializer"""
        sample_show_theme()
        sample_show_theme(name="Test_first")
        sample_show_theme(name="Test_second")

        res = self.client.get(SHOW_THEMES_URL)
        show_themes = ShowTheme.objects.all()

        serializer = ShowThemeListSerializer(show_themes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_themes_filter_by_name(self):
        """Test whether filtering working correctly"""
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
        """Test whether detail endpoint retrieve correct detail serializer"""
        sample = sample_show_theme()

        url = detail_url(sample.id)
        res = self.client.get(url)

        show_theme = ShowTheme.objects.get(pk=sample.id)

        serializer = ShowThemeDetailSerializer(show_theme)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_session_str_correct(self):
        """Test whether str function return correct value"""
        show_theme = sample_show_theme()

        self.assertEqual(str(show_theme), show_theme.name)

    def test_show_theme_create_forbidden(self):
        """Test whether creation with incorrect data forbidden"""
        payload = {
            "name": "Test_theme"
        }

        res = self.client.post(SHOW_THEMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
