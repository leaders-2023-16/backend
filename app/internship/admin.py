from django.contrib import admin
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


@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "get_first_name",
        "get_last_name",
        "get_citizenship",
    )
    search_fields = ("applicant__first_name", "applicant__last_name")

    @admin.display(description="First name")
    def get_first_name(self, obj):
        return obj.applicant.first_name

    @admin.display(description="Last name")
    def get_last_name(self, obj):
        return obj.applicant.last_name

    @admin.display(description="Citizenship")
    def get_citizenship(self, obj):
        return obj.applicant.trainee_profile.citizenship


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "type",
        "description",
        "department",
    )


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "direction",
        "department",
        "owner",
        "reviewed_by",
        "mentor",
    )
    search_fields = (
        "name",
        "owner",
    )


@admin.register(VacancyResponse)
class VacancyResponseAdmin(admin.ModelAdmin):
    list_display = (
        "get_first_name",
        "get_last_name",
    )
    search_fields = ("applicant__user__first_name", "applicant__user__last_name")

    @admin.display(description="First name")
    def get_first_name(self, obj):
        return obj.applicant.user.first_name

    @admin.display(description="Last name")
    def get_last_name(self, obj):
        return obj.applicant.user.last_name


@admin.register(WorkPlace)
class WorkPlaceAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user")
    search_fields = ("from_user", "to_user")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "datetime",
    )
    search_fields = ("name",)
