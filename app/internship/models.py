from accounts.models import Education
from django.conf import settings
from django.db import models
from django.db.models import F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class InternshipApplication(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        REJECTED = "rejected", _("Rejected")
        NEXT_STAGE = "next_stage", _("Approved for next stage")
        APPROVED = "approved", _("Approved")

    applicant = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="applications",
        primary_key=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=255, choices=StatusChoices.choices, blank=True, null=True
    )
    status_changed_at = models.DateTimeField(blank=True, null=True)
    status_changed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_applications",
    )

    def is_recommended(self):
        if (
            self.applicant.trainee_profile.citizenship_id
            != settings.PREFERABLE_CITIZENSHIP_ID
        ):
            return False

        required_university_years = settings.REQUIRED_UNIVERSITY_YEARS
        university_criteria = self.applicant.trainee_profile.educations.filter(
            start_year__lte=Coalesce(F("end_year"), timezone.now().date().year)
            - required_university_years,
            type=Education.Type.UNIVERSITY,
            degree=Education.DegreeType.BACHELOR,
        ).exists()
        if not university_criteria:
            return False
        # TODO: check relevancy of job experience
        return True
