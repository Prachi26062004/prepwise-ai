from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from job_matcher.matching import match
from resumes.models import Resume
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "company", "role", "link", "description", "status", "notes",
                  "match_score", "missing_skills", "created_at"]
        read_only_fields = ["match_score", "missing_skills", "created_at"]


def apply_match(app: Application) -> None:
    """Score the job description against the user's latest resume (if both exist)."""
    resume = Resume.objects.filter(user=app.user).first()
    if resume and len(app.description.strip()) >= 20:
        m = match(resume.text, app.description[:20000])
        app.match_score, app.missing_skills = m["score"], m["missing_skills"]
    else:
        app.match_score, app.missing_skills = None, []
    app.save(update_fields=["match_score", "missing_skills"])


class ApplicationList(APIView):
    def get(self, request):
        return Response(ApplicationSerializer(Application.objects.filter(user=request.user), many=True).data)

    def post(self, request):
        s = ApplicationSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        app = s.save(user=request.user)
        apply_match(app)
        return Response(ApplicationSerializer(app).data, status=201)


class ApplicationDetail(APIView):
    def patch(self, request, pk):
        app = get_object_or_404(Application, pk=pk, user=request.user)
        old_description = app.description
        s = ApplicationSerializer(app, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        app = s.save()
        if app.description != old_description:
            apply_match(app)
        return Response(ApplicationSerializer(app).data)

    def delete(self, request, pk):
        get_object_or_404(Application, pk=pk, user=request.user).delete()
        return Response(status=204)