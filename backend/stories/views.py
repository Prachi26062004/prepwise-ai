import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Story

PARTS = ["situation", "task", "action", "result"]


class StorySerializer(serializers.ModelSerializer):
    missing = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ["id", "title", "tags", "situation", "task", "action", "result", "missing"]

    def get_missing(self, obj):
        return [p for p in PARTS if len(getattr(obj, p).strip()) < 15]

    def validate_tags(self, value):
        if not isinstance(value, list) or len(value) > 8 or not all(isinstance(t, str) and len(t) <= 30 for t in value):
            raise serializers.ValidationError("Up to 8 short text tags.")
        return value


class StoryList(APIView):
    def get(self, request):
        return Response(StorySerializer(Story.objects.filter(user=request.user), many=True).data)

    def post(self, request):
        s = StorySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(user=request.user)
        return Response(s.data, status=201)


class StoryDetail(APIView):
    def put(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        s = StorySerializer(story, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, pk):
        get_object_or_404(Story, pk=pk, user=request.user).delete()
        return Response(status=204)


class StorySuggest(APIView):
    """Rank the user's stories against an interview question by shared tags and words."""

    def post(self, request):
        question = str(request.data.get("question", "")).lower()[:500]
        if not question.strip():
            return Response({"error": "Provide a question."}, status=400)
        q_words = set(re.findall(r"[a-z]{4,}", question))
        ranked = []
        for story in Story.objects.filter(user=request.user):
            text = " ".join([story.title, story.situation, story.task, story.action, story.result]).lower()
            tag_hits = sum(1 for t in story.tags if t.lower() in question)
            word_hits = len(q_words & set(re.findall(r"[a-z]{4,}", text)))
            score = tag_hits * 3 + word_hits
            if score > 0:
                ranked.append((score, story))
        ranked.sort(key=lambda x: -x[0])
        return Response([StorySerializer(s).data for _, s in ranked[:3]])