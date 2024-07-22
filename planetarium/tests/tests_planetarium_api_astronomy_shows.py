"""File with all tests astronomy show list and detail endpoints"""

import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import AstronomyShow
from planetarium.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer
)
from planetarium.tests.sample_functions import (
    sample_astronomy_show,
    sample_show_session
)

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")


def poster_upload_url(astronomy_show_id: int):
    """Return URL for recipe poster upload"""
    return reverse(
        "planetarium:astronomyshow-upload-poster",
        args=[astronomy_show_id]
    )


def detail_url(astronomy_show_id):
    return reverse(
        "planetarium:astronomyshow-detail",
        args=[astronomy_show_id]
    )


class AuthenticatedUserPlanetariumApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasword"
        )
        self.client.force_authenticate(self.user)

    def test_astronomy_show_str_correct(self):
        sample = sample_astronomy_show()

        self.assertEqual(str(sample), sample.title)

    def test_astronomy_show_retrieve_list_and_list_ordering(self):
        sample_astronomy_show(title="1_Atitle", show_theme_name="First")
        sample_astronomy_show(title="1_BTitle", show_theme_name="Second")
        sample_astronomy_show(title="1_CTitle", show_theme_name="Third")

        res = self.client.get(
            ASTRONOMY_SHOW_URL,
            {"title": "1"}
        )

        astronomy_shows = AstronomyShow.objects.all().order_by("title")
        serializer = AstronomyShowListSerializer(astronomy_shows, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_astronomy_show_filter_by_title(self):
        astronomy_show_1 = sample_astronomy_show(
            title="Atitle", show_theme_name="First"
        )
        astronomy_show_2 = sample_astronomy_show(
            title="BTitle", show_theme_name="Second"
        )
        astronomy_show_3 = sample_astronomy_show(
            title="CTi", show_theme_name="Third"
        )

        res = self.client.get(
            ASTRONOMY_SHOW_URL,
            {"title": "tle"}
        )

        serializer_1 = AstronomyShowListSerializer(astronomy_show_1)
        serializer_2 = AstronomyShowListSerializer(astronomy_show_2)
        serializer_3 = AstronomyShowListSerializer(astronomy_show_3)

        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertNotIn(serializer_3.data, res.data)

    def test_astronomy_show_retrieve_detail(self):
        sample = sample_astronomy_show()

        url = detail_url(sample.id)
        res = self.client.get(url)

        serializer = AstronomyShowDetailSerializer(sample)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_astronomy_show_create_forbidden(self):
        payload = {
            "title": "astronomy_show",
            "description": "some_description",
        }

        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AstronomyShowPosterUploadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@admin.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.astronomy_show = sample_astronomy_show(
            show_theme_name="First", title="Title_for_test"
        )
        self.show_session = sample_show_session(
            astronomy_show=self.astronomy_show
        )

    def tearDown(self):
        self.astronomy_show.poster.delete()

    def test_upload_poster_to_astronomy_show(self):
        """Test uploading poster to astronomy_show"""
        url = poster_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg")as ntf:

            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            res = self.client.post(url, {"poster": ntf}, format="multipart")

            self.astronomy_show.refresh_from_db()

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("poster", res.data)
            self.assertTrue(os.path.exists(self.astronomy_show.poster.path))

    def test_upload_poster_bad_request(self):
        """Test uploading an invalid image"""
        url = poster_upload_url(self.astronomy_show.id)
        res = self.client.post(
            url,
            {"poster": "not a poster"},
            format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_poster_to_astronomy_show_list_should_not_work(self):
        url = ASTRONOMY_SHOW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "some_title_1",
                    "description": "some_description",
                    "poster": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(title="some_title_1")
        self.assertFalse(astronomy_show.poster)

    def test_poster_url_is_shown_on_astronomy_show_detail(self):
        url = poster_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "poster": ntf,
                },
                format="multipart",
            )
            self.assertIn("poster", res.data)

    def test_poster_url_is_shown_on_astronomy_show_list(self):
        url = poster_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(
                url,
                {
                    "poster": ntf,
                },
                format="multipart",
            )
            res = self.client.get(ASTRONOMY_SHOW_URL)

            self.assertIn("poster", res.data[0].keys())
