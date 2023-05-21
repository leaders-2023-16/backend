from accounts.models import User
from accounts.permissions import IsCandidate, IsCurator, IsPersonnel, IsTrainee
from django_filters.rest_framework import DjangoFilterBackend
from internship.models import InternshipApplication, Vacancy
from internship.serializers import (
    InternshipApplicationSerializer,
    ReadInternshipApplicationSerializer,
    ReadVacancySerializer,
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
    filterset_fields = ["direction", "status"]
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
            return qs.filter(status=Vacancy.Status.PUBLISHED)
        return qs
