from django.urls import path

from .views import ResumeBullets, ResumeDetail, ResumeListCreate, ResumeRewrite

urlpatterns = [
    path("", ResumeListCreate.as_view()),
    path("<int:pk>/", ResumeDetail.as_view()),
    path("<int:pk>/bullets/", ResumeBullets.as_view()),
    path("<int:pk>/rewrite/", ResumeRewrite.as_view()),
]