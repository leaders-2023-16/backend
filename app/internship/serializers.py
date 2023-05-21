from accounts.models import User
from accounts.serializers import DepartmentSerializer, UserSerializer
from django.db import transaction
from django.utils import timezone
from internship.models import Direction, InternshipApplication, Qualification, Vacancy
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


class ReadVacancySerializer(serializers.ModelSerializer):
    required_qualifications = QualificationSerializer(many=True)
    direction = DirectionSerializer()
    department = DepartmentSerializer()
    owner = UserSerializer()
    reviewed_by = UserSerializer(required=False)
    mentor = UserSerializer()

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
        ]


class VacancySerializer(serializers.ModelSerializer):
    required_qualifications = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Qualification.objects.all()
    )

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
        validated_data.pop("status")  # publishing only after curator review
        validated_data["owner"] = self.context["request"].user
        validated_data["department"] = self.context["request"].user.department
        vacancy = Vacancy.objects.create(**validated_data)
        vacancy.required_qualifications.set(qualifications)
        vacancy.save()
        return vacancy

    @transaction.atomic
    def update(self, instance: Vacancy, validated_data):
        if validated_data["status"] != instance.status:
            if self.context["request"].user.role != User.Role.CURATOR:
                raise PermissionDenied()
            if validated_data["status"] == Vacancy.Status.PUBLISHED:
                validated_data["published_at"] = timezone.now()
                validated_data["reviewed_by"] = self.context["request"].user

        qualifications = validated_data.pop("required_qualifications")
        instance.required_qualifications.set(qualifications)
        return super().update(instance, validated_data)
