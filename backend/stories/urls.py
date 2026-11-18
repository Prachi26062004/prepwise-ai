from django.urls import path

from .views import StoryDetail, StoryList, StorySuggest

urlpatterns = [
    path("", StoryList.as_view()),
    path("suggest/", StorySuggest.as_view()),
    path("<int:pk>/", StoryDetail.as_view()),
]