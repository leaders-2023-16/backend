from accounts.views import CountryViewSet, RegistrationAPIView, TraineeProfileViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    r"users/trainee-profiles", TraineeProfileViewSet, basename="trainee-profiles"
)
router.register(r"countries", CountryViewSet, basename="countries")

urlpatterns = [
    path("", include(router.urls)),
    path("sign-up/", RegistrationAPIView.as_view(), name="sign-up"),
]
