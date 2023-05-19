from accounts.views import (
    CountryViewSet,
    TokenRefreshAndAccessView,
    TraineeProfileViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

router = DefaultRouter()
router.register(r"trainee-profiles", TraineeProfileViewSet, basename="trainee-profiles")
router.register(r"countries", CountryViewSet, basename="countries")

urlpatterns = [
    path("", include(router.urls)),
    path("api/auth/sign-in", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh", TokenRefreshAndAccessView.as_view(), name="token_refresh"),
]
