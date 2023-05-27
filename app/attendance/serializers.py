from attendance.models import Report
from rest_framework import serializers


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ("id", "applicant", "approved_by")

    def create(self, validated_data):
        validated_data["applicant"] = self.context["request"].user
        validated_data["work_place"] = self.context["request"].user.current_work_place
        return Report.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["approved_by"] = self.context["request"].user
        return super().update(instance, validated_data)
