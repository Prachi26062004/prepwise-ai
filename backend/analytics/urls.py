from django.db.models import Avg
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from interviews.models import InterviewAnswer, InterviewSession
from resumes.models import Resume
from roadmaps.models import Roadmap


class DashboardView(APIView):
    def get(self, request):
        u = request.user
        resumes = Resume.objects.filter(user=u)
        latest = resumes.first()
        answers = InterviewAnswer.objects.filter(session__user=u)
        sessions = InterviewSession.objects.filter(user=u)
        skills = latest.analysis.get("technical_skills", []) if latest else []
        by_cat = {c["session__category"]: round(c["a"], 1) for c in
                  answers.values("session__category").annotate(a=Avg("score"))}
        return Response({
            "resume_count": resumes.count(),
            "latest_resume_score": latest.analysis.get("score") if latest else None,
            "interview_count": sessions.count(),
            "avg_interview_score": round(answers.aggregate(a=Avg("score"))["a"] or 0, 1),
            "strongest_skills": skills[:5], "category_scores": by_cat,
            "weakest_category": min(by_cat, key=by_cat.get) if by_cat else None,
            "score_history": [{"date": s.created_at.date(), "avg": round(s.answers.aggregate(a=Avg("score"))["a"] or 0, 1)}
                              for s in sessions[:10]][::-1],
            "roadmap_progress": [{"id": r.id, "role": r.role, "progress": r.progress}
                                 for r in Roadmap.objects.filter(user=u)[:5]],
        })


urlpatterns = [path("", DashboardView.as_view())]