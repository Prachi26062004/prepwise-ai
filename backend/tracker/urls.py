from django.urls import path

from .views import ApplicationDetail, ApplicationList

urlpatterns = [
    path("", ApplicationList.as_view()),
    path("<int:pk>/", ApplicationDetail.as_view()),
]