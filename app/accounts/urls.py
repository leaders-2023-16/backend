from accounts.views import (
    CountryViewSet,
    DecoratedTokenObtainPairView,
    DepartmentViewSet,
    SignUpAPIView,
    TokenRefreshAndAccessView,
    TraineeProfileViewSet,
    UserViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    r"users/trainee-profiles", TraineeProfileViewSet, basename="trainee-profiles"
)
router.register(r"countries", CountryViewSet, basename="countries")
router.register(r"departments", DepartmentViewSet, basename="departments")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/sign-up", SignUpAPIView.as_view(), name="sign-up"),
    path(
        "auth/sign-in", DecoratedTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("auth/refresh", TokenRefreshAndAccessView.as_view(), name="token_refresh"),
]
