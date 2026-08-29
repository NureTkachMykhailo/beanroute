from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AuditEvent, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    AuditEvent.objects.create(user=user, event_type="login", meta=f"IP {request.META.get('REMOTE_ADDR', '')}")


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user is not None:
        AuditEvent.objects.create(user=user, event_type="logout")
