from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь книжного магазина."""

    birth_date = models.DateField("Дата рождения", null=True, blank=True)

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"