from accounts.views import (
    CountryViewSet,
    DecoratedTokenObtainPairView,
    DepartmentViewSet,
    RegistrationAPIView,
    TokenRefreshAndAccessView,
    TraineeProfileViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    r"users/trainee-profiles", TraineeProfileViewSet, basename="trainee-profiles"
)
router.register(r"countries", CountryViewSet, basename="countries")
router.register(r"departments", DepartmentViewSet, basename="departments")

urlpatterns = [
    path("", include(router.urls)),
    path("sign-up/", RegistrationAPIView.as_view(), name="sign-up"),
    path(
        "auth/sign-in", DecoratedTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("auth/refresh", TokenRefreshAndAccessView.as_view(), name="token_refresh"),
]
