"""File with all tests planetarium dome list and detail endpoints"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome
from planetarium.serializers import PlanetariumDomeSerializer
from planetarium.tests.sample_functions import sample_planetarium_dome

PLANETARIUM_DOME_URL = reverse("planetarium:planetariumdome-list")


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_planetarium_dome_str_correct(self):
        """Test whether str function return correct value"""
        dome_1 = sample_planetarium_dome()

        self.assertEqual(str(dome_1), dome_1.name)

    def test_planetarium_dome_retrieve_serializer(self):
        """Test whether retrieve correct serializer"""
        sample_planetarium_dome()
        sample_planetarium_dome(name="1_Test_dome")
        sample_planetarium_dome(name="1_Test_dome_again")

        res = self.client.get(PLANETARIUM_DOME_URL)

        domes = PlanetariumDome.objects.all()

        serializer = PlanetariumDomeSerializer(domes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_planetarium_dome_filter_by_capacity(self):
        """Test whether filtering working correctly"""
        dome_1 = sample_planetarium_dome(rows=1, seats_in_row=5)
        dome_2 = sample_planetarium_dome(rows=1, seats_in_row=10)
        dome_3 = sample_planetarium_dome(rows=1, seats_in_row=100)

        res = self.client.get(
            PLANETARIUM_DOME_URL,
            {"capacity": 10}
        )

        serializer_1 = PlanetariumDomeSerializer(dome_1)
        serializer_2 = PlanetariumDomeSerializer(dome_2)
        serializer_3 = PlanetariumDomeSerializer(dome_3)

        self.assertNotIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertIn(serializer_3.data, res.data)

    def test_planetarium_dome_create_forbidden(self):
        """Test whether creation with incorrect data forbidden"""
        sample_planetarium_dome()

        payload = {
            "name": "Changed_name"
        }

        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
