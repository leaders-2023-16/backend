from accounts.views import (
    CountryViewSet,
    TokenRefreshAndAccessView,
    TraineeProfileViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

router = DefaultRouter()
router.register(
    r"users/trainee-profiles", TraineeProfileViewSet, basename="trainee-profiles"
)
router.register(r"countries", CountryViewSet, basename="countries")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/sign-in", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh", TokenRefreshAndAccessView.as_view(), name="token_refresh"),
]
