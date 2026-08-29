from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [("buyer", "Покупець"), ("staff", "Персонал")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="buyer")
    city = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class RequestLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="request_logs"
    )
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.PositiveIntegerField()
    duration_ms = models.PositiveIntegerField()
    remote_addr = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["status_code", "created_at"]),
        ]


class AuditEvent(models.Model):
    EVENT_CHOICES = [
        ("login", "Вхід"),
        ("register", "Реєстрація"),
        ("order", "Замовлення"),
        ("review", "Відгук"),
        ("wishlist", "Обране"),
        ("profile", "Зміна профілю"),
        ("logout", "Вихід"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="audit_events"
    )
    event_type = models.CharField(max_length=12, choices=EVENT_CHOICES)
    meta = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"]), models.Index(fields=["event_type"])]
