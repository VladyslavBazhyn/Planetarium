"""Register your models here"""

from django.contrib import admin
from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    ShowSpeaker,
    Ticket,
    Reservation,
    ShowSession,
    PlanetariumDome
)

admin.site.register(ShowTheme)
admin.site.register(AstronomyShow)
admin.site.register(ShowSpeaker)
admin.site.register(Ticket)
admin.site.register(Reservation)
admin.site.register(ShowSession)
admin.site.register(PlanetariumDome)
