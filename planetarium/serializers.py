from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ShowSpeaker
        fields = (
            "id", "first_name", "last_name", "profession", "full_name")
        read_only_fields = ("full_name", "id")

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class ShowSpeakerListSerializer(ShowSpeakerSerializer):
    class Meta:
        model = ShowSpeaker
        fields = (
            "id", "full_name", "profession"
        )


class AstronomyShowSerializer(serializers.ModelSerializer):
    show_themes = ShowThemeSerializer(many=True)

    class Meta:
        model = AstronomyShow
        fields = (
            "id",
            "title",
            "description",
            "poster",
            "show_themes",
        )


class AstronomyShowListSerializer(AstronomyShowSerializer):
    show_themes = serializers.SlugRelatedField(
        many=True,
        queryset=ShowTheme.objects.all(),
        slug_field="name"
    )

    def create(self, validated_data):
        show_themes = validated_data.pop("show_themes")
        astronomy_show = AstronomyShow.objects.create(**validated_data)
        astronomy_show.show_themes.set(show_themes)
        return astronomy_show


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
    astronomy_show = AstronomyShowSerializer(many=False)
    planetarium_dome = PlanetariumDomeSerializer(many=False)
    show_speakers = ShowSpeakerSerializer(many=True)

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


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.SlugRelatedField(
        many=False,
        slug_field="title",
        queryset=AstronomyShow.objects.all(),
    )
    planetarium_dome = serializers.SlugRelatedField(
        many=False,
        slug_field="name",
        queryset=PlanetariumDome.objects.all(),
    )
    show_speakers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ShowSpeaker.objects.all(),
    )

    def validate(self, data):
        show_speakers = data.get("show_speakers", [])
        show_day = data.get("show_day")
        time_start = data.get("time_start")
        time_end = data.get("time_end")

        ShowSession.validate_show_speakers(
            show_speakers, show_day, time_start, time_end
        )

        return data

    def create(self, validated_data):
        show_speakers = validated_data.pop("show_speakers", None)
        show_session = ShowSession.objects.create(**validated_data)
        if show_speakers:
            show_session.show_speakers.set(show_speakers)
        return show_session

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["show_speakers"] = ShowSpeakerSerializer(instance.show_speakers, many=True).data
        return representation


class TicketSerializer(serializers.ModelSerializer):
    show_session = ShowSessionSerializer(many=False, read_only=True)
    row = serializers.IntegerField()
    seat = serializers.IntegerField()

    class Meta:
        model = Ticket
        fields = (
            "id",  "show_session", "row", "seat"
        )


class TicketListSerializer(TicketSerializer):
    show_session = serializers.SlugRelatedField(
        many=False,
        queryset=ShowSession.objects.all(),
        slug_field="id"
    )
    show_session_astronomy_show_title = serializers.SlugRelatedField(
        slug_field=ShowSession.astronomy_show.title,
        read_only=True
    )  # Is it a correct way to take appropriate to this ticket show session?

    class Meta:
        model = Ticket
        fields = (
            "id",
            "show_session_astronomy_show_title",
            "show_session",
            "row",
            "seat"
        )

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["show_session"].planetarium_dome,
            ValidationError
        )
        return data


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")


class ReservationDetailSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True)
    # astronomy_show_title =
    # show session date / show session time start / show session speaker
    # for all tickets: ticket row / ticket seat

    class Meta:
        model = Reservation
        fields = (
            "id",
            # "astronomy_show_title",
            # "show session date",
            # "show session time start",
            # "show session speaker",
            "created_at",
            "tickets",
        )


class ReservationListSerializer(ReservationSerializer):
    # astronomy show title /
    # count_of_all_tickets

    class Meta:
        model = Reservation
        fields = (
            "id",
            # "astronomy show title",
            # "count_of_all_tickets"
        )

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation
