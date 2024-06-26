from django.urls import path, include
from rest_framework import routers

from planetarium.views import (
    ReservationViewSet,
    ShowSpeakerViewSet,
    ShowSessionViewSet,
    PlanetariumDomeViewSet,
    ShowThemeViewSet,
    AstronomyShowViewSet
)

app_name = "planetarium"

router = routers.DefaultRouter()

router.register("reservations", ReservationViewSet)
router.register("show_speakers", ShowSpeakerViewSet)
router.register("show_sessions", ShowSessionViewSet)
router.register("show_themes", ShowThemeViewSet)
router.register("planetarium_domes", PlanetariumDomeViewSet)
router.register("astronomy_shows", AstronomyShowViewSet)

urlpatterns = [path("", include(router.urls))]
