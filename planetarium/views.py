from datetime import datetime

from django.db.models import F, Count, Value, CharField, ExpressionWrapper, IntegerField, Prefetch
from django.db.models.functions import Concat
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from planetarium.models import (
    PlanetariumDome,
    ShowTheme,
    ShowSession,
    ShowSpeaker,
    AstronomyShow,
    Ticket,
    Reservation
)
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly
from planetarium.serializers import (
    PlanetariumDomeSerializer,
    ShowThemeSerializer,
    ShowSessionSerializer,
    ShowSpeakerSerializer,
    TicketSerializer,
    ReservationSerializer,
    AstronomyShowPosterSerializer, ReservationListSerializer, ReservationDetailSerializer, ShowSpeakerListSerializer,
    ShowSpeakerDetailSerializer, ShowThemeListSerializer, ShowThemeDetailSerializer, ShowSessionListSerializer,
    ShowSessionDetailSerializer, AstronomyShowListSerializer, AstronomyShowDetailSerializer
)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

    def get_queryset(self):
        queryset = self.queryset

        capacity = self.request.query_params.get("capacity", None)

        if capacity is not None:
            try:
                queryset = queryset.annotate(
                    total_capacity=ExpressionWrapper(
                        F("rows") * F("seats_in_row"),
                        output_field=IntegerField()
                    )
                ).filter(total_capacity__gte=capacity)
            except ValueError:
                pass  # If capacity not a valid value - do nothing

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="capacity",
                type=OpenApiTypes.INT,
                description="Searching by planetarium dome capacity (ex. ?capacity=int)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                description="Find show theme by name (ex. ?name=name)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ShowSessionPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 10


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = (
        ShowSession.objects.all()
        .select_related(
            "astronomy_show",
            "planetarium_dome"
        )
        .prefetch_related(
            "show_speakers"
        )
        .annotate(
            tickets_available=(
                    F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
                    - Count("tickets")
            )
        )
    )
    serializer_class = ShowSessionSerializer
    pagination_class = ShowSessionPagination

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = ShowSessionListSerializer
        if self.action == "retrieve":
            serializer_class = ShowSessionDetailSerializer

        return serializer_class

    def get_queryset(self):
        queryset = self.queryset

        date = self.request.query_params.get("date")
        show_title = self.request.query_params.get("show_title")

        if date:
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
                queryset = queryset.filter(show_day=date)
            except ValueError:
                raise ValueError("Incorrect date format, should be YYYY-MM-DD")

        if show_title:
            queryset = queryset.filter(astronomy_show__title__icontains=show_title)

        return queryset.order_by("-show_day", "-time_start", "-time_end")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "show_title",
                type=OpenApiTypes.STR,
                description="Filter by astronomy_show_title (ex. ?show_title=title)",
            ),
            OpenApiParameter(
                "date",
                type=OpenApiTypes.DATE,
                description=(
                        "Filter by date of ShowSession "
                        "(ex. ?date=2022-10-23)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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

    def get_queryset(self):
        queryset = self.queryset

        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        profession = self.request.query_params.get("profession")

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        if profession:
            queryset = queryset.filter(profession__icontains=profession)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="first_name",
                type=OpenApiTypes.STR,
                description="Filter by show speaker first_name (ex. ?first_name=name)"
            ),
            OpenApiParameter(
                name="last_name",
                type=OpenApiTypes.STR,
                description="Filter by show speaker last_name (ex. ?last_name=name)"
            ),
            OpenApiParameter(
                name="profession",
                type=OpenApiTypes.STR,
                description="Filter by show speaker profession (ex. ?profession=profession)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TicketSerializerViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().select_related()
    serializer_class = TicketSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 30


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "show_title",
                type=OpenApiTypes.INT,
                description="Filter by astronomy_show_title (ex. ?show_title=title)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = ReservationListSerializer
        if self.action == "retrieve":
            serializer_class = ReservationDetailSerializer
        return serializer_class

    def get_queryset(self):
        queryset = (
            self.queryset.select_related("user")
            .prefetch_related(
                Prefetch(
                    "tickets",
                    queryset=Ticket.objects.select_related(
                        "show_session",
                        "show_session__astronomy_show",
                        "show_session__planetarium_dome"
                    )
                )
            )
        )

        show_title = self.request.query_params.get("show_title")

        if show_title:
            queryset = queryset.filter(tickets__show_session__astronomy_show__title__icontains=show_title)

        return queryset


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = (AstronomyShow.objects.prefetch_related(
        "show_themes"
    ))
    serializer_class = AstronomyShowListSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = AstronomyShowListSerializer
        elif self.action == "retrieve":
            serializer_class = AstronomyShowDetailSerializer
        elif self.action == "upload_poster":
            return AstronomyShowPosterSerializer
        return serializer_class

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title")

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    @action(
        methods=["post"],
        detail=True,
        url_path="upload-poster",
    )
    def upload_poster(self, request, pk=None):

        astronomy_show = self.get_object()
        serializer = self.get_serializer(astronomy_show, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type=OpenApiTypes.STR,
                description="Filter by astronomy show titles (ex. ?title=some title here)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
