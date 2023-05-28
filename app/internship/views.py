from accounts.models import TraineeProfile, User
from accounts.permissions import (
    IsCandidate,
    IsCurator,
    IsMentor,
    IsPersonnel,
    IsTrainee,
)
from django.conf import settings
from django.db import transaction
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from internship.models import (
    Event,
    FeedBack,
    InternshipApplication,
    Vacancy,
    VacancyResponse,
    WorkPlace,
)
from internship.serializers import (
    CountSerializer,
    EventSerializer,
    FeedbackSerializer,
    InternshipApplicationSerializer,
    ReadEventSerializer,
    ReadFeedbackSerializer,
    ReadInternshipApplicationSerializer,
    ReadVacancyResponseSerializer,
    ReadVacancySerializer,
    ReadWorkPlaceSerializer,
    VacancyResponseSerializer,
    VacancySerializer,
    WorkPlaceSerializer,
)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class InternshipApplicationViewSet(viewsets.ModelViewSet):
    queryset = InternshipApplication.objects.all()
    serializer_class = InternshipApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_recommended", "direction", "status", "applicant"]

    def get_permissions(self):
        if self.action == "create" or self.action == "destroy":
            return [permissions.IsAuthenticated(), IsCandidate()]
        elif self.action == "update" or self.action == "partial_update":
            return [permissions.IsAuthenticated(), IsCurator()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action not in ("update", "partial_update", "create"):
            return ReadInternshipApplicationSerializer
        return self.serializer_class

    @extend_schema(
        description="Закончить отбор",
        summary="Закончить отбор",
        request=None,
        responses={status.HTTP_200_OK: CountSerializer()},
    )
    @action(detail=False, methods=["POST"], url_path="end-up-selection")
    def end_up_selection(self, request):
        profiles = list(
            TraineeProfile.objects.get_rating().prefetch_related("user__applications")
        )
        updated_applications = []
        updated_users = []
        for profile in profiles[: settings.SELECTION_COUNT]:
            profile.user.applications.status = InternshipApplication.Status.APPROVED
            updated_applications.append(profile.user.applications)
            profile.user.role = User.Role.TRAINEE
            updated_users.append(profile.user)
        for profile in profiles[settings.SELECTION_COUNT :]:
            profile.user.applications.status = InternshipApplication.Status.REJECTED
            updated_applications.append(profile.user.applications)
        InternshipApplication.objects.bulk_update(
            updated_applications, fields=["status"]
        )
        User.objects.bulk_update(updated_users, fields=["role"])

        return Response({"count": len(profiles)}, status=status.HTTP_200_OK)


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["direction", "status", "reviewed_by", "department", "schedule"]
    permission_classes = [permissions.IsAuthenticated]

    def get_permission_classes(self):
        if self.action == "create" or self.action == "destroy":
            return [permissions.IsAuthenticated, IsPersonnel]
        elif self.action == "update" or self.action == "partial_update":
            return [permissions.IsAuthenticated, IsCurator | IsPersonnel]
        return [permissions.IsAuthenticated, IsCurator | IsPersonnel | IsTrainee]

    def get_permissions(self):
        return [perm() for perm in self.get_permission_classes()]

    def get_serializer_class(self):
        if self.action not in ("update", "partial_update", "create"):
            return ReadVacancySerializer
        return self.serializer_class

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.role == User.Role.TRAINEE:
            return qs.filter(
                status=Vacancy.Status.PUBLISHED,
                direction=self.request.user.applications.direction,
            )
        return qs


class VacancyResponseViewSet(viewsets.ModelViewSet):
    queryset = VacancyResponse.objects.all()
    serializer_class = VacancyResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["approved_by_mentor", "approved_by_applicant", "vacancy"]

    def get_permission_classes(self):
        if self.action == "create" or self.action == "destroy":
            return [permissions.IsAuthenticated, IsTrainee]
        if self.action == "approve":
            return [permissions.IsAuthenticated, IsCurator]
        return [
            permissions.IsAuthenticated,
            IsCurator | IsPersonnel | IsTrainee | IsMentor,
        ]

    def get_permissions(self):
        return [perm() for perm in self.get_permission_classes()]

    def get_serializer_class(self):
        if self.action == "approve":
            return WorkPlaceSerializer
        if self.action not in ("update", "partial_update", "create"):
            return ReadVacancyResponseSerializer
        return self.serializer_class

    def get_queryset(self):
        qs = self.queryset
        if self.action not in ("create", "update", "partial_update"):
            qs.select_related("vacancy", "applicant")
        if self.request.user.role == User.Role.TRAINEE:
            return qs.filter(applicant=self.request.user.trainee_profile)
        if self.request.user.role == User.Role.MENTOR:
            return qs.filter(vacancy__mentor=self.request.user)
        if self.request.user.role == User.Role.PERSONNEL:
            return qs.filter(vacancy__department=self.request.user.department)
        return qs

    @action(detail=True, methods=["GET"], url_path="by-vacancy")
    def by_vacancy(self, request, pk=None):
        try:
            vacancy_response = VacancyResponse.objects.filter(
                vacancy_id=pk, applicant_id=self.request.user.id
            ).get()
        except VacancyResponse.DoesNotExist:
            raise Http404
        serializer = self.get_serializer(vacancy_response)
        return Response(data=serializer.data)

    @extend_schema(
        description="Approve the candidate to this mentor",
        summary="Approve the candidate to this mentor",
        request=None,
    )
    @action(detail=True, methods=["POST"])
    @transaction.atomic
    def approve(self, request, pk=None):
        vacancy_response: VacancyResponse = self.get_object()
        work_place = WorkPlace.objects.create(
            name=vacancy_response.vacancy.name,
            vacancy_id=vacancy_response.vacancy_id,
            trainee_id=vacancy_response.applicant_id,
            mentor_id=vacancy_response.vacancy.mentor_id,
            department_id=vacancy_response.vacancy.department_id,
        )
        vacancy_response.vacancy.status = Vacancy.Status.CLOSED
        vacancy_response.vacancy.save()
        serializer = self.get_serializer(work_place)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class WorkPlaceViewSet(viewsets.ModelViewSet):
    queryset = WorkPlace.objects.all()
    serializer_class = WorkPlaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "is_active",
        "created_at",
        "updated_at",
        "department",
        "trainee",
        "mentor",
    ]

    def get_permission_classes(self):
        if self.action == "current":
            return [permissions.IsAuthenticated, IsTrainee | IsMentor]
        return [
            permissions.IsAuthenticated,
            IsCurator | IsPersonnel | IsTrainee | IsMentor,
        ]

    def get_permissions(self):
        return [perm() for perm in self.get_permission_classes()]

    def get_serializer_class(self):
        if self.action not in ("update", "partial_update", "create"):
            return ReadWorkPlaceSerializer
        return self.serializer_class

    @action(detail=False, methods=["GET"])
    def current(self, request):
        work_place = request.user.current_work_place
        if work_place:
            serializer = self.get_serializer(work_place)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Not found active work places"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=["GET"], url_path="by-trainee")
    def by_trainee(self, request, pk=None):
        try:
            work_place = WorkPlace.objects.filter(trainee_id=pk, is_active=True).get()
        except WorkPlace.DoesNotExist:
            raise Http404
        serializer = self.get_serializer(work_place)
        return Response(data=serializer.data)


class FeedBackViewSet(viewsets.ModelViewSet):
    queryset = FeedBack.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "from_user",
        "to_user",
        "date",
        "rating",
    ]

    def get_permission_classes(self):
        if self.action == "create":
            return [permissions.IsAuthenticated, IsTrainee | IsMentor]
        return [
            permissions.IsAuthenticated,
            IsCurator | IsPersonnel | IsTrainee | IsMentor,
        ]

    def get_permissions(self):
        return [perm() for perm in self.get_permission_classes()]

    def get_serializer_class(self):
        if self.action not in ("update", "partial_update", "create"):
            return ReadFeedbackSerializer
        return self.serializer_class


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "datetime",
        "workplace",
    ]

    def get_permission_classes(self):
        if self.action == "create":
            return [permissions.IsAuthenticated, IsMentor]
        return [
            permissions.IsAuthenticated,
            IsCurator | IsPersonnel | IsTrainee | IsMentor,
        ]

    def get_permissions(self):
        return [perm() for perm in self.get_permission_classes()]

    def get_serializer_class(self):
        if self.action not in ("update", "partial_update", "create"):
            return ReadEventSerializer
        return self.serializer_class
