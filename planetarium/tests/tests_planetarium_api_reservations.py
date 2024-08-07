"""File with all tests reservation list and detail endpoints"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import Reservation, Ticket
from planetarium.serializers import (
    ReservationListSerializer,
    ReservationDetailSerializer
)
from planetarium.tests.sample_functions import (
    sample_reservation,
    sample_astronomy_show,
    sample_show_session
)

RESERVATIONS_URL = reverse("planetarium:reservation-list")


def detail_url(reservation_id):
    """Return URL for detail endpoint of given id"""
    return reverse(
        "planetarium:reservation-detail",
        args=[reservation_id]
    )


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.user_2 = get_user_model().objects.create_user(
            "test_2@test.com",
            "testpasword"
        )
        self.user_3 = get_user_model().objects.create_user(
            "test_3@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_reservation_retrieve_list_and_list_ordering(self):
        """Test whether retrieve correct list serializer and it ordered correctly"""
        sample_reservation(user=self.user)
        sample_reservation(user=self.user_2)
        sample_reservation(user=self.user_3)

        res = self.client.get(RESERVATIONS_URL)

        reservations = Reservation.objects.all().order_by(
            "-created_at"
        )

        serializer = ReservationListSerializer(
            reservations, many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_reservation_filter_by_show_session_title(self):
        """Test whether filtering working correctly"""
        astronomy_show_1 = sample_astronomy_show(
            title="First", show_theme_name="2_test"
        )
        astronomy_show_2 = sample_astronomy_show(
            title="Second", show_theme_name="1_test"
        )

        show_session_1 = sample_show_session(
            astronomy_show=astronomy_show_1
        )
        show_session_2 = sample_show_session(
            astronomy_show=astronomy_show_2
        )

        reservation_1 = sample_reservation()
        reservation_2 = sample_reservation()

        Ticket.objects.create(
            reservation=reservation_1,
            show_session=show_session_1,
            row=1,
            seat=1
        )
        Ticket.objects.create(
            reservation=reservation_2,
            show_session=show_session_2,
            row=1,
            seat=2
        )

        queryset = Reservation.objects.filter(
            tickets__show_session__astronomy_show__title__icontains="First"
        )

        res = self.client.get(
            RESERVATIONS_URL,
            {"show_title": "First"}
        )

        serializer = ReservationListSerializer(queryset, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_reservation_retrieve_detail(self):
        """Test whether detail endpoint retrieve correct detail serializer"""
        astronomy_show_1 = sample_astronomy_show(
            title="First", show_theme_name="2_test"
        )
        show_session_1 = sample_show_session(
            astronomy_show=astronomy_show_1
        )
        reservation_1 = sample_reservation()
        Ticket.objects.create(
            reservation=reservation_1,
            show_session=show_session_1,
            row=1,
            seat=1
        )

        url = detail_url(reservation_1.id)
        res = self.client.get(url)

        reservation = Reservation.objects.get(pk=reservation_1.id)

        serializer = ReservationDetailSerializer(reservation)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_reservation_create_forbidden(self):
        """Test whether creation with incorrect data forbidden"""
        astronomy_show_1 = sample_astronomy_show(
            title="First", show_theme_name="2_test"
        )

        payload = {
            "astronomy_show": astronomy_show_1
        }

        res = self.client.post(RESERVATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
