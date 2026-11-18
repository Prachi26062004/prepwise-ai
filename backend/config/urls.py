from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("", lambda request: JsonResponse({"service": "PrepWise API", "docs": "/api/docs/"})),
    path("api/auth/login/", TokenObtainPairView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/", include("accounts.urls")),
    path("api/resumes/", include("resumes.urls")),
    path("api/match/", include("job_matcher.urls")),
    path("api/interviews/", include("interviews.urls")),
    path("api/roadmaps/", include("roadmaps.urls")),
    path("api/dashboard/", include("analytics.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/stories/", include("stories.urls")),
    path("api/applications/", include("tracker.urls")),
    path("api/defense/", include("defense.urls")),
]