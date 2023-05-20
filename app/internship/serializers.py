from accounts.serializers import UserSerializer
from django.utils import timezone
from internship.models import InternshipApplication
from rest_framework import serializers


class ReadInternshipApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer()
    status_changed_by = UserSerializer()

    class Meta:
        model = InternshipApplication
        fields = "__all__"
        read_only_fields = ("status_changed_at", "status_changed_by", "applicant")


class InternshipApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipApplication
        fields = "__all__"
        read_only_fields = ("status_changed_at", "status_changed_by", "applicant")

    def create(self, validated_data: dict):
        validated_data["applicant"] = self.context["request"].user
        if "status" in validated_data:
            del validated_data["status"]
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "status" in validated_data and instance.status != validated_data["status"]:
            instance.status_changed_at = timezone.now()
            instance.status_changed_by = self.context["request"].user
        return super().update(instance, validated_data)
