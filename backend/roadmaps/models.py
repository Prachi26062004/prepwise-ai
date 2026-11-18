from django.conf import settings
from django.db import models


class Roadmap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roadmaps")
    role = models.CharField(max_length=80)
    weeks = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def progress(self) -> int:
        return round(100 * sum(w["done"] for w in self.weeks) / len(self.weeks)) if self.weeks else 0