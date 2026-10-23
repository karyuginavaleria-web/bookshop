from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, Q
from django.urls import reverse

from catalog.models import Book


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтверждён"
        SHIPPED = "shipped", "Передан в доставку"
        DONE = "done", "Выполнен"
        CANCELLED = "cancelled", "Отменён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Покупатель",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
    )
    full_name = models.CharField("Получатель", max_length=150)
    phone = models.CharField("Телефон", max_length=30)
    address = models.CharField("Адрес доставки", max_length=300)
    comment = models.TextField("Комментарий", blank=True)
    promo = models.ForeignKey(
        "promos.PromoCode",
        verbose_name="Промокод",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    promo_code = models.CharField("Код промокода", max_length=50, blank=True)
    discount_amount = models.DecimalField(
        "Сумма скидки", max_digits=10, decimal_places=2, default=0
    )
    created_at = models.DateTimeField("Оформлен", auto_now_add=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.pk}"

    def get_absolute_url(self):
        return reverse("orders:detail", args=[self.pk])

    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())

    @property
    def total_price(self):
        return self.subtotal - self.discount_amount

    @property
    def can_be_cancelled(self):
        return self.status == self.Status.NEW


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, verbose_name="Заказ", on_delete=models.CASCADE, related_name="items"
    )
    book = models.ForeignKey(
        Book, verbose_name="Книга", on_delete=models.PROTECT, related_name="order_items"
    )
    price = models.DecimalField("Цена на момент заказа", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Количество")

    class Meta:
        verbose_name = "позиция заказа"
        verbose_name_plural = "позиции заказа"
        constraints = [
            CheckConstraint(condition=Q(quantity__gte=1), name="order_item_quantity_min_1"),
        ]

    def __str__(self):
        return f"{self.book} × {self.quantity}"

    @property
    def total(self):
        return self.price * self.quantity