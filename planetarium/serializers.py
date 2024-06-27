from rest_framework import serializers

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    ShowSpeaker,
    Ticket,
    Reservation,
    ShowSession,
    PlanetariumDome
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = (
            "id", "name"
        )


class ShowSpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSpeaker
        fields = (
            "id", "first_name", "last_name", "profession"
        )


class AstronomyShowSerializer(serializers.ModelSerializer):
    show_theme = ShowThemeSerializer(many=True, read_only=True)

    class Meta:
        model = AstronomyShow
        fields = (
            "id",
            "title",
            "description",
            "poster",
            "show_theme",
            "poster"
        )


class AstronomyShowPosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = (
            "id", "poster"
        )


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = (
            "id", "name", "rows", "seats_in_row"
        )


class ShowSessionSerializer(serializers.ModelSerializer):
    astronomy_show = AstronomyShowSerializer(many=False, read_only=False)
    planetarium_dome = PlanetariumDomeSerializer(many=False, read_only=False)
    show_speakers = ShowSpeakerSerializer(many=True, read_only=False)

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_speakers",
            "show_day",
            "time_start",
            "time_end"
        )


class TicketSerializer(serializers.ModelSerializer):
    show_session = ShowSessionSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id", "row", "seat", "show_session"
        )


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")
