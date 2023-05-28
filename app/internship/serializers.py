from accounts.models import User
from accounts.serializers import (
    DepartmentSerializer,
    ReadTraineeProfileSerializer,
    UserSerializer,
    UserWithProfileSerialization,
)
from django.db import transaction
from django.utils import timezone
from internship.models import (
    Direction,
    Event,
    FeedBack,
    InternshipApplication,
    Qualification,
    TestTask,
    Vacancy,
    VacancyResponse,
    WorkPlace,
)
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


class ReadInternshipApplicationSerializer(serializers.ModelSerializer):
    applicant = UserWithProfileSerialization()
    status_changed_by = UserSerializer()
    is_recommended = serializers.BooleanField()  # TODO: hide field for candidate

    class Meta:
        model = InternshipApplication
        fields = (
            "status",
            "status_changed_at",
            "status_changed_by",
            "applicant",
            "created_at",
            "is_recommended",
            "direction",
        )


class InternshipApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipApplication
        fields = "__all__"
        read_only_fields = ("status_changed_at", "status_changed_by", "applicant")

    def create(self, validated_data: dict):
        validated_data["applicant"] = self.context["request"].user
        if "status" in validated_data:
            del validated_data["status"]
        instance = super().create(validated_data)
        return instance.set_recommendation()

    def update(self, instance, validated_data):
        if "direction" in validated_data:
            validated_data.pop("direction")
        if "status" in validated_data and instance.status != validated_data["status"]:
            instance.status_changed_at = timezone.now()
            instance.status_changed_by = self.context["request"].user
        return super().update(instance, validated_data)


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ["id", "name"]


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = ["id", "name"]


class TestTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestTask
        fields = ["id", "title", "type", "description"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return TestTask.objects.create(
            **validated_data, department=self.context["department"]
        )


class ReadVacancySerializer(serializers.ModelSerializer):
    required_qualifications = QualificationSerializer(many=True)
    direction = DirectionSerializer()
    department = DepartmentSerializer()
    owner = UserSerializer()
    reviewed_by = UserSerializer(required=False)
    mentor = UserSerializer()
    test_task = TestTaskSerializer()

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "required_qualifications",
            "name",
            "description",
            "direction",
            "department",
            "owner",
            "status",
            "reviewed_by",
            "mentor",
            "test_task",
            "published_at",
            "created_at",
            "schedule",
        ]


class VacancySerializer(serializers.ModelSerializer):
    required_qualifications = serializers.ListSerializer(child=serializers.CharField())
    test_task = TestTaskSerializer()

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "required_qualifications",
            "name",
            "description",
            "direction",
            "department",
            "owner",
            "status",
            "reviewed_by",
            "mentor",
            "published_at",
            "created_at",
            "test_task",
            "schedule",
        ]
        read_only_fields = (
            "id",
            "department",
            "owner",
            "reviewed_by",
            "published_at",
            "created_at",
        )

    @transaction.atomic
    def create(self, validated_data):
        qualifications = validated_data.pop("required_qualifications")
        test_task_data = validated_data.pop("test_task")
        validated_data.pop("status")  # publishing only after curator review
        validated_data["owner"] = self.context["request"].user
        department = self.context["request"].user.department
        validated_data["department"] = department
        serializer = TestTaskSerializer(
            data=test_task_data,
            context={"department": department},
        )
        serializer.is_valid(raise_exception=True)
        test_task = serializer.save()
        vacancy = Vacancy.objects.create(**validated_data, test_task=test_task)
        qualifications = [Qualification(name=name) for name in qualifications]
        qualifications = Qualification.objects.bulk_create(qualifications)
        vacancy.required_qualifications.set(qualifications)
        vacancy.save()
        return vacancy

    @transaction.atomic
    def update(self, instance: Vacancy, validated_data):
        if "status" in validated_data and validated_data["status"] != instance.status:
            if self.context["request"].user.role != User.Role.CURATOR:
                raise PermissionDenied()
            if validated_data["status"] == Vacancy.Status.PUBLISHED:
                validated_data["published_at"] = timezone.now()
                validated_data["reviewed_by"] = self.context["request"].user

        test_task_data = validated_data.pop("test_task", None)
        if test_task_data is not None:
            serializer = TestTaskSerializer(
                data=test_task_data, context={"department": instance.department}
            )
            serializer.is_valid(raise_exception=True)
            test_task = serializer.save()
            instance.test_task = test_task
        qualifications = validated_data.pop("required_qualifications", None)
        if qualifications is not None:
            qualifications = [Qualification(name=name) for name in qualifications]
            qualifications = Qualification.objects.bulk_create(qualifications)
            instance.required_qualifications.set(qualifications)
        return super().update(instance, validated_data)


class ReadVacancyResponseSerializer(serializers.ModelSerializer):
    vacancy = ReadVacancySerializer()
    applicant = ReadTraineeProfileSerializer()

    class Meta:
        model = VacancyResponse
        fields = (
            "id",
            "vacancy",
            "applicant",
            "text_answer",
            "covering_letter",
            "approved_by_mentor",
            "approved_by_applicant",
        )


class VacancyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyResponse
        fields = (
            "id",
            "vacancy",
            "text_answer",
            "covering_letter",
            "approved_by_mentor",
            "approved_by_applicant",
        )
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        if user.role != User.Role.TRAINEE:
            raise PermissionDenied()
        return VacancyResponse.objects.create(
            **validated_data, applicant=user.trainee_profile
        )

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user.role == User.Role.TRAINEE:
            validated_data = {
                "approved_by_applicant": validated_data.get("approved_by_applicant")
            }
        elif user.role == User.Role.MENTOR:
            validated_data = {
                "approved_by_mentor": validated_data.get("approved_by_mentor")
            }
        return super().update(instance, validated_data)


class ReadWorkPlaceSerializer(serializers.ModelSerializer):
    trainee = UserSerializer()
    mentor = UserSerializer()
    department = DepartmentSerializer()
    vacancy = VacancySerializer()

    class Meta:
        model = WorkPlace
        fields = (
            "id",
            "name",
            "mentor",
            "trainee",
            "vacancy",
            "is_active",
            "created_at",
            "updated_at",
            "department",
        )


class WorkPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPlace
        fields = [
            "id",
            "name",
            "mentor",
            "trainee",
            "is_active",
            "department",
            "vacancy",
        ]


class CountSerializer(serializers.Serializer):
    count = serializers.IntegerField()


class ReadFeedbackSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()
    to_user = UserSerializer()

    class Meta:
        model = FeedBack
        fields = [
            "id",
            "from_user",
            "to_user",
            "date",
            "rating",
            "text",
        ]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = [
            "id",
            "to_user",
            "rating",
            "text",
        ]

    def create(self, validated_data):
        validated_data["date"] = timezone.now()
        validated_data["from_user"] = self.context["request"].user
        return FeedBack.objects.create(**validated_data)


class ReadEventSerializer(serializers.ModelSerializer):
    workplace = WorkPlaceSerializer()

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "datetime",
            "workplace",
        ]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "datetime",
            "workplace",
        ]
