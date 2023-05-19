from accounts.models import (
    Country,
    Education,
    Link,
    TraineeProfile,
    User,
    WorkExperience,
)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class LinkInline(admin.TabularInline):
    model = Link


class EducationInline(admin.TabularInline):
    model = Education


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience


@admin.register(TraineeProfile)
class TraineeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "citizenship",
    )
    search_fields = (
        "user__username",
        "user__email",
    )
    inlines = [LinkInline, EducationInline, WorkExperienceInline]


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "url",
    )
    search_fields = (
        "profile__user__username",
        "url",
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "name",
        "type",
        "start_date",
        "end_date",
    )
    search_fields = (
        "profile__user__username",
        "name",
    )


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "employer",
        "position",
        "start_date",
        "end_date",
    )
    search_fields = (
        "profile__user__username",
        "employer",
        "position",
    )
