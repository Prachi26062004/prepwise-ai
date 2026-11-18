from django.conf import settings
from django.db import models


class Application(models.Model):
    STATUSES = [("saved", "Saved"), ("applied", "Applied"), ("interview", "Interview"),
                ("offer", "Offer"), ("rejected", "Rejected")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    company = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    link = models.URLField(blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUSES, default="saved")
    notes = models.TextField(blank=True)
    match_score = models.PositiveSmallIntegerField(null=True, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"])]