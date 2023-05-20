from accounts.serializers import DepartmentSerializer, UserSerializer
from django.db import transaction
from django.utils import timezone
from internship.models import Direction, InternshipApplication, Qualification, Vacancy
from rest_framework import serializers


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
    approved_by = UserSerializer()
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
            "is_published",
            "approved_by",
            "mentor",
            "published_at",
            "created_at",
        ]


class VacancySerializer(serializers.ModelSerializer):
    required_qualifications = serializers.ListSerializer(
        child=serializers.IntegerField()
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
            "is_published",
            "approved_by",
            "mentor",
            "published_at",
            "created_at",
        ]
        read_only_fields = (
            "id",
            "department",
            "owner",
            "approved_by",
            "published_at",
            "created_at",
        )

    @transaction.atomic
    def create(self, validated_data):
        qualification_ids = validated_data.pop("required_qualifications")
        validated_data.pop("is_published")  # publishing only after curator review
        validated_data["owner"] = self.context["request"].user
        validated_data["department"] = self.context["request"].user.department
        vacancy = Vacancy.objects.create(**validated_data)

        qualifications = Qualification.objects.filter(id__in=qualification_ids)
        for qualification in qualifications:
            vacancy.required_qualifications.add(qualification)
        vacancy.save()
        return vacancy

    @transaction.atomic
    def update(self, instance: Vacancy, validated_data):
        if validated_data["is_published"] and not instance.is_published:
            validated_data["published_at"] = timezone.now()
            validated_data["approved_by"] = self.context["request"].user
        return super().update(instance, validated_data)
