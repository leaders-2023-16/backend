from accounts.permissions import IsCandidate, IsCurator
from internship.models import InternshipApplication
from internship.serializers import InternshipApplicationSerializer
from rest_framework import permissions, viewsets


class InternshipApplicationViewSet(viewsets.ModelViewSet):
    queryset = InternshipApplication.objects.all()
    serializer_class = InternshipApplicationSerializer

    def get_permissions(self):
        if self.action == "create" or self.action == "destroy":
            return [permissions.IsAuthenticated(), IsCandidate()]
        elif self.action == "update" or self.action == "partial_update":
            return [permissions.IsAuthenticated(), IsCurator()]
        return [permissions.IsAuthenticated()]
