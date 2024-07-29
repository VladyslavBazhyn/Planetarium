"""File with all tests show speaker list and detail endpoints"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import ShowSpeaker
from planetarium.serializers import (
    ShowSpeakerListSerializer,
    ShowSpeakerDetailSerializer
)
from planetarium.tests.sample_functions import sample_show_speaker

SHOW_SPEAKERS_ULR = reverse("planetarium:showspeaker-list")


def detail_url(show_speaker_id):
    """Return URL for detail endpoint of given id"""
    return reverse(
        "planetarium:showspeaker-detail",
        args=[show_speaker_id]
    )


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_show_speaker_str_correct(self):
        """Test whether str function return correct value"""
        show_speaker = sample_show_speaker()

        self.assertEqual(str(show_speaker), "Bob Obo")

    def test_show_speaker_retrieve_list_serializer(self):
        """Test whether retrieve correct list serializer"""
        sample_show_speaker(first_name="Second")
        sample_show_speaker(last_name="Strong")
        sample_show_speaker(profession="Good Guy")

        res = self.client.get(SHOW_SPEAKERS_ULR)

        show_speakers = ShowSpeaker.objects.all()

        serializer = ShowSpeakerListSerializer(show_speakers, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_speaker_filters(self):
        """Test whether filtering working correctly"""
        sample_show_speaker(first_name="Second")
        sample_show_speaker(last_name="Strong")
        sample_show_speaker(profession="Good Guy")

        show_speaker_1 = ShowSpeaker.objects.filter(
            first_name="Second"
        ).first()
        show_speaker_2 = ShowSpeaker.objects.filter(
            last_name="Strong"
        ).first()
        show_speaker_3 = ShowSpeaker.objects.filter(
            profession="Good Guy"
        ).first()

        res_1 = self.client.get(
            SHOW_SPEAKERS_ULR,
            {"first_name": "Seco"}
        )
        res_2 = self.client.get(
            SHOW_SPEAKERS_ULR,
            {"last_name": "Stro"}
        )
        res_3 = self.client.get(
            SHOW_SPEAKERS_ULR,
            {"profession": "Good"}
        )

        serializer_1 = ShowSpeakerListSerializer(show_speaker_1)
        serializer_2 = ShowSpeakerListSerializer(show_speaker_2)
        serializer_3 = ShowSpeakerListSerializer(show_speaker_3)

        self.assertEqual(res_1.status_code, status.HTTP_200_OK)
        self.assertEqual(res_2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_3.status_code, status.HTTP_200_OK)

        self.assertIn(serializer_1.data, res_1.data)
        self.assertNotIn(serializer_2.data, res_1.data)
        self.assertNotIn(serializer_3.data, res_1.data)

        self.assertNotIn(serializer_1.data, res_2.data)
        self.assertIn(serializer_2.data, res_2.data)
        self.assertNotIn(serializer_3.data, res_2.data)

        self.assertNotIn(serializer_1.data, res_3.data)
        self.assertNotIn(serializer_2.data, res_3.data)
        self.assertIn(serializer_3.data, res_3.data)

    def test_show_speaker_retrieve_detail(self):
        """Test whether detail endpoint retrieve correct detail serializer"""
        show_speaker = sample_show_speaker(first_name="Second")

        url = detail_url(show_speaker.id)
        res = self.client.get(url)

        serializer = ShowSpeakerDetailSerializer(show_speaker)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_speaker_create_forbidden(self):
        """Test whether creation with incorrect data forbidden"""
        payload = {
            "first_name": "Bob",
            "last_name": "Good"
        }

        res = self.client.post(SHOW_SPEAKERS_ULR, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
