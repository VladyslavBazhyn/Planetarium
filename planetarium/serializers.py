"""
All serializers which used in this project.
Serializers usually separate on three pert:
    - Base serializer (Used as a basis for handling with serializers, adding new general fields etc.)
    - List serializer (Used for handling all information which shown on list endpoints)
    - Detail serializer (Used for handling all information which shown on detail endpoints)
"""


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


class ShowThemeListSerializer(ShowThemeSerializer):
    class Meta:
        model = ShowTheme
        fields = ("name", )


class ShowThemeDetailSerializer(ShowThemeSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name", )


class ShowSpeakerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ShowSpeaker
        fields = (
            "id", "first_name", "last_name", "profession", "full_name"
        )
        read_only_fields = ("full_name", "id")

    def get_full_name(self, obj):
        """Function for taking speaker's full name"""
        return f"{obj.first_name} {obj.last_name}"


class ShowSpeakerListSerializer(ShowSpeakerSerializer):
    class Meta:
        model = ShowSpeaker
        fields = (
            "full_name", "profession"
        )


class ShowSpeakerDetailSerializer(ShowSpeakerSerializer):
    class Meta:
        model = ShowSpeaker
        fields = (
            "id",
            "first_name",
            "last_name",
            "profession"
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

    class Meta:
        model = AstronomyShow
        fields = (
            "title",
            "show_themes",
            "poster",
        )

    def create(self, validated_data):
        """
        Changed save method to correctly adding show themes and poster
        to astronomy show because of theirs relation type
        """
        show_themes = validated_data.pop("show_themes")
        validated_data.pop("poster")
        astronomy_show = AstronomyShow.objects.create(**validated_data)
        astronomy_show.show_themes.set(show_themes)
        return astronomy_show


class AstronomyShowDetailSerializer(AstronomyShowSerializer):
    class Meta:
        model = AstronomyShow
        fields = (
            "id",
            "title",
            "description",
            "poster",
            "show_themes",
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
    astronomy_show = serializers.SlugRelatedField(
        slug_field="title",
        queryset=AstronomyShow.objects.all(),
        many=False
    )
    planetarium_dome = serializers.SlugRelatedField(
        slug_field="name",
        queryset=PlanetariumDome.objects.all(),
        many=False
    )
    show_speakers = serializers.PrimaryKeyRelatedField(
        queryset=ShowSpeaker.objects.all(),
        many=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        """
        This function change usual representation of
        show_speakers field for better readability
        """
        representation = super().to_representation(instance)
        representation["show_speakers"] = ShowSpeakerSerializer(
            instance.show_speakers,
            many=True
        ).data
        return representation

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_speakers",
            "show_day",
            "time_start",
            "time_end",
            "tickets_available"
        )

    def create(self, validated_data):
        """
        Changed save method to correctly adding show speakers
        to show session because of theirs relation type
        """
        show_speakers = validated_data.pop("show_speakers", None)
        show_session = ShowSession.objects.create(**validated_data)
        if show_speakers:
            show_session.show_speakers.set(show_speakers)
        return show_session

    def validate(self, data):
        """Function to call method for validating show speakers working time"""
        show_speakers = data.get("show_speakers", [])
        show_day = data.get("show_day")
        time_start = data.get("time_start")
        time_end = data.get("time_end")

        ShowSession.validate_show_speakers(
            show_speakers, show_day, time_start, time_end
        )

        return data


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

    class Meta:
        model = ShowSession
        fields = (
            "astronomy_show",
            "planetarium_dome",
            "show_day",
            "time_start",
            "time_end",
            "show_speakers",
            "tickets_available"
        )

    def to_representation(self, instance):
        """
        This function change usual representation of
        show_speakers field for better readability
        """
        representation = super().to_representation(instance)
        representation["show_speakers"] = ShowSpeakerListSerializer(
            instance.show_speakers,
            many=True
        ).data
        return representation


class ShowSessionDetailSerializer(ShowSessionSerializer):
    """This serializers now don't have any differences from base serializer"""
    pass


class TicketSerializer(serializers.ModelSerializer):
    show_session = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=ShowSession.objects.all()
    )
    row = serializers.IntegerField()
    seat = serializers.IntegerField()

    class Meta:
        model = Ticket
        fields = (
            "id",  "show_session", "row", "seat"
        )


class TicketListSerializer(TicketSerializer):
    show_session_day = serializers.SlugRelatedField(
        many=False,
        queryset=ShowSession.objects.all(),
        slug_field="show_day"
    )
    show_session_time_start = serializers.SlugRelatedField(
        many=False,
        queryset=ShowSession.objects.all(),
        slug_field="time_start"
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "show_session_day",
            "show_session_time_start",
            "row",
            "seat"
        )

    def validate(self, attrs):
        """Function to call method for validating ticket's set and row"""
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["show_session"].planetarium_dome,
            ValidationError
        )
        return data


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False)
    astronomy_show_title = serializers.SerializerMethodField()
    taken_places = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = (
            "id",
            "created_at",
            "tickets",
            "astronomy_show_title",
            "taken_places"
        )

    def create(self, validated_data):
        """
        Changed save method to correctly adding tickets
        to reservation because of theirs relation type
        """
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation

    def get_astronomy_show_title(self, obj):
        """Function to take specific astronomy show title by models relations"""
        try:
            show_session = obj.tickets.show_session
        except AttributeError:
            show_session = None
        if show_session and show_session.astronomy_show:
            return show_session.astronomy_show.title
        return None

    def get_taken_places(self, obj):
        """Function to take all taken places for specific astronomy show"""
        taken_places = obj.tickets.all()
        return TicketSeatsSerializer(taken_places, many=True).data


class ReservationDetailSerializer(ReservationSerializer):
    show_session_date = serializers.SerializerMethodField()
    show_session_time_start = serializers.SerializerMethodField()
    show_session_speakers = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = (
            "id",
            "astronomy_show_title",
            "show_session_date",
            "show_session_time_start",
            "taken_places",
            "show_session_speakers",
            "created_at"
        )

    def get_show_session_date(self, obj):
        """Function to take show session date for specific show by models relations"""
        show_session = obj.tickets.first().show_session
        if show_session:
            return show_session.show_day
        return None

    def get_show_session_time_start(self, obj):
        """Function to take show session time start for specific show by models relations"""
        show_session = obj.tickets.first().show_session
        if show_session:
            return show_session.time_start
        return None

    def get_show_session_speakers(self, obj):
        """Function to take show session speakers for specific show by models relations"""
        show_session = obj.tickets.first().show_session
        if show_session:
            speakers = show_session.show_speakers.all()
            return ShowSpeakerListSerializer(speakers, many=True).data
        return []


class ReservationListSerializer(ReservationSerializer):

    class Meta:
        model = Reservation
        fields = (
            "id",
            "astronomy_show_title",
            "taken_places"
        )
