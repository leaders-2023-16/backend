from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    class StatusType(models.TextChoices):
        ATTENDED = "ATTENDED", _("Attended")
        SICK_DAY = "SICK_DAY", _("Sick day")
        VOCATION = "VOCATION", _("Vocation")

    date = models.DateField()
    applicant = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="reports"
    )
    is_approved = models.BooleanField()
    approved_by = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="approved_reports"
    )
    status = models.CharField(
        max_length=10,
        choices=StatusType.choices,
    )
