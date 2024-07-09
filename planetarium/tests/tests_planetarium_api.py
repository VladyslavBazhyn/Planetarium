import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome, ShowTheme, AstronomyShow, ShowSession
from planetarium.serializers import AstronomyShowSerializer, AstronomyShowListSerializer

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def sample_astronomy_show(show_name=None, **def_param):
    def_show_name = "Zero"
    default_data = {
        "title": "Title test",
        "description": "Some description",
    }

    if show_name:
        def_show_name = show_name

    show_theme = ShowTheme.objects.create(
        name=def_show_name
    )

    default_data.update(def_param)

    astronomy_show = AstronomyShow.objects.create(**default_data)
    astronomy_show.show_themes.add(show_theme)

    return astronomy_show


def show_session_sample(**parameters):
    planetarium_dome = PlanetariumDome.objects.create(
        name="BIG", rows=10, seats_in_row=10
    )
    astronomy_show = sample_astronomy_show()

    default_data = {
        "planetarium_dome": planetarium_dome,
        "astronomy_show": astronomy_show,
        "show_day": "2025-01-01",
        "time_start": "14:00:00",
        "time_end": "15:00:00"
    }

    default_data.update(parameters)

    return ShowSession.objects.create(**default_data)


def poster_upload_url(astronomy_show_id: int):
    """Return URL for recipe poster upload"""
    return reverse(
        "planetarium:astronomyshow-upload-image",
        args=[astronomy_show_id]
    )


def detail_url(astronomy_show_id):
    return reverse(
        "planetarium:astronomyshow-detail",
        args=[astronomy_show_id]
    )


class UnauthenticatedUserPlanetariumApiTest(TestCase):
    def setup(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_list_ordering_astronomy_show(self):
        sample_astronomy_show(title="Atitle", show_name="First")
        sample_astronomy_show(title="BTitle", show_name="Second")
        sample_astronomy_show(title="CTitle", show_name="Third")

        res = self.client.get(ASTRONOMY_SHOW_URL)

        astronomy_shows = AstronomyShow.objects.all().order_by("title")
        serializer = AstronomyShowListSerializer(astronomy_shows, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_astronomy_show_filter_by_title(self):
        astronomy_show_1 = sample_astronomy_show(title="Atitle", show_name="First")
        astronomy_show_2 = sample_astronomy_show(title="BTitle", show_name="Second")
        astronomy_show_3 = sample_astronomy_show(title="CTi", show_name="Third")

        res = self.client.get(
            ASTRONOMY_SHOW_URL,
            {
                "title": "tle"
            }
        )

        serializer_1 = AstronomyShowListSerializer(astronomy_show_1)
        serializer_2 = AstronomyShowListSerializer(astronomy_show_2)
        serializer_3 = AstronomyShowListSerializer(astronomy_show_3)

        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertNotIn(serializer_3.data, res.data)




