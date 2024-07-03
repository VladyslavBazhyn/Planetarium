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
    AstronomyShowPosterSerializer, ReservationListSerializer, ReservationDetailSerializer, ShowSpeakerListSerializer,
    ShowSpeakerDetailSerializer, ShowThemeListSerializer, ShowThemeDetailSerializer, ShowSessionListSerializer,
    ShowSessionDetailSerializer, AstronomyShowListSerializer, AstronomyShowDetailSerializer
)


# [
#     showspeakerlistserializer,
# AstronomyShowListSerializer,
# AstronomyShowSerializer(usual with slugfields instead of full serializer)
# ]

class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = ShowThemeListSerializer
        if self.action == "retrieve":
            serializer_class = ShowThemeDetailSerializer

        return serializer_class


class ShowSessionPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 30


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all().select_related()
    serializer_class = ShowSessionSerializer
    pagination_class = ShowSessionPagination

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = ShowSessionListSerializer
        if self.action == "retrieve":
            serializer_class = ShowSessionDetailSerializer

        return serializer_class


class ShowSpeakerViewSet(viewsets.ModelViewSet):
    queryset = ShowSpeaker.objects.all()
    serializer_class = ShowSpeakerSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = ShowSpeakerListSerializer
        if self.action == "retrieve":
            serializer_class = ShowSpeakerDetailSerializer

        return serializer_class


class TicketSerializerViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().select_related()
    serializer_class = TicketSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 30


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all().select_related()
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = ReservationListSerializer
        if self.action == "retrieve":
            serializer_class = ReservationDetailSerializer
        return serializer_class


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowListSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = AstronomyShowListSerializer
        if self.action == "retrieve":
            serializer_class = AstronomyShowDetailSerializer
        return serializer_class
