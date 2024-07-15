import os
import uuid

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from planetarium_service import settings


def astronomy_show_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/astronomy_shows/", filename)


class ShowSpeaker(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    profession = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ShowTheme(models.Model):
    name = models.CharField(max_length=30,
                            unique=True
                            )

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=30,
                             unique=True
                             )
    description = models.TextField()
    poster = models.ImageField(
        blank=True,
        null=True,
        upload_to=astronomy_show_image_file_path
    )
    show_themes = models.ManyToManyField(
        ShowTheme,
        related_name="show_themes"
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=30)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow,
        on_delete=models.CASCADE,
        related_name="show_sessions"
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE,
        related_name="planetarium_dome"
    )
    show_speakers = models.ManyToManyField(
        ShowSpeaker,
        related_name="speakers_show",
        blank=True
    )
    show_day = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()

    class Meta:
        ordering = [
            "-show_day",
            "-time_start",
            "-time_end"
        ]

    @staticmethod
    def validate_show_speakers(show_speakers, show_day, time_start, time_end):
        for speaker in show_speakers:
            other_speaker_shows = speaker.speakers_show.filter(
                show_day=show_day
            )
            for other_show in other_speaker_shows:
                if (
                        time_start <= other_show.time_start <= time_end or
                        time_start <= other_show.time_end <= time_end
                ):
                    raise ValidationError(
                        f"Speaker {speaker.first_name} {speaker.last_name} "
                        f"has another show scheduled on the same day and time."
                    )

    def clean(self):
        self.validate_show_speakers(
            self.show_speakers.all(), self.show_day, self.time_start, self.time_end
        )

    def save(self, *args, **kwargs):
        super(ShowSession, self).save(*args, **kwargs)
        self.clean()

    def __str__(self):
        return f"{self.astronomy_show.title} {str(self.show_day)} at {self.time_start}"


class Reservation(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
        null=True,
        blank=True
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, planetarium_dome, error_to_raise):
        for ticket_attr_value, ticket_attr_name, planetarium_dome_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(planetarium_dome, planetarium_dome_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {planetarium_dome_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.show_session.planetarium_dome,
            ValidationError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (
            f"{str(self.show_session)} (row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ("show_session", "row", "seat")
        ordering = ["row", "seat"]
