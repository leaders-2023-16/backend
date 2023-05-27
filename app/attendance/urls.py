from attendance.views import ReportViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("reports", ReportViewSet, basename="reports")


urlpatterns = [
    path("", include(router.urls)),
]
