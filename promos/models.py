from django.db import models
from django.db.models import CheckConstraint, F, Q


class PromoCode(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Процент"
        FIXED = "fixed", "Фиксированная сумма"

    code = models.CharField("Код", max_length=50, unique=True)
    discount_type = models.CharField(
        "Тип скидки", max_length=10, choices=DiscountType.choices
    )
    value = models.DecimalField("Размер скидки", max_digits=8, decimal_places=2)
    valid_from = models.DateTimeField("Действует с")
    valid_to = models.DateTimeField("Действует по")
    usage_limit = models.PositiveIntegerField("Лимит использований")
    used_count = models.PositiveIntegerField("Использован раз", default=0)
    min_order_amount = models.DecimalField(
        "Минимальная сумма заказа", max_digits=10, decimal_places=2, default=0
    )
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "промокод"
        verbose_name_plural = "промокоды"
        ordering = ["-valid_from"]
        constraints = [
            CheckConstraint(condition=Q(value__gt=0), name="promo_value_positive"),
            CheckConstraint(
                condition=Q(discount_type="fixed") | Q(value__lte=100),
                name="promo_percent_max_100",
            ),
            CheckConstraint(
                condition=Q(used_count__lte=F("usage_limit")),
                name="promo_used_not_over_limit",
            ),
        ]

    def __str__(self):
        return self.code