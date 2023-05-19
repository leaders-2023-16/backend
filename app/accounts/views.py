from accounts.models import Country, Department, TraineeProfile
from accounts.permissions import OwnProfilePermission
from accounts.serializers import (
    CountrySerializer,
    DepartmentSerializer,
    TokenRefreshSerializer,
    TraineeProfileSerializer,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView


class TokenRefreshAndAccessView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        refresh_token = serializer.validated_data["refresh"]
        access_token = RefreshToken(refresh_token).access_token

        return Response(
            {
                "access": str(access_token),
                "refresh": str(refresh_token),
            }
        )


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


class DepartmentViewSet(ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    @method_decorator(cache_page(60 * 60 * 6))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
