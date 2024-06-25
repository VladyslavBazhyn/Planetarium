from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext as _
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=30, null=True)
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()
