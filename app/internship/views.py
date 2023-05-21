from accounts.models import User
from accounts.permissions import (
    IsCandidate,
    IsCurator,
    IsMentor,
    IsPersonnel,
    IsTrainee,
)
from django_filters.rest_framework import DjangoFilterBackend
from internship.models import InternshipApplication, Vacancy, VacancyResponse
from internship.serializers import (
    InternshipApplicationSerializer,
    ReadInternshipApplicationSerializer,
    ReadVacancyResponseSerializer,
    ReadVacancySerializer,
    VacancyResponseSerializer,
    VacancySerializer,
)
from rest_framework import permissions, viewsets


class InternshipApplicationViewSet(viewsets.ModelViewSet):
    queryset = InternshipApplication.objects.all()
    serializer_class = InternshipApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_recommended"]

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


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["direction", "status", "reviewed_by", "department"]
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
                # TODO: uncomment when direction will be added to trainee profile
                # direction=self.request.user.trainee_profile.direction,
            )
        return qs


class VacancyResponseViewSet(viewsets.ModelViewSet):
    queryset = VacancyResponse.objects.all()
    serializer_class = VacancyResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permission_classes(self):
        if self.action == "create" or self.action == "destroy":
            return [permissions.IsAuthenticated, IsTrainee]
        return [
            permissions.IsAuthenticated,
            IsCurator | IsPersonnel | IsTrainee | IsMentor,
        ]

    def get_permissions(self):
        return [perm() for perm in self.get_permission_classes()]

    def get_serializer_class(self):
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
