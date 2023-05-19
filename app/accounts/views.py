from accounts.models import Country, TraineeProfile, User
from accounts.permissions import OwnProfilePermission
from accounts.serializers import CountrySerializer, TraineeProfileSerializer
from django.contrib.auth import login
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


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


class RegistrationAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        gender = request.data.get("gender")
        age = int(request.data.get("age"))

        # Создание нового пользователя
        user = User.objects.create_user(
            username=username, password=password, gender=gender, age=age
        )

        # Вход в систему после регистрации
        login(request, user)

        # Создание и получение JWT-токенов
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Создание профиля стажера и связывание с пользователем
        trainee_profile = TraineeProfile.objects.create(user=user)

        # Сериализация профиля стажера
        profile_serializer = TraineeProfileSerializer(trainee_profile)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh,
                "trainee_profile": profile_serializer.data,
            }
        )
