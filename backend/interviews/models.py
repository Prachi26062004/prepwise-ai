from django.conf import settings
from django.db import models


class InterviewSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions")
    role = models.CharField(max_length=80)
    category = models.CharField(max_length=20, default="technical")
    level = models.CharField(max_length=20, default="Intermediate")
    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]


class InterviewAnswer(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="answers")
    question = models.TextField()
    answer = models.TextField()
    score = models.FloatField()
    feedback = models.TextField(blank=True)
    missing = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)