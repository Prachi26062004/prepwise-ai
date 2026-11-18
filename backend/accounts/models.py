from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    target_role = models.CharField(max_length=80, blank=True)
    experience_level = models.CharField(max_length=20, default="Beginner")
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)