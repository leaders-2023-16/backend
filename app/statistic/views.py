from collections import Counter

from accounts.models import TraineeProfile
from django.db.models import Count, ExpressionWrapper, F, Sum, fields
from django.db.models.functions import Coalesce, ExtractYear
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from internship.models import InternshipApplication, Vacancy
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from statistic.serializers import StatisticsSerializer


class StatisticsAPIView(APIView):
    @extend_schema(responses={status.HTTP_200_OK: StatisticsSerializer})
    def get(self, request):
        total_responses = InternshipApplication.objects.count()
        relevant_responses = InternshipApplication.objects.filter(
            is_recommended=True
        ).count()
        irrelevant_responses = total_responses - relevant_responses

        age_statistics = (
            TraineeProfile.objects.annotate(
                label=timezone.now().year - ExtractYear("birth_date")
            )
            .values("label")
            .annotate(count=Count("label"))
        )

        education_statistics_by_name = (
            TraineeProfile.objects.values("educations__name")
            .annotate(count=Count("educations__name"), label=F("educations__name"))
            .values("count", "label")
        )
        education_statistics_by_type = (
            TraineeProfile.objects.values("educations__type")
            .annotate(count=Count("educations__type"), label=F("educations__type"))
            .values("count", "label")
        )

        work_experience_statistics = get_work_experience_statistics()

        # Направления стажировки
        direction_statistics = (
            InternshipApplication.objects.values("direction__name")
            .annotate(count=Count("direction"), label=F("direction__name"))
            .values("count", "label")
        )
        government_applications = Vacancy.objects.count()
        government_entities_applications = (
            Vacancy.objects.values("department__name")
            .annotate(count=Count("department__name"), label=F("department__name"))
            .values("count", "label")
        )

        statistics = {
            "responses": {
                "total": total_responses,
                "relevant": relevant_responses,
                "irrelevant": irrelevant_responses,
            },
            "age_statistics": age_statistics,
            "education": {
                "by_name": education_statistics_by_name,
                "by_type": education_statistics_by_type,
            },
            "work_experience": work_experience_statistics,
            "direction_statistics": direction_statistics,
            "vacancies": {
                "total": government_applications,
                "by_department": government_entities_applications,
            },
        }

        return Response(statistics)


def get_work_experience_statistics():
    work_experience_statistics = TraineeProfile.objects.annotate(
        total_experience=Sum(
            ExpressionWrapper(
                F("work_experiences__end_date")
                - Coalesce(F("work_experiences__start_date"), timezone.now().date()),
                output_field=fields.DurationField(),
            )
        )
    ).values_list("total_experience", flat=True)
    work_experience_statistics = [
        val.days // 365 if val else val for val in work_experience_statistics
    ]
    work_experience_statistics = Counter(work_experience_statistics)
    output = []
    for key, value in work_experience_statistics.items():
        output.append({"label": key, "count": value})
    return output
