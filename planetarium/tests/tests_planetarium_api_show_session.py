import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome, ShowSession, ShowTheme, AstronomyShow, ShowSpeaker
from planetarium.serializers import ShowSessionListSerializer

SHOW_SESSION_URL = reverse("planetarium:showsession-list")


# Function to create a sample astronomy show
def sample_astronomy_show(**def_param):
    def_show_name = "Zero"
    default_data = {
        "title": "Title test",
        "description": "Some description",
    }

    if def_param.get("show_name"):
        def_show_name = def_param.pop("show_name")

    show_theme = ShowTheme.objects.create(name=def_show_name)

    default_data.update(def_param)

    astronomy_show = AstronomyShow.objects.create(**default_data)
    astronomy_show.show_themes.add(show_theme)

    return astronomy_show

# Function to create sample show speakers
def sample_show_speakers(**parameters):
    default_data = {
        "first_name": "Bob",
        "last_name": "Obo",
        "profession": "Bodoviec"
    }

    default_data.update(parameters)

    return ShowSpeaker.objects.create(**default_data)

# Function to create sample planetarium dome
def sample_planetarium_dome(**parameters):
    default_data = {
        "name": "Test_dome",
        "rows": 10,
        "seats_in_row": 10
    }

    default_data.update(parameters)

    return PlanetariumDome.objects.create(**default_data)

# Function to create sample show session
def sample_show_session(**parameters):
    astronomy_show = sample_astronomy_show(show_name=parameters.pop("show_theme_name", "Zero"))
    planetarium_dome = sample_planetarium_dome()
    show_speakers = [sample_show_speakers()]

    if "show_speakers" in parameters:
        show_speakers = parameters.pop("show_speakers")

    if "astronomy_show" in parameters:
        astronomy_show = parameters.pop("astronomy_show")

    if "planetarium_dome" in parameters:
        planetarium_dome = parameters.pop("planetarium_dome")

    default_data = {
        "astronomy_show": astronomy_show,
        "planetarium_dome": planetarium_dome,
        "show_day": "2025-01-01",
        "time_start": "14:00:00",
        "time_end": "15:00:00"
    }
    default_data.update(parameters)

    show_session = ShowSession.objects.create(**default_data)

    for speaker in show_speakers:
        show_session.show_speakers.add(speaker)

    return show_session



class UnauthenticatedUserPlanetariumApiTest(TestCase):
    def setup(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_show_session_retrieve_list_and_list_ordering(self):
        planetarium_dome = sample_planetarium_dome()

        show_session_1 = ShowSession.objects.create(
            show_day="2025-01-01",
            time_start="11:00:00",
            time_end="12:00:00",
            astronomy_show=sample_astronomy_show(show_name="Test_zero", title="first_title"),
            planetarium_dome=planetarium_dome
        )
        show_session_2 = ShowSession.objects.create(
            show_day="2025-01-02",
            time_start="10:00:00",
            time_end="11:00:00",
            astronomy_show=sample_astronomy_show(show_name="Test_first", title="second_title"),
            planetarium_dome=planetarium_dome

        )
        show_session_3 = ShowSession.objects.create(
            show_day="2025-01-02",
            time_start="12:00:00",
            time_end="13:00:00",
            astronomy_show=sample_astronomy_show(show_name="Test_second", title="third_title"),
            planetarium_dome=planetarium_dome

        )

        res = self.client.get(SHOW_SESSION_URL)

        show_sessions = ShowSession.objects.all().order_by(
            "-show_day",
            "-time_start",
            "-time_end"
        )

        serializer = ShowSessionListSerializer(show_sessions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
