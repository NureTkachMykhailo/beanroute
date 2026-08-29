from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["name"])]

    def __str__(self):
        return self.name


ROAST_CHOICES = [
    ("light", "Світла обсмажка"),
    ("medium", "Середня обсмажка"),
    ("dark", "Темна обсмажка"),
]

PROCESS_CHOICES = [
    ("washed", "Мита"),
    ("natural", "Натуральна"),
    ("honey", "Хані"),
]


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=210, unique=True, allow_unicode=True)
    origin_country = models.CharField(max_length=80)
    producer = models.CharField(max_length=120, blank=True)
    process = models.CharField(max_length=10, choices=PROCESS_CHOICES, default="washed")
    roast_level = models.CharField(max_length=10, choices=ROAST_CHOICES, default="medium")
    altitude_m = models.PositiveIntegerField(default=0)
    lot_reference = models.CharField(max_length=40, blank=True)
    weight_g = models.PositiveIntegerField(default=250)
    cupping_notes = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["price"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_featured", "is_active"]),
        ]
        constraints = [
            CheckConstraint(condition=Q(price__gte=0), name="product_price_non_negative"),
            CheckConstraint(condition=Q(stock__gte=0), name="product_stock_non_negative"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])

    @property
    def rating_avg(self):
        agg = self.reviews.aggregate(models.Avg("rating"))
        return round(agg["rating__avg"] or 0, 1)


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [UniqueConstraint(fields=["user", "product"], name="unique_wishlist_entry")]


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Очікує"),
        ("paid", "Оплачено"),
        ("shipped", "Відправлено"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"]), models.Index(fields=["created_at"])]

    def __str__(self):
        return f"Замовлення №{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [models.Index(fields=["product", "order"])]

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["product", "created_at"]), models.Index(fields=["rating"])]
        constraints = [UniqueConstraint(fields=["user", "product"], name="unique_review_per_purchase")]


class SiteSettings(models.Model):
    hero_title = models.CharField(max_length=200, default="BeanRoute")
    hero_subtitle = models.CharField(
        max_length=300, default="Мікро-обсмажувальня спешелті кави, зібрана по зернах"
    )
    hero_cta = models.CharField(max_length=80, default="Обрати зерно")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Site settings"


class RoasteryService(models.Model):
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    author_name = models.CharField(max_length=100)
    quote = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.author_name


class FAQItem(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question
