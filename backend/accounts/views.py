from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, data):
        return User.objects.create_user(**data)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["target_role", "education", "experience", "skills", "experience_level"]


class ProfileView(APIView):
    def get(self, request):
        p, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(p).data)

    def put(self, request):
        p, _ = UserProfile.objects.get_or_create(user=request.user)
        s = ProfileSerializer(p, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)


class PasswordResetRequest(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        user = User.objects.filter(email__iexact=request.data.get("email", "")).first()
        if user:  # same reply either way so emails can't be enumerated
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_mail("Reset your password", f"Open: {settings.FRONTEND_URL}/reset?uid={uid}&token={token}",
                      None, [user.email])
        return Response({"detail": "If that email exists, a reset link was sent."})


class PasswordResetConfirm(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(request.data.get("uid", ""))))
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid link"}, status=400)
        if not default_token_generator.check_token(user, request.data.get("token", "")):
            return Response({"error": "Link expired or invalid"}, status=400)
        validate_password(request.data.get("password", ""), user)
        user.set_password(request.data["password"])
        user.save()
        return Response({"detail": "Password updated"})

class DeleteAccountView(APIView):
    """Permanently delete the logged-in user and all their data (resumes, sessions, stories...)."""

    def delete(self, request):
        if not request.user.check_password(request.data.get("password", "")):
            return Response({"error": "Password is incorrect"}, status=400)
        request.user.delete()
        return Response(status=204)