from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_engine.usage import record_usage
from resumes.models import Resume
from .models import DefenseClaim, DefenseSession
from .service import judge, pick_claims


def claim_out(c):
    return {"id": c.id, "claim": c.claim, "question": c.question, "answer": c.answer, "followup": c.followup,
            "followup_answer": c.followup_answer, "verdict": c.verdict, "feedback": c.feedback,
            "paste_attempts": c.paste_attempts}


def session_out(s):
    return {"id": s.id, "resume": s.resume.filename, "claims": [claim_out(c) for c in s.claims.all()]}


class DefenseView(APIView):
    def get(self, request):
        s = DefenseSession.objects.filter(user=request.user).prefetch_related("claims").first()
        return Response(session_out(s) if s else None)

    def post(self, request):
        resume = get_object_or_404(Resume, pk=request.data.get("resume_id"), user=request.user)
        claims = pick_claims(resume)
        if not claims:
            return Response({"error": "No skills or bullets found on this resume to defend."}, status=400)
        s = DefenseSession.objects.create(user=request.user, resume=resume)
        DefenseClaim.objects.bulk_create([DefenseClaim(session=s, claim=c, question=q) for c, q in claims])
        return Response(session_out(s), status=201)


class DefenseAnswer(APIView):
    def post(self, request, pk):
        c = get_object_or_404(DefenseClaim, pk=pk, session__user=request.user)
        text = str(request.data.get("answer", "")).strip()[:3000]
        if len(text) < 10:
            return Response({"error": "Write at least a sentence."}, status=400)
        try:
            attempts = min(max(int(request.data.get("paste_attempts", 0)), 0), 50)
        except (TypeError, ValueError):
            attempts = 0
        c.paste_attempts = min(c.paste_attempts + attempts, 255)

        if not c.answer:
            c.answer = text
            res = judge(c.claim, c.question, [text], want_followup=True)
            c.followup = res["followup"] or "What would you do differently if you did it again, and why?"
        elif not c.followup_answer:
            c.followup_answer = text
            res = judge(c.claim, c.question, [c.answer, text], want_followup=False)
        else:
            return Response({"error": "This claim is already finished."}, status=400)
        c.verdict, c.feedback = res["verdict"], res["feedback"]
        c.save()
        record_usage(request.user, "defense")
        return Response(claim_out(c))