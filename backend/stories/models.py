from django.conf import settings
from django.db import models


class Story(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stories")
    title = models.CharField(max_length=120)
    tags = models.JSONField(default=list, blank=True)
    situation = models.TextField(blank=True)
    task = models.TextField(blank=True)
    action = models.TextField(blank=True)
    result = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]