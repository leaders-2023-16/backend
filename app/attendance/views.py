from accounts.permissions import IsCurator, IsMentor, IsPersonnel, IsTrainee
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
    filterset_fields = ["role", "department"]

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
        return self.queryset
