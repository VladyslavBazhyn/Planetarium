import os

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome, ShowSession, ShowTheme, AstronomyShow, ShowSpeaker
from planetarium.serializers import ShowSessionListSerializer, ShowSessionDetailSerializer

SHOW_SESSION_URL = reverse("planetarium:showsession-list")


# Function to create sample planetarium dome
def sample_planetarium_dome(**parameters):
    default_data = {
        "name": "Test_dome",
        "rows": 10,
        "seats_in_row": 10
    }

    default_data.update(parameters)

    return PlanetariumDome.objects.create(**default_data)


# Function to create sample show speakers
def sample_show_speaker(**parameters):
    default_data = {
        "first_name": "Bob",
        "last_name": "Obo",
        "profession": "Bodoviec"
    }

    default_data.update(parameters)

    return ShowSpeaker.objects.create(**default_data)


def sample_show_theme(**params):
    name = "Test_theme"

    if params.get("name"):
        name = params.get("name")

    return ShowTheme.objects.create(name=name)


# Function to create a sample astronomy show
def sample_astronomy_show(**params):
    default_data = {
        "title": "Title test",
        "description": "Some description",
    }

    show_theme_name = None

    if params.get("show_theme_name"):
        show_theme_name = params.pop("show_theme_name")

    show_theme = sample_show_theme(name=show_theme_name)

    default_data.update(params)

    astronomy_show = AstronomyShow.objects.create(**default_data)
    astronomy_show.show_themes.add(show_theme)

    return astronomy_show


# Function to create sample show session
def sample_show_session(**parameters):
    if "show_speaker" not in parameters:
        show_speaker = sample_show_speaker()
    if "show_speaker" in parameters:
        show_speaker = parameters.pop("show_speaker")

    if "astronomy_show" not in parameters:
        astronomy_show = sample_astronomy_show()
    if "astronomy_show" in parameters:
        astronomy_show = parameters.pop("astronomy_show")

    if "planetarium_dome" not in parameters:
        planetarium_dome = sample_planetarium_dome()
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

    show_session.show_speakers.add(show_speaker)

    return show_session


def detail_url(show_session_id):
    return reverse(
        "planetarium:showsession-detail",
        args=[show_session_id]
    )


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
        show_session_1 = sample_show_session(
            show_day="2025-01-01",
            time_start="11:00:00",
            time_end="12:00:00",
            astronomy_show=sample_astronomy_show(show_theme_name="2_Test_zero", title="zero_title"),
        )

        show_session_2 = sample_show_session(
            show_day="2025-01-02",
            time_start="10:00:00",
            time_end="11:00:00",
            astronomy_show=sample_astronomy_show(show_theme_name="2_Test_first", title="first_title"),
        )

        show_session_3 = sample_show_session(
            show_day="2025-01-02",
            time_start="12:00:00",
            time_end="13:00:00",
            astronomy_show=sample_astronomy_show(show_theme_name="2_Test_second", title="second_title"),
        )

        res = self.client.get(SHOW_SESSION_URL)

        show_sessions = ShowSession.objects.all().annotate(
            tickets_available=(
                    F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
                    - Count("tickets"))
            )

        serializer = ShowSessionListSerializer(show_sessions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_show_session_filters(self):
        show_session_1 = sample_show_session(
            show_day="2025-01-01",
            time_start="11:00:00",
            time_end="12:00:00",
            astronomy_show=sample_astronomy_show(show_theme_name="Test_zero", title="2_zero_title"),
        )

        show_session_2 = sample_show_session(
            show_day="2025-01-02",
            time_start="10:00:00",
            time_end="11:00:00",
            astronomy_show=sample_astronomy_show(show_theme_name="Test_first", title="2_first_title"),
        )

        show_session_3 = sample_show_session(
            show_day="2025-01-02",
            time_start="12:00:00",
            time_end="13:00:00",
            astronomy_show=sample_astronomy_show(show_theme_name="Test_second", title="C_second_title"),
        )

        res = self.client.get(
            SHOW_SESSION_URL,
            {"show_title": "2"}
        )

        queryset = ShowSession.objects.filter(
            astronomy_show__title__icontains="2"
        ).annotate(
            tickets_available=(
                    F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
                    - Count("tickets")
            )
        )
        serializer = ShowSessionListSerializer(queryset, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

        res = self.client.get(
            SHOW_SESSION_URL,
            {"date": "2025-01-02"}
        )

        queryset = ShowSession.objects.filter(
            show_day="2025-01-02"
        ).annotate(
            tickets_available=(
                    F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
                    - Count("tickets")
            )
        )
        serializer = ShowSessionListSerializer(queryset, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_show_session_retrieve_detail(self):
        sample = sample_show_session()

        url = detail_url(sample.id)
        res = self.client.get(url)

        show_session = ShowSession.objects.annotate(
            tickets_available=(
                    F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
                    - Count("tickets")
            )
        ).get(pk=sample.id)

        serializer = ShowSessionDetailSerializer(show_session)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_session_create_forbidden(self):
        payload = {
            "show_day": "2025-03-03"
        }

        res = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
