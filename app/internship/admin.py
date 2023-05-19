from django.contrib import admin
from internship.models import InternshipApplication


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
