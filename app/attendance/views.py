from datetime import datetime

from accounts.models import User
from accounts.permissions import IsCurator, IsMentor, IsPersonnel, IsTrainee
from attendance.excel_exporter import form_report
from attendance.filters import ReportFilterSet
from attendance.models import Report
from attendance.serializers import ReportSerializer
from django.core.files import File
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from internship.models import WorkPlace
from rest_framework import viewsets
from rest_framework.decorators import action
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
        elif self.action == "total_report":
            permission_classes = [IsAuthenticated, IsCurator | IsPersonnel]
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

    @action(detail=False, methods=["GET"])
    def export(self, request):
        date = request.GET.get("date", None)
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        queryset = WorkPlace.objects.all()
        if request.user.role == User.Role.PERSONNEL:
            queryset = queryset.filter(work_place__department=request.user.department)
        filename = form_report(queryset, date)
        with open(filename, "rb") as file:
            response = HttpResponse(
                File(file),
                content_type=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
