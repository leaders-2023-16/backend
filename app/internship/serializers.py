from accounts.models import User
from accounts.serializers import (
    DepartmentSerializer,
    ReadTraineeProfileSerializer,
    UserSerializer,
)
from django.db import transaction
from django.utils import timezone
from internship.models import (
    Direction,
    InternshipApplication,
    Qualification,
    TestTask,
    Vacancy,
    VacancyResponse,
)
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


class ReadInternshipApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer()
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
        ]


class VacancySerializer(serializers.ModelSerializer):
    required_qualifications = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Qualification.objects.all()
    )
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
        vacancy.required_qualifications.set(qualifications)
        vacancy.save()
        return vacancy

    @transaction.atomic
    def update(self, instance: Vacancy, validated_data):
        test_task_data = validated_data.pop("test_task")
        if validated_data["status"] != instance.status:
            if self.context["request"].user.role != User.Role.CURATOR:
                raise PermissionDenied()
            if validated_data["status"] == Vacancy.Status.PUBLISHED:
                validated_data["published_at"] = timezone.now()
                validated_data["reviewed_by"] = self.context["request"].user

        serializer = TestTaskSerializer(
            data=test_task_data, context={"department": instance.department}
        )
        serializer.is_valid(raise_exception=True)
        test_task = serializer.save()
        instance.test_task = test_task
        qualifications = validated_data.pop("required_qualifications")
        instance.required_qualifications.set(qualifications)
        return super().update(instance, validated_data)


class ReadVacancyResponseSerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer()
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
            "vacancy",
            "text_answer",
            "covering_letter",
            "approved_by_mentor",
            "approved_by_applicant",
        )

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
