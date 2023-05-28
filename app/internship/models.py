from accounts.models import Department, Education, TraineeProfile, User
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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
        NOT_QUALIFY = "not_qualify", _("Did not qualify for the application")

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

    def __str__(self):
        return self.name


class Qualification(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Vacancy(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        REJECTED = "rejected", _("Rejected")
        PUBLISHED = "published", _("Published")
        CLOSED = "closed", _("Closed")

    class ScheduleType(models.TextChoices):
        FULL_TIME = "full-time", _("Full-time")
        PART_TIME = "part-time", _("Part-time")

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
    mentor = models.ForeignKey(
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

    schedule = models.CharField(
        max_length=50,
        choices=ScheduleType.choices,
        default=ScheduleType.FULL_TIME,
        verbose_name="Status",
    )

    class Meta:
        verbose_name_plural = "Vacancies"


class VacancyResponse(models.Model):
    vacancy = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name="responses"
    )
    applicant = models.ForeignKey(TraineeProfile, on_delete=models.CASCADE)
    text_answer = models.TextField()
    covering_letter = models.TextField(
        verbose_name="Covering letter", blank=True, null=True
    )
    approved_by_mentor = models.BooleanField(
        "Approved by mentor", blank=True, null=True
    )
    approved_by_applicant = models.BooleanField(
        "Approved by applicant", blank=True, null=True
    )

    class Meta:
        db_table = "internship_vacancy_response"
        verbose_name_plural = "Vacancy responses"
        unique_together = [["vacancy", "applicant"]]


class WorkPlace(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    vacancy = models.OneToOneField(
        Vacancy,
        related_name="work_place",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    trainee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="work_on",
        verbose_name=_("Trainee"),
    )
    mentor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mentor_on",
        verbose_name=_("Mentor"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name="Department"
    )

    class Meta:
        db_table = "attendance_work_place"
        verbose_name_plural = "Work places"


class FeedBack(models.Model):
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="feedbacks_sent"
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="feedbacks_received"
    )
    date = models.DateField()
    rating = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    text = models.TextField(max_length=255)

    def __str__(self):
        return f"FeedBack from {self.from_user} to {self.to_user} at {self.date}"
