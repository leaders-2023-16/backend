from django.urls import include, path
from internship.views import InternshipApplicationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    r"internship-applications",
    InternshipApplicationViewSet,
    basename="internship-application",
)

urlpatterns = [
    path("", include(router.urls)),
]
