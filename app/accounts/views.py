from accounts.models import Country, TraineeProfile
from accounts.permissions import OwnProfilePermission
from accounts.serializers import CountrySerializer, TraineeProfileSerializer
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated


class TraineeProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = TraineeProfile.objects.all()
    serializer_class = TraineeProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = "user_id"

    def get_permissions(self):
        if self.action in ("update", "partial_update"):
            return IsAuthenticated(), OwnProfilePermission()
        return super().get_permissions()


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
