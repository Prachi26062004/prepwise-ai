from django.conf import settings
from django.db import models

from resumes.models import Resume


class DefenseSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="defenses")
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class DefenseClaim(models.Model):
    session = models.ForeignKey(DefenseSession, on_delete=models.CASCADE, related_name="claims")
    claim = models.CharField(max_length=300)
    question = models.TextField()
    answer = models.TextField(blank=True)
    followup = models.TextField(blank=True)
    followup_answer = models.TextField(blank=True)
    verdict = models.CharField(max_length=12, blank=True)
    feedback = models.TextField(blank=True)
    paste_attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["id"]