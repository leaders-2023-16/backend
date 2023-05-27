from accounts.models import Country, Department, TraineeProfile, User
from accounts.permissions import IsCurator, IsMentor, IsPersonnel, OwnProfilePermission
from accounts.serializers import (
    CountrySerializer,
    DepartmentSerializer,
    RatingTraineeProfileSerializer,
    ReadTraineeProfileSerializer,
    SignUpSerializer,
    TokenObtainPairResponseSerializer,
    TokenObtainPairWithUserIdSerializer,
    TokenRefreshSerializer,
    TraineeProfileSerializer,
    UserSerializer,
)
from django.db.models import F, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
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
    @extend_schema(
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


class SignUpAPIView(APIView):
    @extend_schema(
        request=SignUpSerializer(),
        responses={
            200: TokenObtainPairResponseSerializer(),
        },
    )
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = TokenObtainPairWithUserIdSerializer(
            data={
                "username": serializer.validated_data["username"],
                "password": serializer.validated_data["password"],
            }
        )
        response_serializer.is_valid()
        return Response(response_serializer.validated_data, status=201)


class TraineeProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = TraineeProfile.objects.all()
    serializer_class = TraineeProfileSerializer
    lookup_field = "user_id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsCurator | OwnProfilePermission]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "rating":
            return RatingTraineeProfileSerializer
        if self.action not in ("update", "partial_update", "create"):
            return ReadTraineeProfileSerializer
        return self.serializer_class

    def get_queryset(self):
        if self.action == "rating":
            return (
                self.queryset.filter(status=TraineeProfile.QualifyingStatus.PASSED)
                .annotate(total_score=F("cv_score") + F("test_score"))
                .order_by("-total_score")
            )
        return self.queryset

    @action(detail=False, methods=["GET"])
    def rating(self, request):
        return self.list(request)


class UserViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["role", "department"]

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsCurator | OwnProfilePermission]
        elif self.action in "free_mentors":
            permission_classes = [IsAuthenticated, IsCurator | IsPersonnel]
        else:
            permission_classes = [IsAuthenticated, IsCurator | IsPersonnel | IsMentor]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action == "free_mentors":
            qs = self.queryset.filter(role=User.Role.MENTOR, mentor_of__isnull=True)
            if self.request.user.role == User.Role.PERSONNEL:
                qs = qs.filter(department=self.request.user.department)
            return qs
        if self.request.user.role == User.Role.PERSONNEL:
            department = self.request.user.department
            return self.queryset.filter(
                Q(department=department)
                | Q(trainee_profile__vacancyresponse__vacancy__department=department)
            )
        if self.request.user.role == User.Role.MENTOR:
            return self.queryset.filter(
                trainee_profile__vacancyresponse__vacancy__mentor=self.request.user
            )
        return self.queryset

    @action(methods=["GET"], detail=False, url_path="free-mentors")
    def free_mentors(self, request):
        return self.list(request)


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = None


class DepartmentViewSet(ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = None

    @method_decorator(cache_page(60 * 60 * 6))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
