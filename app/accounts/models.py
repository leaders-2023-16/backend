from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    @transaction.atomic
    def _create_user(self, username, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if user.role == User.Role.TRAINEE:
            user.trainee_profile = TraineeProfile.objects.create(user=user)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("role", User.Role.TRAINEE)
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

    objects = UserManager()


class Country(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="Name")

    class Meta:
        verbose_name_plural = "Countries"


class TraineeProfile(models.Model):
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

    class Meta:
        db_table = "accounts_trainee_profile"
        verbose_name_plural = "Trainee Profiles"


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
        max_length=100, choices=DegreeType.choices, verbose_name="Degree"
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
