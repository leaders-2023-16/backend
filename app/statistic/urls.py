from django.urls import path
from statistic.views import StatisticsAPIView

urlpatterns = [
    path(
        "statistics/",
        StatisticsAPIView.as_view(),
        name="statistics",
    ),
]
