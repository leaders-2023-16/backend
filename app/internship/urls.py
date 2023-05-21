from django.urls import include, path
from internship.views import (
    InternshipApplicationViewSet,
    VacancyResponseViewSet,
    VacancyViewSet,
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

urlpatterns = [
    path("", include(router.urls)),
]
