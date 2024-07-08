import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome, ShowTheme, AstronomyShow, ShowSession

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def sample_astronomy_show(**parameters):
    show_theme = ShowTheme.objects.create(
        name="Show theme test 1"
    )

    default_data = {
        "title": "Title test",
        "description": "Some description",
    }

    default_data.update(parameters)

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
