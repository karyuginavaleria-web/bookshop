from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.urls import reverse


class Genre(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        verbose_name = "жанр"
        verbose_name_plural = "жанры"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField("Имя автора", max_length=150, unique=True)

    class Meta:
        verbose_name = "автор"
        verbose_name_plural = "авторы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField("Название", max_length=150, unique=True)

    class Meta:
        verbose_name = "издательство"
        verbose_name_plural = "издательства"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    class AgeRating(models.IntegerChoices):
        ZERO = 0, "0+"
        SIX = 6, "6+"
        TWELVE = 12, "12+"
        SIXTEEN = 16, "16+"
        EIGHTEEN = 18, "18+"

    title = models.CharField("Название", max_length=250)
    genre = models.ForeignKey(
        Genre, verbose_name="Жанр", on_delete=models.PROTECT, related_name="books"
    )
    authors = models.ManyToManyField(Author, verbose_name="Авторы", related_name="books")
    publisher = models.ForeignKey(
        Publisher, verbose_name="Издательство", on_delete=models.PROTECT, related_name="books"
    )
    year = models.PositiveSmallIntegerField("Год издания")
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField("Остаток на складе", default=0)
    age_rating = models.PositiveSmallIntegerField(
        "Возрастная маркировка", choices=AgeRating.choices, default=AgeRating.ZERO
    )
    cover = models.ImageField("Обложка", upload_to="books/", blank=True)
    is_active = models.BooleanField("Показывать в каталоге", default=True)
    created_at = models.DateTimeField("Добавлена", auto_now_add=True)

    class Meta:
        verbose_name = "книга"
        verbose_name_plural = "книги"
        ordering = ["title"]
        constraints = [
            CheckConstraint(condition=Q(price__gte=0), name="book_price_non_negative"),
            UniqueConstraint(
                fields=["title", "publisher", "year"], name="unique_book_edition"
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("catalog:detail", args=[self.pk])