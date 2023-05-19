from accounts.models import Country, TraineeProfile
from accounts.permissions import OwnProfilePermission
from accounts.serializers import CountrySerializer, TraineeProfileSerializer
from rest_framework import serializers, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")
        if refresh_token:
            try:
                refresh_token = RefreshToken(refresh_token)
                refresh_token.verify()
                attrs["refresh_token"] = refresh_token
            except TokenError:
                raise serializers.ValidationError("Invalid refresh token")
        else:
            raise serializers.ValidationError("Refresh token is required")

        return attrs


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
