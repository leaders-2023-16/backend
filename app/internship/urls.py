from django.urls import include, path
from internship.views import (
    InternshipApplicationViewSet,
    VacancyResponseViewSet,
    VacancyViewSet,
    WorkPlaceViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    r"internship-applications",
    InternshipApplicationViewSet,
    basename="internship-application",
)
router.register(r"vacancies", VacancyViewSet, basename="vacancies")
router.register(
    r"vacancy-response", VacancyResponseViewSet, basename="vacancy-responses"
)
router.register(r"work-places", WorkPlaceViewSet, basename="work-places")
urlpatterns = [
    path("", include(router.urls)),
]
