from accounts.models import (
    Country,
    Department,
    Education,
    Link,
    TraineeProfile,
    User,
    WorkExperience,
)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Roles"), {"fields": ("role",)}),
    )
    list_display = ("first_name", "last_name", "role", "is_staff")
    search_fields = ("first_name", "last_name", "role")


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
        "start_year",
        "end_year",
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


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
