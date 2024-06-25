import os
import uuid

from django.db import models
from django.utils.text import slugify


def astronomy_show_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/astronomy_shows/", filename)


class Speaker(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    profession = models.CharField(max_length=30)
    # Need to delete astronomy show field from diagram!!!


class ShowTheme(models.Model):
    name = models.CharField(max_length=30)


class AstronomyShow(models.Model):
    title = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    poster = models.ImageField(
        null=True,
        upload_to=astronomy_show_image_file_path
    )
    speaker = models.ManyToManyField(
        Speaker,
        related_name="speaker"
    )
    show_theme = models.ForeignKey(
        ShowTheme,
        related_name="theme",
        on_delete=models.CASCADE
    )
