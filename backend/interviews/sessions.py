from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_engine.services import evaluate_answer, generate_interview_questions
from ai_engine.star import star_check
from ai_engine.usage import record_usage
from resumes.models import Resume
from .models import InterviewAnswer, InterviewSession


def _summary(s):
    avg = s.answers.aggregate(a=Avg("score"))["a"]
    return {
        "id": s.id,
        "role": s.role,
        "category": s.category,
        "level": s.level,
        "questions": s.questions,
        "answered": s.answers.count(),
        "avg_score": round(avg, 1) if avg is not None else None,
        "finished": s.finished_at is not None,
        "created_at": s.created_at,
    }


class SessionList(APIView):
    def get(self, request):
        sessions = InterviewSession.objects.filter(user=request.user)[:50]
        return Response([_summary(s) for s in sessions])

    def post(self, request):
        d = request.data
        skills = []
        if d.get("resume_id"):
            resume = get_object_or_404(Resume, pk=d["resume_id"], user=request.user)
            skills = resume.analysis.get("technical_skills", [])
        role = str(d.get("role", "Software Engineer"))[:80]
        category = d.get("category", "technical")
        level = d.get("level", "Intermediate")
        questions = generate_interview_questions(role, skills, category, level)
        record_usage(request.user, "questions")
        s = InterviewSession.objects.create(
            user=request.user, role=role, category=category, level=level, questions=questions
        )
        return Response(_summary(s), status=201)


class SessionDetail(APIView):
    def get(self, request, pk):
        s = get_object_or_404(InterviewSession, pk=pk, user=request.user)
        answers = list(s.answers.values("question", "answer", "score", "feedback", "missing"))
        return Response({**_summary(s), "answers": answers})

    def delete(self, request, pk):
        get_object_or_404(InterviewSession, pk=pk, user=request.user).delete()
        return Response(status=204)


class SessionAnswer(APIView):
    def post(self, request, pk):
        s = get_object_or_404(InterviewSession, pk=pk, user=request.user, finished_at=None)
        question = request.data.get("question", "")
        answer = str(request.data.get("answer", "")).strip()
        if question not in s.questions or not answer:
            return Response({"error": "Valid question and non-empty answer required"}, status=400)
        ev = evaluate_answer(question, answer)
        record_usage(request.user, "evaluate")
        InterviewAnswer.objects.create(
            session=s,
            question=question,
            answer=answer[:5000],
            score=ev["score"],
            feedback=ev["feedback"],
            missing=ev["missing"],
        )
        if s.category == "behavioral":
            ev["star"] = star_check(answer)
        return Response(ev)


class SessionFinish(APIView):
    def post(self, request, pk):
        s = get_object_or_404(InterviewSession, pk=pk, user=request.user)
        s.finished_at = s.finished_at or timezone.now()
        s.save(update_fields=["finished_at"])
        return Response(_summary(s))