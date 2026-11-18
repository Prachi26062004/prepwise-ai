from django.shortcuts import get_object_or_404
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from job_matcher.matching import match
from resumes.models import Resume
from .models import Roadmap


def build_weeks(skills: list) -> list:
    return [{"week": i, "topic": s, "done": False,
             "tasks": [f"Study core concepts of {s}", f"Solve 5 practice exercises in {s}",
                       f"Build a small project using {s}"]} for i, s in enumerate(skills, 1)]


def out(r):
    return {"id": r.id, "role": r.role, "weeks": r.weeks, "progress": r.progress}


class RoadmapList(APIView):
    def get(self, request):
        return Response([out(r) for r in Roadmap.objects.filter(user=request.user)[:20]])

    def post(self, request):
        role = str(request.data.get("role", "Software Engineer"))[:80]
        gaps, job = [], request.data.get("job_description", "")
        if job and request.data.get("resume_id"):
            r = get_object_or_404(Resume, pk=request.data["resume_id"], user=request.user)
            gaps = match(r.text, job[:20000])["missing_skills"]
        extra = [s for s in request.data.get("skills", []) if isinstance(s, str)][:10]
        skills = list(dict.fromkeys(gaps + extra))[:12]
        if not skills:
            return Response({"error": "Provide a job description with a resume, or a skills list."}, status=400)
        return Response(out(Roadmap.objects.create(user=request.user, role=role, weeks=build_weeks(skills))), status=201)


class RoadmapDetail(APIView):
    def patch(self, request, pk):
        r = get_object_or_404(Roadmap, pk=pk, user=request.user)
        week, done = int(request.data.get("week", 0)), bool(request.data.get("done", True))
        for w in r.weeks:
            if w["week"] == week:
                w["done"] = done
        r.save(update_fields=["weeks"])
        return Response(out(r))

    def delete(self, request, pk):
        get_object_or_404(Roadmap, pk=pk, user=request.user).delete()
        return Response(status=204)


urlpatterns = [path("", RoadmapList.as_view()), path("<int:pk>/", RoadmapDetail.as_view())]