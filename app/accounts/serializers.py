from accounts.models import (
    Country,
    Department,
    Education,
    Link,
    TraineeProfile,
    User,
    WorkExperience,
)
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["url"]


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            "name",
            "type",
            "start_year",
            "end_year",
            "specialization",
            "degree",
            "description",
        ]


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ["employer", "position", "start_date", "end_date", "description"]


class ReadTraineeProfileSerializer(serializers.ModelSerializer):
    links = LinkSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    work_experiences = WorkExperienceSerializer(many=True, required=False)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = TraineeProfile
        fields = [
            "user_id",
            "citizenship",
            "bio",
            "phone_number",
            "links",
            "educations",
            "work_experiences",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "sex",
            "status",
            "cv_score",
            "test_score",
            "career_school_username",
            "career_school_password",
            "progress_career_school",
            "testing_platform_username",
            "testing_platform_password",
        ]
        depth = 1


class TraineeProfileSerializer(serializers.ModelSerializer):
    links = LinkSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    work_experiences = WorkExperienceSerializer(many=True, required=False)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = TraineeProfile
        fields = [
            "user_id",
            "citizenship",
            "bio",
            "phone_number",
            "links",
            "educations",
            "work_experiences",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "sex",
            "status",
            "cv_score",
            "test_score",
            "career_school_username",
            "career_school_password",
            "progress_career_school",
            "testing_platform_username",
            "testing_platform_password",
        ]
        read_only_fields = ("status",)

    @transaction.atomic
    def create(self, validated_data):
        links_data = validated_data.pop("links", [])
        educations_data = validated_data.pop("educations", [])
        work_experiences_data = validated_data.pop("work_experiences", [])

        profile = TraineeProfile.objects.create(**validated_data)

        links = [Link(profile=profile, **link_data) for link_data in links_data]
        Link.objects.bulk_create(links)

        educations = [
            Education(profile=profile, **education_data)
            for education_data in educations_data
        ]
        Education.objects.bulk_create(educations)

        work_experiences = [
            WorkExperience(profile=profile, **work_experience_data)
            for work_experience_data in work_experiences_data
        ]
        WorkExperience.objects.bulk_create(work_experiences)

        return profile

    @transaction.atomic
    def update(self, instance, validated_data):
        if self.context["request"].user.role in [
            User.Role.CANDIDATE,
            User.Role.TRAINEE,
        ]:
            ignore_fields = [
                "cv_score",
                "test_score",
                "career_school_username",
                "career_school_password",
                "progress_career_school",
                "testing_platform_username",
                "testing_platform_password",
            ]
            for field in ignore_fields:
                validated_data.pop(field, None)
        links_data = validated_data.pop("links", [])
        educations_data = validated_data.pop("educations", [])
        work_experiences_data = validated_data.pop("work_experiences", [])

        instance.links.all().delete()
        links = [Link(profile=instance, **link_data) for link_data in links_data]
        Link.objects.bulk_create(links)

        instance.educations.all().delete()
        educations = [
            Education(profile=instance, **education_data)
            for education_data in educations_data
        ]
        Education.objects.bulk_create(educations)

        instance.work_experiences.all().delete()
        work_experiences = [
            WorkExperience(profile=instance, **work_experience_data)
            for work_experience_data in work_experiences_data
        ]
        WorkExperience.objects.bulk_create(work_experiences)

        return super().update(instance, validated_data)


class RatingTraineeProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    total_score = serializers.IntegerField()

    class Meta:
        model = TraineeProfile
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "sex",
            "cv_score",
            "test_score",
            "total_score",
        ]


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


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class TokenObtainPairWithUserIdSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(required=False)

    class Meta:
        model = User
        fields = ("id", "email", "role", "first_name", "last_name", "department")


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer(many=False, required=False)

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()
