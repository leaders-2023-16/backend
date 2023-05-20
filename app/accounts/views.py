from accounts.models import Country, Department, TraineeProfile, User
from accounts.permissions import OwnProfilePermission
from accounts.serializers import (
    CountrySerializer,
    DepartmentSerializer,
    SignUpSerializer,
    TokenObtainPairResponseSerializer,
    TokenRefreshSerializer,
    TraineeProfileSerializer,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class DecoratedTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer(),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


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


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer()

    @action(methods=["POST"], detail=False)
    def sign_up(self, request):
        serializer = self.get_serializer(request.data)
        serializer.is_valid()
        instance = serializer.save()
        return Response(TraineeProfileSerializer(instance.trainee_profile))


class RegistrationAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["first_name", "last_name", "email", "password"],
        ),
        responses={
            200: "OK",
            # Добавьте здесь другие возможные коды ответов, если требуется
        },
    )
    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")
        username = request.data.get("username")
        try:
            User.objects.get(username=username)
            return Response(
                {"detail": "USER_ALREADY_EXISTS"}, status=status.HTTP_409_CONFLICT
            )
        except User.DoesNotExist:
            pass
        # Создание нового пользователя
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
        )

        # Создание и получение JWT-токенов
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Создание профиля стажера и связывание с пользователем
        trainee_profile = user.trainee_profile

        # Сериализация профиля стажера
        profile_serializer = TraineeProfileSerializer(trainee_profile)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": str(refresh),
                "trainee_profile": profile_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class DepartmentViewSet(ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    @method_decorator(cache_page(60 * 60 * 6))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
