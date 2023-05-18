from accounts.models import Country, Education, Link, TraineeProfile, WorkExperience
from django.db import transaction
from rest_framework import serializers


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
