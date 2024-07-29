"""
This file collect all basic sample functions needed for tests
"""

from datetime import datetime

from planetarium.models import (
    ShowSession,
    AstronomyShow,
    ShowTheme,
    ShowSpeaker,
    PlanetariumDome, Reservation
)


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


# Function to create sample show theme
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

    ShowSession.validate_show_speakers(
        [show_speaker],
        datetime.strptime(show_session.show_day, "%Y-%m-%d").date(),
        datetime.strptime(show_session.time_start, "%H:%M:%S").time(),
        datetime.strptime(show_session.time_end, "%H:%M:%S").time()
    )

    show_session.show_speakers.add(show_speaker)

    return show_session


# Function to create sample reservation
def sample_reservation(**params):

    def_param = {
        "user": None,
    }

    def_param.update(params)

    return Reservation.objects.create(**def_param)
