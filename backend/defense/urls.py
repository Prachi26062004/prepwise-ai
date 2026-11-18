from django.urls import path

from .views import DefenseAnswer, DefenseView

urlpatterns = [
    path("", DefenseView.as_view()),
    path("claims/<int:pk>/answer/", DefenseAnswer.as_view()),
]