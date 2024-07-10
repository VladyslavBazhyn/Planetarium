import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome, ShowSession, ShowTheme, AstronomyShow
from planetarium.tests.tests_planetarium_api_astronomy_show import sample_astronomy_show

SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def sample_show_session(**parameters):
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


class UnauthenticatedUserPlanetariumApiTest(TestCase):
    def setup(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    AstronomyShow.objects.all().delete()
