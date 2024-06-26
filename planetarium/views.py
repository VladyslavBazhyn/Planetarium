from rest_framework import viewsets, mixins, status
from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination

from planetarium.models import (
    PlanetariumDome,
    ShowTheme,
    ShowSession,
    ShowSpeaker,
    AstronomyShow,
    Ticket,
    Reservation
)
from planetarium.serializers import (
    PlanetariumDomeSerializer,
    ShowThemeSerializer,
    ShowSessionSerializer,
    ShowSpeakerSerializer,
    TicketSerializer,
    ReservationSerializer,
    AstronomyShowSerializer,
    AstronomyShowPosterSerializer
)


class PlanetariumDomeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowThemeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class ShowSessionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer


class ShowSpeakerViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShowSpeaker.objects.all()
    serializer_class = ShowSpeakerSerializer


class TicketSerializerViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 30


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer
