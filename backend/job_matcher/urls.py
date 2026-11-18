from django.shortcuts import get_object_or_404
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from resumes.models import Resume
from .matching import match


class MatchView(APIView):
    def post(self, request):
        job = (request.data.get("job_description") or "").strip()
        if len(job) < 20:
            return Response({"error": "Provide a job description."}, status=400)
        r = get_object_or_404(Resume, pk=request.data.get("resume_id"), user=request.user)
        return Response(match(r.text, job[:20000]))


urlpatterns = [path("", MatchView.as_view())]