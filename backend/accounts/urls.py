from django.urls import path

from .views import (DeleteAccountView, PasswordResetConfirm, PasswordResetRequest,
                    ProfileView, RegisterView)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("me/", DeleteAccountView.as_view()),
    path("password-reset/", PasswordResetRequest.as_view()),
    path("password-reset/confirm/", PasswordResetConfirm.as_view()),
]