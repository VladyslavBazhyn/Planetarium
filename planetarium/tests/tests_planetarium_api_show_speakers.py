from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome, ShowSession, ShowTheme, AstronomyShow, ShowSpeaker, Reservation, Ticket
from planetarium.serializers import ShowSessionListSerializer, ShowSessionDetailSerializer, ReservationListSerializer, \
    ReservationDetailSerializer, ShowSpeakerListSerializer
from planetarium.tests.tests_planetarium_api_show_sessions import sample_show_session, sample_astronomy_show

SHOW_SPEAKERS_ULR = reverse("planetarium:showspeaker-list")


def sample_show_speaker(**params):

    default_data = {
        "first_name": "Test",
        "last_name": "Speaker",
        "profession": "Speaker"
    }

    default_data.update(params)

    return ShowSpeaker.objects.create(**default_data)

def detail_url(show_speaker_id):
    return reverse(
        "planetarium:showspeaker-detail",
        args=[show_speaker_id]
    )


class UnauthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()\


    def test_auth_required(self):
        res = self.client.get(SHOW_SPEAKERS_ULR)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_show_speaker_str_correct(self):
        show_speaker = sample_show_speaker()

        self.assertEqual(str(show_speaker), "Test Speaker")

    def test_show_speaker_retrieve_list(self):
        sample_show_speaker(first_name="Second")
        sample_show_speaker(last_name="Strong")
        sample_show_speaker(profession="Good Guy")

        res = self.client.get(SHOW_SPEAKERS_ULR)

        show_speakers = ShowSpeaker.objects.all()

        serializer = ShowSpeakerListSerializer(show_speakers, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

