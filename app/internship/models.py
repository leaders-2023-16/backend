from accounts.models import Department, Education
from django.conf import settings
from django.db import models
from django.db.models import F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class InternshipApplication(models.Model):
    class Status(models.TextChoices):
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
    is_recommended = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=255, choices=Status.choices, default=Status.PENDING
    )
    status_changed_at = models.DateTimeField(blank=True, null=True)
    status_changed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_applications",
    )
    direction = models.ForeignKey(
        "internship.Direction",
        on_delete=models.CASCADE,
        null=True,
    )

    def set_recommendation(self):
        self.is_recommended = self._calculate_recommendation()
        self.save()
        return self

    def _calculate_recommendation(self):
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


class TestTask(models.Model):
    class Type(models.TextChoices):
        TEXT = "text", _("Text")

    title = models.CharField(max_length=200, default="Тестовое задание")
    type = models.CharField(max_length=50, choices=Type.choices, default=Type.TEXT)
    description = models.TextField("Description")
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name="Owned by department",
        related_name="test_tasks",
    )

    class Meta:
        db_table = "internship_test_task"
        verbose_name_plural = "Test tasks"


class Direction(models.Model):
    name = models.CharField(max_length=255)


class Qualification(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Vacancy(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        REJECTED = "rejected", _("Rejected")
        PUBLISHED = "published", _("Published")

    required_qualifications = models.ManyToManyField(
        Qualification, verbose_name="Required Qualifications"
    )
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(verbose_name="Description")
    direction = models.ForeignKey(
        Direction, on_delete=models.CASCADE, verbose_name="Direction"
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name="Department"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Owner",
        related_name="owned_vacancies",
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Reviewed by",
        related_name="reviewed_vacancies",
    )
    mentor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Mentor",
        related_name="mentor_of",
    )
    test_task = models.ForeignKey(
        TestTask,
        verbose_name="Test task",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    published_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Published At"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name_plural = "Vacancies"
