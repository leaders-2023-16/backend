from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import F
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    name = models.CharField("Name", max_length=200)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    @transaction.atomic
    def _create_user(self, username, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.pop("email", None)
        user = self.model(username=username, email=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if user.role in (User.Role.TRAINEE, User.Role.CANDIDATE):
            user.trainee_profile = TraineeProfile.objects.create(user=user)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("role", User.Role.CANDIDATE)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = "F", _("Candidate")  # F - like first-timer
        TRAINEE = "T", _("Trainee")
        MENTOR = "M", _("Mentor")
        PERSONNEL = "P", _("Personnel")
        CURATOR = "C", _("Curator")
        ADMIN = "A", _("Admin")

    role = models.CharField(
        max_length=1,
        choices=Role.choices,
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, blank=True, null=True
    )

    objects = UserManager()

    @cached_property
    def current_work_place(self):
        if self.role == User.Role.TRAINEE:
            return self.work_on.filter(is_active=True).first()
        elif self.role == User.Role.MENTOR:
            return self.mentor_on.filter(is_active=True).first()


class Country(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="Name")

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class TraineeProfileManager(models.Manager):
    def get_rating(self):
        return (
            self.filter(test_status=TraineeProfile.QualifyingStatus.PASSED)
            .annotate(total_score=F("cv_score") + F("test_score"))
            .order_by("-total_score")
        )


class TraineeProfile(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", _("MALE")
        FEMALE = "F", _("FEMALE")

    class QualifyingStatus(models.TextChoices):
        PASSED = "PASSED", _("Passed")
        IN_PROGRESS = "IN_PROGRESS", _("In progress of qualification")
        FAILED = "FAILED", _("Did not pass qualification")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="trainee_profile",
        primary_key=True,
        verbose_name="User",
    )
    citizenship = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Citizenship",
    )
    bio = models.TextField(default="", verbose_name="Bio")
    phone_number = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Phone Number"
    )
    sex = models.CharField(
        "Sex", max_length=1, choices=Sex.choices, null=True, blank=True
    )
    birth_date = models.DateField("Birth date", blank=True, null=True)

    test_status = models.CharField(
        max_length=11,
        choices=QualifyingStatus.choices,
        default=QualifyingStatus.IN_PROGRESS,
    )

    cv_score = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)], default=0
    )
    test_score = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)], default=0
    )
    career_school_username = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Career School Login"
    )
    career_school_password = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Career School Password"
    )
    progress_career_school = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )
    testing_platform_username = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Testing platform Login"
    )
    testing_platform_password = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Testing platform Password"
    )

    objects = TraineeProfileManager()

    class Meta:
        db_table = "accounts_trainee_profile"
        verbose_name_plural = "Trainee Profiles"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Link(models.Model):
    profile = models.ForeignKey(
        TraineeProfile,
        on_delete=models.CASCADE,
        related_name="links",
        verbose_name="Profile",
    )
    url = models.URLField(verbose_name="URL")


class Education(models.Model):
    class Type(models.TextChoices):
        SCHOOL = "school", _("School")
        UNIVERSITY = "university", _("University")
        COLLEGE = "college", _("College")

    class DegreeType(models.TextChoices):
        BACHELOR = "Bachelor", _("Bachelor")
        MASTER = "Master", _("Master")
        DOCTORATE = "Doctorate", _("Doctorate")

    profile = models.ForeignKey(
        TraineeProfile,
        on_delete=models.CASCADE,
        related_name="educations",
        verbose_name="Profile",
    )
    name = models.CharField(max_length=100, verbose_name="Name")
    type = models.CharField(max_length=20, choices=Type.choices, verbose_name="Type")
    start_year = models.IntegerField(verbose_name="Start year")
    end_year = models.IntegerField(blank=True, null=True, verbose_name="End year")
    specialization = models.CharField(max_length=100, verbose_name="Specialization")
    degree = models.CharField(
        max_length=100, choices=DegreeType.choices, verbose_name="Degree", null=True
    )
    description = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="Description"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Educations"


class WorkExperience(models.Model):
    profile = models.ForeignKey(
        TraineeProfile,
        on_delete=models.CASCADE,
        related_name="work_experiences",
        verbose_name="Profile",
    )
    employer = models.CharField(max_length=100, verbose_name="Employer")
    position = models.CharField(max_length=100, verbose_name="Position")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(blank=True, null=True, verbose_name="End Date")
    description = models.TextField(verbose_name="Description")

    def __str__(self):
        return self.employer

    class Meta:
        db_table = "accounts_work_experience"
        verbose_name_plural = "Work Experiences"
