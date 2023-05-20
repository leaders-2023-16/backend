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
        ]

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
        links_data = validated_data.pop("links", [])
        educations_data = validated_data.pop("educations", [])
        work_experiences_data = validated_data.pop("work_experiences", [])

        instance.citizenship = validated_data.get("citizenship", instance.citizenship)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.save()

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

        return instance


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


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user_id = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class TokenObtainPairWithUserIdSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user_id"] = self.user.id
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
