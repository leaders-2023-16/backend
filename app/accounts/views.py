from rest_framework import serializers
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
