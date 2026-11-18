from django.shortcuts import get_object_or_404
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_engine.services import evaluate_answer, generate_interview_questions
from resumes.models import Resume
from .sessions import SessionAnswer, SessionDetail, SessionFinish, SessionList


class QuestionsView(APIView):
    def post(self, request):
        d, skills = request.data, []
        if d.get("resume_id"):
            skills = get_object_or_404(Resume, pk=d["resume_id"], user=request.user).analysis.get("technical_skills", [])
        qs = generate_interview_questions(str(d.get("role", "Software Engineer"))[:80], skills,
                                          d.get("category", "technical"), d.get("level", "Intermediate"))
        return Response({"questions": qs})


class EvaluateView(APIView):
    def post(self, request):
        q, a = str(request.data.get("question", "")), str(request.data.get("answer", "")).strip()
        if not q or not a:
            return Response({"error": "question and answer are required"}, status=400)
        return Response(evaluate_answer(q, a))


urlpatterns = [
    path("questions/", QuestionsView.as_view()),
    path("evaluate/", EvaluateView.as_view()),
    path("sessions/", SessionList.as_view()),
    path("sessions/<int:pk>/", SessionDetail.as_view()),
    path("sessions/<int:pk>/answer/", SessionAnswer.as_view()),
    path("sessions/<int:pk>/finish/", SessionFinish.as_view()),
]