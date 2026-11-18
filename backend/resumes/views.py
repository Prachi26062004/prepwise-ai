import os

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .analysis import ExtractionError, analyze, extract_text, validate_resume
from .bullets import analyze_bullets
from .models import Resume
from ai_engine.services import rewrite_bullet
from ai_engine.usage import record_usage


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ["id", "filename", "analysis", "created_at"]


class ResumeListCreate(APIView):
    parser_classes = [MultiPartParser]

    def get(self, request):
        return Response(ResumeSerializer(Resume.objects.filter(user=request.user), many=True).data)

    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return Response({"error": "No file uploaded"}, status=400)
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in (".pdf", ".docx") or f.size > settings.MAX_UPLOAD_BYTES:
            return Response({"error": "Upload a PDF or DOCX under 5 MB."}, status=400)
        try:
            text = extract_text(f.read(), ext)
        except ExtractionError as exc:
            return Response({"error": str(exc)}, status=400)
        is_resume, reason = validate_resume(text)
        if not is_resume:
            return Response({"error": reason}, status=400)
        r = Resume.objects.create(user=request.user, filename=os.path.basename(f.name)[:255],
                                  text=text, analysis=analyze(text))
        return Response(ResumeSerializer(r).data, status=status.HTTP_201_CREATED)


class ResumeDetail(APIView):
    def get(self, request, pk):
        return Response(ResumeSerializer(get_object_or_404(Resume, pk=pk, user=request.user)).data)

    def delete(self, request, pk):
        get_object_or_404(Resume, pk=pk, user=request.user).delete()
        return Response(status=204)


class ResumeBullets(APIView):
    def get(self, request, pk):
        r = get_object_or_404(Resume, pk=pk, user=request.user)
        return Response(analyze_bullets(r.text))

class ResumeRewrite(APIView):
    def post(self, request, pk):
        r = get_object_or_404(Resume, pk=pk, user=request.user)
        bullet = str(request.data.get("bullet", "")).strip()
        if not bullet or len(bullet) > 400 or bullet not in r.text:
            return Response({"error": "Pick a bullet from your own resume."}, status=400)
        result = rewrite_bullet(bullet, str(request.data.get("role", "Software Engineer"))[:80])
        record_usage(request.user, "rewrite")
        return Response(result)