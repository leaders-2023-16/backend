from attendance.models import Report
from django.contrib import admin


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "get_first_name",
        "get_last_name",
        "date",
        "status",
    )
    search_fields = ("applicant__first_name", "applicant__last_name")

    @admin.display(description="First name")
    def get_first_name(self, obj):
        return obj.applicant.first_name

    @admin.display(description="Last name")
    def get_last_name(self, obj):
        return obj.applicant.last_name
