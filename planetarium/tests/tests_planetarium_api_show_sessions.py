"""File with all tests show session list and detail endpoints"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import ShowSession
from planetarium.serializers import (
    ShowSessionListSerializer,
    ShowSessionDetailSerializer
)
from planetarium.tests.sample_functions import (
    sample_show_session,
    sample_astronomy_show,
    sample_show_speaker
)

SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def detail_url(show_session_id):
    """Return URL for detail endpoint of given id"""
    return reverse(
        "planetarium:showsession-detail",
        args=[show_session_id]
    )


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_show_session_retrieve_list_and_list_ordering(self):
        """Test whether retrieve correct list serializer and it ordered correctly"""
        sample_show_session(
            show_day="2025-01-01",
            time_start="11:00:00",
            time_end="12:00:00",
            astronomy_show=sample_astronomy_show(
                show_theme_name="2_Test_zero", title="zero_title"
            ),
        )

        sample_show_session(
            show_day="2025-01-02",
            time_start="10:00:00",
            time_end="11:00:00",
            astronomy_show=sample_astronomy_show(
                show_theme_name="2_Test_first", title="first_title"
            ),
        )

        sample_show_session(
            show_day="2025-01-02",
            time_start="12:00:00",
            time_end="13:00:00",
            astronomy_show=sample_astronomy_show(
                show_theme_name="2_Test_second", title="second_title"
            ),
        )

        res = self.client.get(SHOW_SESSION_URL)

        show_sessions = ShowSession.objects.all().annotate(
            tickets_available=(
                    F("planetarium_dome__rows") *
                    F("planetarium_dome__seats_in_row")
                    - Count("tickets"))
        ).order_by("-show_day", "-time_start", "-time_end")

        serializer = ShowSessionListSerializer(show_sessions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_show_session_filters(self):
        """Test whether filtering working correctly"""
        sample_show_session(
            show_day="2025-01-01",
            time_start="11:00:00",
            time_end="12:00:00",
            astronomy_show=sample_astronomy_show(
                show_theme_name="Test_zero", title="2_zero_title"
            ),
        )

        sample_show_session(
            show_day="2025-01-02",
            time_start="10:00:00",
            time_end="11:00:00",
            astronomy_show=sample_astronomy_show(
                show_theme_name="Test_first", title="2_first_title"
            ),
        )

        sample_show_session(
            show_day="2025-01-03",
            time_start="12:00:00",
            time_end="13:00:00",
            astronomy_show=sample_astronomy_show(
                show_theme_name="Test_second", title="C_second_title"
            ),
        )

        res = self.client.get(
            SHOW_SESSION_URL,
            {"show_title": "2"}
        )

        queryset = ShowSession.objects.order_by(
            "-show_day", "-time_start", "-time_end"
        ).filter(
            astronomy_show__title__icontains="2"
        ).annotate(
            tickets_available=(
                    F("planetarium_dome__rows")
                    * F("planetarium_dome__seats_in_row")
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
                    F("planetarium_dome__rows")
                    * F("planetarium_dome__seats_in_row")
                    - Count("tickets")
            )
        )
        serializer = ShowSessionListSerializer(queryset, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_show_session_retrieve_detail(self):
        """Test whether detail endpoint retrieve correct detail serializer"""
        sample = sample_show_session()

        url = detail_url(sample.id)
        res = self.client.get(url)

        show_session = ShowSession.objects.annotate(
            tickets_available=(
                    F("planetarium_dome__rows")
                    * F("planetarium_dome__seats_in_row")
                    - Count("tickets")
            )
        ).get(pk=sample.id)

        serializer = ShowSessionDetailSerializer(show_session)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_session_create_forbidden(self):
        """Test whether creation with incorrect data forbidden"""
        payload = {
            "show_day": "2025-03-03"
        }

        res = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_show_session_with_one_speaker_in_same_time_forbidden(self):
        """
        Test whether validation of show speakers
        working time validate correctly. To prevent creating
        two different show session for one speaker at the same time
        """

        astronomy_show = sample_astronomy_show()
        show_speaker = sample_show_speaker()

        sample_show_session(
            show_speaker=show_speaker,
            astronomy_show=astronomy_show,
            show_day="2025-01-01",
            time_start="14:00:00",
            time_end="15:00:00"
        )
        with self.assertRaises(ValidationError):
            sample_show_session(
                show_speaker=show_speaker,
                astronomy_show=astronomy_show,
                show_day="2025-01-01",
                time_start="14:00:00",
                time_end="15:00:00"
            )
