from accounts.models import User
from accounts.permissions import IsCurator, IsMentor, IsPersonnel, IsTrainee
from attendance.filters import ReportFilterSet
from attendance.models import Report
from attendance.serializers import ReportSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReportFilterSet

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsCurator | IsMentor]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsTrainee]
        else:
            permission_classes = [
                IsAuthenticated,
                IsCurator | IsPersonnel | IsMentor | IsTrainee,
            ]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.role == User.Role.PERSONNEL:
            return self.queryset.filter(
                work_place__mentor__department=self.request.user.department
            )
        if self.request.user.role == User.Role.MENTOR:
            return self.queryset.filter(work_place__mentor=self.request.user)
        if self.request.user.role == User.Role.TRAINEE:
            return self.queryset.filter(work_place__trainee=self.request.user)
        return self.queryset
